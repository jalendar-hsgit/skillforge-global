"""
Seed Premium Courses and Coding Practice Challenges
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.modelsx.course import Course
from app.modelsx.coding_practice import (
    CodingChallenge, SimulatorEnvironment, CloudLabScenario,
    ChallengeHint
)
from datetime import datetime


def seed_premium_courses():
    """Add premium courses with high-quality content"""
    db = SessionLocal()
    
    premium_courses = [
        {
            "path": "advanced-python-mastery",
            "title": "Advanced Python Mastery",
            "description": "Master advanced Python concepts including decorators, metaclasses, async programming, and performance optimization",
            "category": "Programming",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 79.99,
            "instructor": "David Johnson",
            "difficulty": "advanced",
            "duration_hours": 40.0,
            "rating": 4.8,
            "youtube_playlist_id": "PLeo1K3hjS3uu7CxVacqLXYA5U_-RUU0Ot"  # Real Python playlist
        },
        {
            "path": "system-design-interview-prep",
            "title": "System Design Interview Preparation",
            "description": "Complete guide to acing system design interviews at top tech companies. Learn scalability, microservices, and distributed systems",
            "category": "System Design",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 99.99,
            "instructor": "Sarah Chen",
            "difficulty": "advanced",
            "duration_hours": 50.0,
            "rating": 4.9
        },
        {
            "path": "aws-solutions-architect-pro",
            "title": "AWS Solutions Architect Professional",
            "description": "Comprehensive AWS certification preparation with hands-on labs and real-world scenarios",
            "category": "Cloud Computing",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 149.99,
            "instructor": "Michael Rodriguez",
            "difficulty": "advanced",
            "duration_hours": 60.0,
            "rating": 4.9,
            "youtube_playlist_id": "PL2yQDdvlhXf_Y0c_6f-"  # Mock
        },
        {
            "path": "kubernetes-production-ready",
            "title": "Kubernetes for Production",
            "description": "Learn Kubernetes from basics to production deployment with security, monitoring, and best practices",
            "category": "DevOps",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 89.99,
            "instructor": "Alex Kumar",
            "difficulty": "intermediate",
            "duration_hours": 35.0,
            "rating": 4.7
        },
        {
            "path": "machine-learning-engineering",
            "title": "Machine Learning Engineering",
            "description": "End-to-end ML engineering: model training, deployment, monitoring, and MLOps best practices",
            "category": "AI & Machine Learning",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 129.99,
            "instructor": "Dr. Emily Zhang",
            "difficulty": "advanced",
            "duration_hours": 55.0,
            "rating": 4.8
        },
        {
            "path": "fullstack-nextjs-enterprise",
            "title": "Full-Stack Next.js Enterprise",
            "description": "Build production-ready enterprise applications with Next.js 14, TypeScript, and modern best practices",
            "category": "Web Development",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 94.99,
            "instructor": "James Wilson",
            "difficulty": "intermediate",
            "duration_hours": 42.0,
            "rating": 4.7
        },
        {
            "path": "data-engineering-masterclass",
            "title": "Data Engineering Masterclass",
            "description": "Master data pipelines, ETL, data warehousing with Spark, Airflow, and modern data stack",
            "category": "Data Engineering",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 119.99,
            "instructor": "Maria Santos",
            "difficulty": "advanced",
            "duration_hours": 48.0,
            "rating": 4.9
        },
        {
            "path": "cybersecurity-ethical-hacking",
            "title": "Cybersecurity & Ethical Hacking",
            "description": "Comprehensive cybersecurity training: penetration testing, vulnerability assessment, and defense strategies",
            "category": "Cybersecurity",
            "tier": "premium",
            "is_premium": True,
            "is_paid": True,
            "price": 109.99,
            "instructor": "Robert Anderson",
            "difficulty": "intermediate",
            "duration_hours": 45.0,
            "rating": 4.8
        }
    ]
    
    added = 0
    for course_data in premium_courses:
        # Check if exists
        existing = db.query(Course).filter(Course.path == course_data["path"]).first()
        if not existing:
            course = Course(**course_data)
            db.add(course)
            added += 1
            print(f"✅ Added premium course: {course_data['title']}")
        else:
            print(f"⏭️  Course already exists: {course_data['title']}")
    
    db.commit()
    print(f"\n📚 Added {added} premium courses")
    db.close()


def seed_coding_challenges():
    """Add coding practice challenges"""
    db = SessionLocal()
    
    challenges = [
        {
            "title": "Two Sum Problem",
            "slug": "two-sum-problem",
            "description": "Find two numbers in an array that add up to a target sum",
            "category": "algorithms",
            "difficulty": "easy",
            "tags": ["arrays", "hash-table", "interview"],
            "problem_statement": """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]"
                }
            ],
            "supported_languages": ["python", "javascript", "java", "cpp"],
            "starter_code": {
                "python": "def two_sum(nums, target):\n    # Your code here\n    pass",
                "javascript": "function twoSum(nums, target) {\n    // Your code here\n}",
                "java": "public int[] twoSum(int[] nums, int target) {\n    // Your code here\n}",
                "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    // Your code here\n}"
            },
            "test_cases": [
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1], "hidden": False},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2], "hidden": False},
                {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1], "hidden": True}
            ],
            "simulator_type": "code_editor",
            "time_limit_seconds": 5,
            "memory_limit_mb": 128,
            "estimated_time_minutes": 15,
            "points": 10,
            "coins_reward": 5,
            "is_premium": False
        },
        {
            "title": "Binary Tree Level Order Traversal",
            "slug": "binary-tree-level-order",
            "description": "Traverse a binary tree level by level",
            "category": "data_structures",
            "difficulty": "medium",
            "tags": ["trees", "bfs", "queue"],
            "problem_statement": """Given the root of a binary tree, return the level order traversal of its nodes' values. (i.e., from left to right, level by level).""",
            "examples": [
                {
                    "input": "root = [3,9,20,null,null,15,7]",
                    "output": "[[3],[9,20],[15,7]]",
                    "explanation": "Level 1: [3], Level 2: [9,20], Level 3: [15,7]"
                }
            ],
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {
                "python": "def levelOrder(root):\n    # Your code here\n    pass"
            },
            "test_cases": [],
            "simulator_type": "code_editor",
            "time_limit_seconds": 10,
            "memory_limit_mb": 256,
            "estimated_time_minutes": 25,
            "points": 20,
            "coins_reward": 10,
            "is_premium": False
        },
        {
            "title": "Deploy Lambda Function with API Gateway",
            "slug": "aws-lambda-api-gateway",
            "description": "Create and deploy a serverless API using AWS Lambda and API Gateway",
            "category": "cloud_aws",
            "difficulty": "medium",
            "tags": ["aws", "lambda", "api-gateway", "serverless"],
            "problem_statement": """Create a serverless REST API that:
1. Accepts POST requests with JSON data
2. Processes the data with a Lambda function
3. Returns a JSON response
4. Uses API Gateway for HTTP endpoint""",
            "examples": [],
            "supported_languages": ["python", "javascript"],
            "starter_code": {
                "python": "import json\n\ndef lambda_handler(event, context):\n    # Your code here\n    pass"
            },
            "test_cases": [],
            "simulator_type": "cloud_console",
            "simulator_config": {"cloud_provider": "aws", "services": ["lambda", "apigateway"]},
            "requires_cloud_access": True,
            "cloud_provider": "aws",
            "time_limit_seconds": 1800,  # 30 minutes
            "estimated_time_minutes": 45,
            "points": 50,
            "coins_reward": 25,
            "is_premium": True
        },
        {
            "title": "Kubernetes Multi-Container Pod",
            "slug": "kubernetes-multi-container",
            "description": "Deploy and manage a multi-container pod in Kubernetes",
            "category": "devops",
            "difficulty": "hard",
            "tags": ["kubernetes", "containers", "devops"],
            "problem_statement": """Create a Kubernetes pod with:
1. Main application container (nginx)
2. Sidecar logging container
3. Shared volume between containers
4. Proper resource limits
5. Health checks""",
            "examples": [],
            "supported_languages": ["yaml", "bash"],
            "starter_code": {
                "yaml": "apiVersion: v1\nkind: Pod\nmetadata:\n  name: multi-container-pod\nspec:\n  # Your configuration here"
            },
            "test_cases": [],
            "simulator_type": "kubernetes_cluster",
            "time_limit_seconds": 3600,
            "estimated_time_minutes": 60,
            "points": 100,
            "coins_reward": 50,
            "is_premium": True
        },
        {
            "title": "SQL Query Optimization",
            "slug": "sql-query-optimization",
            "description": "Optimize slow SQL queries for better performance",
            "category": "database",
            "difficulty": "medium",
            "tags": ["sql", "database", "optimization"],
            "problem_statement": """Given a slow SQL query, optimize it by:
1. Adding appropriate indexes
2. Rewriting joins
3. Using EXPLAIN to analyze
4. Reducing execution time by 80%""",
            "examples": [],
            "supported_languages": ["sql"],
            "starter_code": {
                "sql": "-- Original slow query\nSELECT * FROM orders o\nJOIN customers c ON o.customer_id = c.id\nWHERE o.status = 'pending';\n\n-- Optimize this query"
            },
            "test_cases": [],
            "simulator_type": "database_query",
            "estimated_time_minutes": 30,
            "points": 30,
            "coins_reward": 15,
            "is_premium": False
        }
    ]
    
    added = 0
    for challenge_data in challenges:
        existing = db.query(CodingChallenge).filter(CodingChallenge.slug == challenge_data["slug"]).first()
        if not existing:
            challenge = CodingChallenge(**challenge_data)
            db.add(challenge)
            db.flush()
            
            # Add hints for beginner/easy challenges
            if challenge_data["difficulty"] in ["easy", "beginner"]:
                hints = [
                    ChallengeHint(
                        challenge_id=challenge.id,
                        hint_text="Try using a hash map to store values you've seen",
                        hint_order=1,
                        cost_coins=2
                    ),
                    ChallengeHint(
                        challenge_id=challenge.id,
                        hint_text="For each number, check if (target - number) exists in your hash map",
                        hint_order=2,
                        cost_coins=3
                    )
                ]
                for hint in hints:
                    db.add(hint)
            
            added += 1
            print(f"✅ Added challenge: {challenge_data['title']}")
        else:
            print(f"⏭️  Challenge already exists: {challenge_data['title']}")
    
    db.commit()
    print(f"\n💻 Added {added} coding challenges")
    db.close()


