"""Code execution and testing API endpoints."""
import subprocess
import tempfile
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.modelsx.code_executor import (
    CodeExecution, TestCaseResult, ExecutionEnvironment,
    ExecutionLanguage, ExecutionStatus, TestCaseStatus, ExecutionMetrics
)
from app.schemas.notifications_executor import (
    CodeExecutionRequest, CodeExecutionResponse, ExecutionStatusResponse,
    ExecutionHistoryResponse, ExecutionEnvironmentResponse, ExecutionMetricsResponse,
    TestCaseResultResponse
)

router = APIRouter(prefix="/execute", tags=["code-execution"])


# ============ EXECUTION ENGINE ============

class CodeExecutor:
    """Sandboxed code execution engine."""
    
    @staticmethod
    def get_execution_command(language: str) -> dict:
        """Get execution command for language."""
        commands = {
            "python": {
                "compile": None,
                "run": "python3 {file}",
                "timeout": 5,
                "memory": 256,
            },
            "javascript": {
                "compile": None,
                "run": "node {file}",
                "timeout": 5,
                "memory": 256,
            },
            "java": {
                "compile": "javac {file}.java",
                "run": "java {file}",
                "timeout": 10,
                "memory": 512,
            },
            "cpp": {
                "compile": "g++ -o {file} {file}.cpp",
                "run": "./{file}",
                "timeout": 5,
                "memory": 256,
            },
            "c": {
                "compile": "gcc -o {file} {file}.c",
                "run": "./{file}",
                "timeout": 5,
                "memory": 256,
            },
        }
        return commands.get(language, commands["python"])
    
    @staticmethod
    def execute_code(code: str, language: str, test_cases: list, 
                     time_limit: int = 5, memory_limit: int = 256) -> dict:
        """Execute code against test cases."""
        results = {
            "status": ExecutionStatus.RUNNING,
            "test_results": [],
            "compilation_log": None,
            "error_message": None,
            "stdout": None,
            "stderr": None,
            "execution_time_ms": 0,
            "memory_used_mb": 0,
            "passed": 0,
            "failed": 0,
        }
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            ext = CodeExecutor._get_file_extension(language)
            code_file = os.path.join(tmpdir, f"solution{ext}")
            
            try:
                with open(code_file, "w") as f:
                    f.write(code)
                
                # Get execution command
                cmd_info = CodeExecutor.get_execution_command(language)
                
                # Compile if needed
                if cmd_info["compile"]:
                    compile_cmd = cmd_info["compile"].format(file=code_file.replace(ext, ""))
                    try:
                        compile_result = subprocess.run(
                            compile_cmd,
                            shell=True,
                            cwd=tmpdir,
                            capture_output=True,
                            timeout=time_limit,
                            text=True
                        )
                        if compile_result.returncode != 0:
                            results["status"] = ExecutionStatus.COMPILATION_ERROR
                            results["compilation_log"] = compile_result.stderr
                            results["error_message"] = "Compilation failed"
                            return results
                    except subprocess.TimeoutExpired:
                        results["status"] = ExecutionStatus.TIMEOUT
                        results["error_message"] = "Compilation timeout"
                        return results
                
                # Run test cases
                for idx, test_case in enumerate(test_cases):
                    test_result = CodeExecutor._run_test_case(
                        code_file, language, cmd_info, test_case, time_limit, tmpdir
                    )
                    results["test_results"].append(test_result)
                    
                    if test_result["passed"]:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                
                # Set final status
                if results["failed"] == 0:
                    results["status"] = ExecutionStatus.COMPLETED
                else:
                    results["status"] = ExecutionStatus.COMPLETED
                
            except Exception as e:
                results["status"] = ExecutionStatus.ERROR
                results["error_message"] = str(e)
        
        return results
    
    @staticmethod
    def _get_file_extension(language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
        }
        return extensions.get(language, ".txt")
    
    @staticmethod
    def _run_test_case(code_file: str, language: str, cmd_info: dict, 
                       test_case: dict, time_limit: int, tmpdir: str) -> dict:
        """Run single test case."""
        result = {
            "status": TestCaseStatus.FAILED,
            "passed": False,
            "actual_output": None,
            "execution_time_ms": None,
            "error_message": None,
        }
        
        try:
            # Prepare input
            input_data = test_case.get("input_data", "")
            expected_output = test_case.get("expected_output", "").strip()
            
            # Build run command
            run_cmd = cmd_info["run"].format(file=code_file.replace(cmd_info["run"].split(" {")[0], ""))
            
            # Execute with timeout
            import time
            start_time = time.time()
            
            proc = subprocess.run(
                run_cmd,
                shell=True,
                input=input_data,
                cwd=tmpdir,
                capture_output=True,
                timeout=time_limit,
                text=True
            )
            
            exec_time = (time.time() - start_time) * 1000
            result["execution_time_ms"] = int(exec_time)
            
            # Check output
            actual_output = proc.stdout.strip()
            result["actual_output"] = actual_output
            
            if proc.returncode != 0 and proc.stderr:
                result["status"] = TestCaseStatus.ERROR
                result["error_message"] = proc.stderr
                return result
            
            # Compare output
            if actual_output == expected_output:
                result["status"] = TestCaseStatus.PASSED
                result["passed"] = True
            else:
                result["status"] = TestCaseStatus.FAILED
                result["passed"] = False
            
        except subprocess.TimeoutExpired:
            result["status"] = TestCaseStatus.TIMEOUT
            result["error_message"] = "Execution timeout"
        except Exception as e:
            result["status"] = TestCaseStatus.ERROR
            result["error_message"] = str(e)
        
        return result


