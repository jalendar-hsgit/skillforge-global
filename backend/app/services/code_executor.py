"""
Real-time Code Execution Service
Supports multiple languages with sandboxing and security
"""
import subprocess
import tempfile
import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Docker is optional - only needed for production sandboxing
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None


class CodeExecutor:
    """
    Execute code in multiple languages with proper sandboxing
    """
    
    LANGUAGE_CONFIGS = {
        'python': {
            'extension': '.py',
            'command': 'python',
            'docker_image': 'python:3.11-slim',
            'timeout': 30
        },
        'javascript': {
            'extension': '.js',
            'command': 'node',
            'docker_image': 'node:18-slim',
            'timeout': 30
        },
        'typescript': {
            'extension': '.ts',
            'command': 'ts-node',
            'docker_image': 'node:18-slim',
            'timeout': 30
        },
        'java': {
            'extension': '.java',
            'command': 'java',
            'docker_image': 'openjdk:17-slim',
            'timeout': 45
        },
        'cpp': {
            'extension': '.cpp',
            'command': 'g++',
            'docker_image': 'gcc:latest',
            'timeout': 45
        },
        'go': {
            'extension': '.go',
            'command': 'go run',
            'docker_image': 'golang:1.21-alpine',
            'timeout': 30
        },
        'rust': {
            'extension': '.rs',
            'command': 'rustc',
            'docker_image': 'rust:latest',
            'timeout': 45
        },
        'sql': {
            'extension': '.sql',
            'command': 'sqlite3',
            'docker_image': 'alpine:latest',
            'timeout': 15
        }
    }
    
    def __init__(self, use_docker: bool = False):
        """
        Initialize code executor
        
        Args:
            use_docker: Whether to use Docker for sandboxing (recommended for production)
        """
        self.use_docker = use_docker and DOCKER_AVAILABLE
        self.docker_client = None
        
        if use_docker and not DOCKER_AVAILABLE:
            print("Warning: Docker requested but python-docker is not installed. Using local execution.")
            self.use_docker = False
        
        if self.use_docker:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                print(f"Docker not available: {e}")
                self.use_docker = False
    
    def execute_code(
        self,
        code: str,
        language: str,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute code and return results
        
        Args:
            code: Source code to execute
            language: Programming language
            test_cases: Optional list of test cases with input/expected output
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        if language not in self.LANGUAGE_CONFIGS:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'output': '',
                'execution_time': 0
            }
        
        config = self.LANGUAGE_CONFIGS[language]
        timeout = timeout or config['timeout']
        
        try:
            if self.use_docker:
                return self._execute_in_docker(code, language, test_cases, timeout)
            else:
                return self._execute_locally(code, language, test_cases, timeout)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }
    
    def _execute_locally(
        self,
        code: str,
        language: str,
        test_cases: Optional[List[Dict[str, Any]]],
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute code locally (less secure, for development only)
        """
        config = self.LANGUAGE_CONFIGS[language]
        extension = config['extension']
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            start_time = time.time()
            
            # Prepare command
            if language == 'python':
                cmd = ['python', temp_file]
            elif language == 'javascript':
                cmd = ['node', temp_file]
            elif language == 'java':
                # Compile and run Java
                compile_result = subprocess.run(
                    ['javac', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'error': compile_result.stderr,
                        'output': '',
                        'execution_time': 0
                    }
                class_name = Path(temp_file).stem
                cmd = ['java', '-cp', str(Path(temp_file).parent), class_name]
            elif language == 'cpp':
                # Compile C++
                output_file = temp_file.replace('.cpp', '.out')
                compile_result = subprocess.run(
                    ['g++', temp_file, '-o', output_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'error': compile_result.stderr,
                        'output': '',
                        'execution_time': 0
                    }
                cmd = [output_file]
            elif language == 'go':
                cmd = ['go', 'run', temp_file]
            elif language == 'rust':
                output_file = temp_file.replace('.rs', '')
                compile_result = subprocess.run(
                    ['rustc', temp_file, '-o', output_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                if compile_result.returncode != 0:
                    return {
                        'success': False,
                        'error': compile_result.stderr,
                        'output': '',
                        'execution_time': 0
                    }
                cmd = [output_file]
            else:
                cmd = [config['command'], temp_file]
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            # Test case validation
            test_results = []
            if test_cases:
                for i, test_case in enumerate(test_cases):
                    # Run with test input
                    test_result = subprocess.run(
                        cmd,
                        input=test_case.get('input', ''),
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    
                    actual_output = test_result.stdout.strip()
                    expected_output = str(test_case.get('expected', '')).strip()
                    
                    test_results.append({
                        'test_case': i + 1,
                        'passed': actual_output == expected_output,
                        'input': test_case.get('input', ''),
                        'expected': expected_output,
                        'actual': actual_output
                    })
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'execution_time': round(execution_time * 1000, 2),  # Convert to ms
                'test_results': test_results,
                'passed_tests': sum(1 for t in test_results if t['passed']) if test_results else None,
                'total_tests': len(test_results) if test_results else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Execution timeout ({timeout}s)',
                'output': '',
                'execution_time': timeout * 1000
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }
        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
                # Clean up compiled files
                if language == 'java':
                    class_file = temp_file.replace('.java', '.class')
                    if os.path.exists(class_file):
                        os.unlink(class_file)
                elif language == 'cpp':
                    out_file = temp_file.replace('.cpp', '.out')
                    if os.path.exists(out_file):
                        os.unlink(out_file)
                elif language == 'rust':
                    out_file = temp_file.replace('.rs', '')
                    if os.path.exists(out_file):
                        os.unlink(out_file)
            except:
                pass
    
    def _execute_in_docker(
        self,
        code: str,
        language: str,
        test_cases: Optional[List[Dict[str, Any]]],
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute code in Docker container (more secure)
        """
        if not self.docker_client:
            return self._execute_locally(code, language, test_cases, timeout)
        
        config = self.LANGUAGE_CONFIGS[language]
        image = config['docker_image']
        
        try:
            # Pull image if needed
            try:
                self.docker_client.images.get(image)
            except docker.errors.ImageNotFound:
                print(f"Pulling Docker image: {image}")
                self.docker_client.images.pull(image)
            
            start_time = time.time()
            
            # Create temporary directory for code
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = os.path.join(tmpdir, f'code{config["extension"]}')
                with open(code_file, 'w') as f:
                    f.write(code)
                
                # Run container
                container = self.docker_client.containers.run(
                    image,
                    command=f'{config["command"]} /app/code{config["extension"]}',
                    volumes={tmpdir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir='/app',
                    detach=True,
                    mem_limit='256m',
                    network_disabled=True,
                    remove=True
                )
                
                # Wait for completion
                try:
                    result = container.wait(timeout=timeout)
                    logs = container.logs().decode('utf-8')
                    execution_time = time.time() - start_time
                    
                    return {
                        'success': result['StatusCode'] == 0,
                        'output': logs,
                        'error': logs if result['StatusCode'] != 0 else None,
                        'execution_time': round(execution_time * 1000, 2)
                    }
                except Exception as e:
                    container.stop()
                    return {
                        'success': False,
                        'error': f'Container execution failed: {str(e)}',
                        'output': '',
                        'execution_time': 0
                    }
        except Exception as e:
            return {
                'success': False,
                'error': f'Docker execution failed: {str(e)}',
                'output': '',
                'execution_time': 0
            }
    
    def validate_solution(
        self,
        code: str,
        language: str,
        test_cases: List[Dict[str, Any]],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate solution against test cases
        
        Returns:
            Dictionary with validation results including score
        """
        result = self.execute_code(code, language, test_cases, timeout)
        
        if not result['success']:
            return {
                **result,
                'score': 0,
                'passed_all': False
            }
        
        test_results = result.get('test_results', [])
        passed = sum(1 for t in test_results if t['passed'])
        total = len(test_results)
        
        score = (passed / total * 100) if total > 0 else 0
        
        return {
            **result,
            'score': round(score, 2),
            'passed_all': passed == total,
            'passed_tests': passed,
            'total_tests': total
        }