def seed_simulator_environments():
    """Add simulator environments"""
    db = SessionLocal()
    
    environments = [
        {
            "name": "Python 3.11 Sandbox",
            "description": "Standard Python environment with popular libraries",
            "simulator_type": "code_editor",
            "base_image": "python:3.11-slim",
            "environment_variables": {"PYTHON_VERSION": "3.11"},
            "is_premium": False,
            "max_session_minutes": 30,
            "cpu_limit": 0.5,
            "memory_limit_mb": 256
        },
        {
            "name": "AWS Developer Environment",
            "description": "AWS CLI and SDK pre-configured",
            "simulator_type": "cloud_console",
            "base_image": "amazon/aws-cli",
            "cloud_provider": "aws",
            "cloud_services": ["lambda", "s3", "dynamodb", "apigateway"],
            "is_premium": True,
            "max_session_minutes": 120,
            "cpu_limit": 1.0,
            "memory_limit_mb": 512
        },
        {
            "name": "Kubernetes Cluster",
            "description": "Managed Kubernetes cluster with kubectl",
            "simulator_type": "kubernetes_cluster",
            "base_image": "kindest/node:v1.27.0",
            "is_premium": True,
            "max_session_minutes": 180,
            "cpu_limit": 2.0,
            "memory_limit_mb": 2048
        },
        {
            "name": "PostgreSQL Database",
            "description": "PostgreSQL 15 with sample data",
            "simulator_type": "database_query",
            "base_image": "postgres:15",
            "environment_variables": {"POSTGRES_DB": "practice"},
            "is_premium": False,
            "max_session_minutes": 60,
            "cpu_limit": 0.5,
            "memory_limit_mb": 512
        }
    ]
    
    added = 0
    for env_data in environments:
        existing = db.query(SimulatorEnvironment).filter(
            SimulatorEnvironment.name == env_data["name"]
        ).first()
        if not existing:
            env = SimulatorEnvironment(**env_data)
            db.add(env)
            added += 1
            print(f"✅ Added environment: {env_data['name']}")
    
    db.commit()
    print(f"\n🖥️  Added {added} simulator environments")
    db.close()


