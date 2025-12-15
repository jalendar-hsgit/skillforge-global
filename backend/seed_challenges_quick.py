"""
Quick seed for coding challenges
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal, engine
from app.modelsx.coding_practice import CodingChallenge, Base
from sqlalchemy import inspect

def create_tables():
    """Create tables if they don't exist"""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created/verified")

def seed_challenges():
    """Add sample challenges"""
    db = SessionLocal()
    
    challenges = [
        {
            "title": "Two Sum Problem",
            "slug": "two-sum",
            "description": "Find two numbers in an array that add up to a target sum. Classic interview question to practice hash maps and arrays.",
            "category": "algorithms",
            "difficulty": "easy",
            "tags": ["arrays", "hash-table", "interview"],
            "problem_statement": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "examples": [{"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"}],
            "supported_languages": ["python", "javascript", "java", "cpp", "go"],
            "starter_code": {"python": "def two_sum(nums, target):\n    # Your code here\n    pass"},
            "test_cases": [
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]}
            ],
            "simulator_type": "code_editor",
            "time_limit_seconds": 5,
            "memory_limit_mb": 128,
            "estimated_time_minutes": 15,
            "points": 10,
            "coins_reward": 5,
            "success_rate": 85.5,
            "is_premium": False
        },
        {
            "title": "Reverse Linked List",
            "slug": "reverse-linked-list",
            "description": "Reverse a singly linked list in-place. Essential data structure problem.",
            "category": "data_structures",
            "difficulty": "easy",
            "tags": ["linked-list", "pointers"],
            "problem_statement": "Given the head of a singly linked list, reverse the list, and return the reversed list.",
            "supported_languages": ["python", "javascript", "java", "cpp"],
            "starter_code": {"python": "def reverseList(head):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 5,
            "estimated_time_minutes": 20,
            "points": 15,
            "coins_reward": 8,
            "success_rate": 78.2,
            "is_premium": False
        },
        {
            "title": "Binary Search Implementation",
            "slug": "binary-search",
            "description": "Implement binary search algorithm for sorted arrays.",
            "category": "algorithms",
            "difficulty": "easy",
            "tags": ["binary-search", "arrays", "divide-conquer"],
            "problem_statement": "Given a sorted array of integers, implement binary search to find the index of a target value.",
            "supported_languages": ["python", "javascript", "java", "cpp", "go"],
            "starter_code": {"python": "def binary_search(arr, target):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 3,
            "estimated_time_minutes": 15,
            "points": 10,
            "coins_reward": 5,
            "success_rate": 88.7,
            "is_premium": False
        },
        {
            "title": "Valid Parentheses",
            "slug": "valid-parentheses",
            "description": "Check if a string of parentheses is valid using stack data structure.",
            "category": "data_structures",
            "difficulty": "easy",
            "tags": ["stack", "string"],
            "problem_statement": "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {"python": "def isValid(s):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 5,
            "estimated_time_minutes": 20,
            "points": 15,
            "coins_reward": 8,
            "success_rate": 75.3,
            "is_premium": False
        },
        {
            "title": "Merge Intervals",
            "slug": "merge-intervals",
            "description": "Merge overlapping intervals - common in scheduling problems.",
            "category": "algorithms",
            "difficulty": "medium",
            "tags": ["arrays", "sorting", "intervals"],
            "problem_statement": "Given an array of intervals, merge all overlapping intervals and return an array of non-overlapping intervals.",
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {"python": "def merge(intervals):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 10,
            "estimated_time_minutes": 30,
            "points": 25,
            "coins_reward": 12,
            "success_rate": 65.8,
            "is_premium": False
        },
        {
            "title": "LRU Cache",
            "slug": "lru-cache",
            "description": "Design and implement a Least Recently Used (LRU) cache.",
            "category": "data_structures",
            "difficulty": "medium",
            "tags": ["hash-table", "linked-list", "design"],
            "problem_statement": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.",
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {"python": "class LRUCache:\n    def __init__(self, capacity):\n        pass\n    \n    def get(self, key):\n        pass\n    \n    def put(self, key, value):\n        pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 10,
            "estimated_time_minutes": 40,
            "points": 35,
            "coins_reward": 18,
            "success_rate": 55.2,
            "is_premium": False
        },
        {
            "title": "Graph DFS Traversal",
            "slug": "graph-dfs",
            "description": "Implement depth-first search traversal for graphs.",
            "category": "algorithms",
            "difficulty": "medium",
            "tags": ["graph", "dfs", "recursion"],
            "problem_statement": "Implement depth-first search to traverse all nodes in a graph starting from a given node.",
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {"python": "def dfs(graph, start):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 10,
            "estimated_time_minutes": 35,
            "points": 30,
            "coins_reward": 15,
            "success_rate": 68.4,
            "is_premium": False
        },
        {
            "title": "Dynamic Programming: Coin Change",
            "slug": "coin-change",
            "description": "Find minimum coins needed to make change using dynamic programming.",
            "category": "algorithms",
            "difficulty": "medium",
            "tags": ["dynamic-programming", "optimization"],
            "problem_statement": "Given an amount and a list of coin denominations, find the minimum number of coins needed to make that amount.",
            "supported_languages": ["python", "javascript", "java"],
            "starter_code": {"python": "def coinChange(coins, amount):\n    # Your code here\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 10,
            "estimated_time_minutes": 45,
            "points": 40,
            "coins_reward": 20,
            "success_rate": 52.7,
            "is_premium": False
        },
        {
            "title": "AWS Lambda REST API",
            "slug": "aws-lambda-api",
            "description": "Build serverless REST API with AWS Lambda and API Gateway.",
            "category": "cloud_aws",
            "difficulty": "medium",
            "tags": ["aws", "lambda", "serverless", "api"],
            "problem_statement": "Create a serverless REST API using AWS Lambda, API Gateway, and DynamoDB for CRUD operations.",
            "supported_languages": ["python", "javascript"],
            "starter_code": {"python": "import json\n\ndef lambda_handler(event, context):\n    # Your code here\n    pass"},
            "simulator_type": "cloud_console",
            "time_limit_seconds": 1800,
            "estimated_time_minutes": 60,
            "points": 75,
            "coins_reward": 40,
            "success_rate": 62.1,
            "is_premium": True
        },
        {
            "title": "Kubernetes Pod Deployment",
            "slug": "kubernetes-pod",
            "description": "Deploy and manage pods in Kubernetes cluster.",
            "category": "devops",
            "difficulty": "medium",
            "tags": ["kubernetes", "containers", "devops"],
            "problem_statement": "Create Kubernetes manifests to deploy a multi-container pod with proper resource limits and health checks.",
            "supported_languages": ["yaml", "bash"],
            "starter_code": {"yaml": "apiVersion: v1\nkind: Pod\nmetadata:\n  name: app-pod\nspec:\n  # Your configuration"},
            "simulator_type": "kubernetes_cluster",
            "time_limit_seconds": 3600,
            "estimated_time_minutes": 75,
            "points": 85,
            "coins_reward": 45,
            "success_rate": 58.3,
            "is_premium": True
        },
        {
            "title": "SQL Query Optimization",
            "slug": "sql-optimization",
            "description": "Optimize slow database queries for better performance.",
            "category": "database",
            "difficulty": "medium",
            "tags": ["sql", "optimization", "indexing"],
            "problem_statement": "Given a slow SQL query, optimize it using indexes, query rewriting, and best practices.",
            "supported_languages": ["sql"],
            "starter_code": {"sql": "-- Optimize this query\nSELECT * FROM orders\nJOIN customers ON orders.customer_id = customers.id\nWHERE orders.status = 'pending';"},
            "simulator_type": "database_query",
            "time_limit_seconds": 600,
            "estimated_time_minutes": 40,
            "points": 45,
            "coins_reward": 22,
            "success_rate": 61.5,
            "is_premium": False
        },
        {
            "title": "Docker Multi-Stage Build",
            "slug": "docker-multistage",
            "description": "Create optimized Docker images using multi-stage builds.",
            "category": "devops",
            "difficulty": "easy",
            "tags": ["docker", "containerization"],
            "problem_statement": "Write a Dockerfile with multi-stage builds to create a production-ready container image.",
            "supported_languages": ["dockerfile"],
            "starter_code": {"dockerfile": "FROM node:18 AS builder\n# Your build steps\n\nFROM node:18-alpine\n# Your production steps"},
            "simulator_type": "container_lab",
            "time_limit_seconds": 1200,
            "estimated_time_minutes": 30,
            "points": 30,
            "coins_reward": 15,
            "success_rate": 72.8,
            "is_premium": False
        },
        {
            "title": "REST API Design",
            "slug": "rest-api-design",
            "description": "Design and test RESTful API endpoints.",
            "category": "web_development",
            "difficulty": "easy",
            "tags": ["rest", "api", "http"],
            "problem_statement": "Design a RESTful API for a blog application with proper HTTP methods, status codes, and response formats.",
            "supported_languages": ["json"],
            "starter_code": {"json": "{\n  \"endpoints\": [\n    // Define your API endpoints\n  ]\n}"},
            "simulator_type": "api_playground",
            "time_limit_seconds": 900,
            "estimated_time_minutes": 35,
            "points": 35,
            "coins_reward": 18,
            "success_rate": 69.2,
            "is_premium": False
        },
        {
            "title": "System Design: URL Shortener",
            "slug": "url-shortener-design",
            "description": "Design a scalable URL shortening service like bit.ly.",
            "category": "system_design",
            "difficulty": "hard",
            "tags": ["system-design", "scalability", "databases"],
            "problem_statement": "Design a URL shortening service that handles millions of requests. Consider database design, caching, and API design.",
            "supported_languages": ["markdown"],
            "starter_code": {"markdown": "# URL Shortener System Design\n\n## Requirements\n- Functional requirements\n- Non-functional requirements\n\n## Design\n- Architecture\n- Database schema\n- API endpoints"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 5400,
            "estimated_time_minutes": 90,
            "points": 120,
            "coins_reward": 60,
            "success_rate": 45.7,
            "is_premium": True
        },
        {
            "title": "Microservices Communication",
            "slug": "microservices-comm",
            "description": "Implement communication between microservices.",
            "category": "system_design",
            "difficulty": "hard",
            "tags": ["microservices", "message-queue", "architecture"],
            "problem_statement": "Design and implement communication patterns between microservices using REST, message queues, and service mesh.",
            "supported_languages": ["python", "javascript"],
            "starter_code": {"python": "# Service A\nimport requests\n\ndef call_service_b():\n    # Implement communication\n    pass"},
            "simulator_type": "code_editor",
            "time_limit_seconds": 7200,
            "estimated_time_minutes": 120,
            "points": 150,
            "coins_reward": 75,
            "success_rate": 38.2,
            "is_premium": True
        }
    ]
    
    added = 0
    updated = 0
    
    for data in challenges:
        existing = db.query(CodingChallenge).filter(CodingChallenge.slug == data["slug"]).first()
        if existing:
            print(f"⏭️  Challenge exists: {data['title']}")
            updated += 1
        else:
            challenge = CodingChallenge(**data)
            db.add(challenge)
            added += 1
            print(f"✅ Added: {data['title']} ({data['difficulty']}, {data['points']} pts)")
    
    try:
        db.commit()
        print(f"\n✅ Added {added} new challenges, {updated} already existed")
        
        # Verify
        final_count = db.query(CodingChallenge).count()
        print(f"📊 Total challenges in database: {final_count}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during commit: {e}")
        print("⚠️  Trying to save without foreign key validation...")
        
        # Try again without commit (might work if FK is deferred)
        db.close()
        db = SessionLocal()
        
        for data in challenges:
            data_copy = data.copy()
            data_copy.pop('created_by', None)  # Remove created_by if exists
            existing = db.query(CodingChallenge).filter(CodingChallenge.slug == data["slug"]).first()
            if not existing:
                challenge = CodingChallenge(**data_copy)
                db.add(challenge)
        
        try:
            db.commit()
            print(f"✅ Saved challenges successfully!")
            print(f"📊 Total challenges: {db.query(CodingChallenge).count()}")
        except Exception as e2:
            db.rollback()
            print(f"❌ Still failed: {e2}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Seeding Coding Practice Challenges")
    print("=" * 70)
    
    create_tables()
    print()
    seed_challenges()
    
    print("\n" + "=" * 70)
    print("✅ Seed complete!")
    print("=" * 70)