# ============ EXECUTION ENDPOINTS ============

@router.post("/run", response_model=CodeExecutionResponse)
def run_code(
    execution_request: CodeExecutionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute code and run test cases."""
    
    # Create execution record
    execution = CodeExecution(
        user_id=current_user.id,
        challenge_id=execution_request.challenge_id,
        contest_id=execution_request.contest_id,
        code=execution_request.code,
        language=execution_request.language,
        time_limit_seconds=execution_request.time_limit_seconds,
        memory_limit_mb=execution_request.memory_limit_mb,
        status=ExecutionStatus.PENDING,
        created_at=datetime.utcnow(),
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Execute code
    executor = CodeExecutor()
    
    # Convert test cases to dict format
    test_cases_data = [
        {
            "input_data": tc.input_data,
            "expected_output": tc.expected_output,
            "is_sample": tc.is_sample
        }
        for tc in execution_request.test_cases
    ]
    
    try:
        execution.started_at = datetime.utcnow()
        db.commit()
        
        results = executor.execute_code(
            execution_request.code,
            execution_request.language,
            test_cases_data,
            execution_request.time_limit_seconds,
            execution_request.memory_limit_mb
        )
        
        # Update execution record
        execution.status = results["status"]
        execution.test_cases_total = len(test_cases_data)
        execution.test_cases_passed = results["passed"]
        execution.test_cases_failed = results["failed"]
        execution.compilation_log = results["compilation_log"]
        execution.error_message = results["error_message"]
        execution.stdout = results["stdout"]
        execution.stderr = results["stderr"]
        execution.execution_time_ms = results["execution_time_ms"]
        execution.memory_used_mb = results["memory_used_mb"]
        execution.completed_at = datetime.utcnow()
        
        # Calculate points
        if results["failed"] == 0:
            execution.points_earned = execution_request.time_limit_seconds * 10
        else:
            execution.points_earned = max(0, (results["passed"] / len(test_cases_data)) * 100)
        
        # Save test results
        for idx, test_result in enumerate(results["test_results"]):
            test_case_obj = TestCaseResult(
                execution_id=execution.id,
                test_case_number=idx + 1,
                is_sample=test_cases_data[idx].get("is_sample", False),
                input_data=test_cases_data[idx]["input_data"],
                expected_output=test_cases_data[idx]["expected_output"],
                actual_output=test_result.get("actual_output"),
                status=test_result["status"],
                passed=test_result.get("passed", False),
                execution_time_ms=test_result.get("execution_time_ms"),
                error_message=test_result.get("error_message"),
            )
            db.add(test_case_obj)
        
        db.commit()
        db.refresh(execution)
        
    except Exception as e:
        execution.status = ExecutionStatus.ERROR
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(execution)
    
    # Load test results
    test_results = db.query(TestCaseResult).filter(
        TestCaseResult.execution_id == execution.id
    ).all()
    execution.test_results = test_results
    
    return execution


@router.get("/{execution_id}", response_model=CodeExecutionResponse)
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get execution details."""
    execution = db.query(CodeExecution).filter(
        CodeExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check permission
    if execution.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Load test results
    test_results = db.query(TestCaseResult).filter(
        TestCaseResult.execution_id == execution.id
    ).all()
    execution.test_results = test_results
    
    return execution


@router.get("/history", response_model=List[ExecutionHistoryResponse])
def get_execution_history(
    challenge_id: Optional[int] = None,
    language: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's execution history."""
    query = db.query(CodeExecution).filter(
        CodeExecution.user_id == current_user.id
    )
    
    if challenge_id:
        query = query.filter(CodeExecution.challenge_id == challenge_id)
    if language:
        query = query.filter(CodeExecution.language == language)
    
    executions = query.order_by(desc(CodeExecution.created_at)).offset(skip).limit(limit).all()
    
    return executions


@router.get("/status/{execution_id}", response_model=ExecutionStatusResponse)
def get_execution_status(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get execution status (for polling)."""
    execution = db.query(CodeExecution).filter(
        CodeExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Calculate progress
    progress = 0
    if execution.status == ExecutionStatus.PENDING:
        progress = 10
    elif execution.status == ExecutionStatus.RUNNING:
        progress = 50
    elif execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.TIMEOUT, ExecutionStatus.ERROR]:
        progress = 100
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "progress": progress,
        "test_cases_passed": execution.test_cases_passed,
        "test_cases_total": execution.test_cases_total,
        "completed": execution.status == ExecutionStatus.COMPLETED,
    }


# ============ ENVIRONMENT ENDPOINTS ============

@router.get("/environments", response_model=List[ExecutionEnvironmentResponse])
def get_execution_environments(
    db: Session = Depends(get_db),
):
    """Get available execution environments."""
    environments = db.query(ExecutionEnvironment).filter(
        ExecutionEnvironment.is_active == True
    ).all()
    return environments


@router.get("/environments/{language}", response_model=ExecutionEnvironmentResponse)
def get_environment(
    language: str,
    db: Session = Depends(get_db),
):
    """Get execution environment for language."""
    env = db.query(ExecutionEnvironment).filter(
        ExecutionEnvironment.language == language
    ).first()
    
    if not env:
        raise HTTPException(status_code=404, detail=f"Environment not found for {language}")
    
    return env


# ============ METRICS ENDPOINTS ============

@router.get("/metrics", response_model=List[ExecutionMetricsResponse])
def get_execution_metrics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Get execution metrics for last N days."""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    metrics = db.query(ExecutionMetrics).filter(
        ExecutionMetrics.date >= start_date
    ).order_by(ExecutionMetrics.date).all()
    
    return metrics


@router.get("/stats")
def get_execution_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's execution statistics."""
    executions = db.query(CodeExecution).filter(
        CodeExecution.user_id == current_user.id
    ).all()
    
    total = len(executions)
    passed = sum(1 for e in executions if e.test_cases_passed == e.test_cases_total)
    
    # Language breakdown
    lang_breakdown = {}
    for exe in executions:
        lang = exe.language
        lang_breakdown[lang] = lang_breakdown.get(lang, 0) + 1
    
    # Average execution time
    avg_time = 0
    if total > 0:
        avg_time = sum(e.execution_time_ms or 0 for e in executions) / total
    
    return {
        "total_executions": total,
        "successful_executions": passed,
        "success_rate": (passed / total * 100) if total > 0 else 0,
        "language_breakdown": lang_breakdown,
        "avg_execution_time_ms": avg_time,
    }