def seed_cloud_labs():
    """Add cloud lab scenarios"""
    db = SessionLocal()
    
    labs = [
        {
            "title": "Build Serverless REST API",
            "slug": "serverless-rest-api",
            "description": "Create a complete serverless API with Lambda, API Gateway, and DynamoDB",
            "cloud_provider": "aws",
            "services_used": ["lambda", "apigateway", "dynamodb", "iam"],
            "objective": "Deploy a production-ready serverless API that handles CRUD operations",
            "instructions": """1. Create DynamoDB table
2. Write Lambda functions for CRUD operations
3. Set up API Gateway endpoints
4. Configure IAM permissions
5. Test all endpoints""",
            "difficulty": "medium",
            "estimated_time_minutes": 90,
            "points_reward": 100,
            "coins_reward": 50,
            "is_premium": True
        },
        {
            "title": "Deploy Microservices on Kubernetes",
            "slug": "k8s-microservices",
            "description": "Deploy a multi-service application on Kubernetes with service mesh",
            "cloud_provider": "aws",
            "services_used": ["eks", "ecr", "loadbalancer"],
            "objective": "Deploy and manage microservices architecture on Kubernetes",
            "instructions": """1. Create EKS cluster
2. Build and push Docker images to ECR
3. Create Kubernetes deployments
4. Set up services and ingress
5. Implement health checks and monitoring""",
            "difficulty": "hard",
            "estimated_time_minutes": 120,
            "points_reward": 150,
            "coins_reward": 75,
            "is_premium": True
        },
        {
            "title": "Azure Functions with Cosmos DB",
            "slug": "azure-functions-cosmos",
            "description": "Build serverless functions on Azure with Cosmos DB backend",
            "cloud_provider": "azure",
            "services_used": ["functions", "cosmosdb", "storage"],
            "objective": "Create Azure Functions that interact with Cosmos DB",
            "instructions": """1. Create Cosmos DB account and database
2. Write Azure Functions for data operations
3. Configure triggers and bindings
4. Implement error handling
5. Test functions""",
            "difficulty": "medium",
            "estimated_time_minutes": 75,
            "points_reward": 90,
            "coins_reward": 45,
            "is_premium": True
        }
    ]
    
    added = 0
    for lab_data in labs:
        existing = db.query(CloudLabScenario).filter(CloudLabScenario.slug == lab_data["slug"]).first()
        if not existing:
            lab = CloudLabScenario(**lab_data)
            db.add(lab)
            added += 1
            print(f"✅ Added cloud lab: {lab_data['title']}")
    
    db.commit()
    print(f"\n☁️  Added {added} cloud lab scenarios")
    db.close()


if __name__ == "__main__":
    print("🌱 Starting seed process...\n")
    print("=" * 60)
    
    print("\n1️⃣  Seeding Premium Courses...")
    seed_premium_courses()
    
    print("\n2️⃣  Seeding Coding Challenges...")
    seed_coding_challenges()
    
    print("\n3️⃣  Seeding Simulator Environments...")
    seed_simulator_environments()
    
    print("\n4️⃣  Seeding Cloud Lab Scenarios...")
    seed_cloud_labs()
    
    print("\n" + "=" * 60)
    print("✅ Seed process completed!")
    print("\n📊 Summary:")
    print("   - Premium courses with advanced topics")
    print("   - Coding challenges for practice")
    print("   - Simulator environments ready")
    print("   - Cloud lab scenarios for hands-on experience")
