"""
Seed hints for coding challenges
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import SessionLocal
from app.modelsx.coding_practice import CodingChallenge, ChallengeHint

def seed_hints():
    """Add hints to existing challenges"""
    db = SessionLocal()
    
    # Define hints for each challenge
    hints_data = {
        "two-sum": [
            "Think about using a hash map to store numbers you've seen",
            "For each number, check if (target - number) exists in your hash map",
            "You only need to iterate through the array once"
        ],
        "reverse-linked-list": [
            "Use three pointers: previous, current, and next",
            "Start with previous = None and current = head",
            "On each iteration, reverse the 'next' pointer"
        ],
        "valid-parentheses": [
            "Use a stack to keep track of opening brackets",
            "When you see a closing bracket, check if it matches the top of the stack",
            "At the end, the stack should be empty"
        ],
        "binary-search": [
            "Remember: the array must be sorted",
            "Compare the middle element with target",
            "Eliminate half of the search space each iteration"
        ],
        "fibonacci-sequence": [
            "Think about storing previous results to avoid recalculation",
            "You only need to keep track of the last two numbers",
            "Consider both recursive and iterative approaches"
        ],
        "merge-sorted-arrays": [
            "Use two pointers, one for each array",
            "Compare elements and add the smaller one first",
            "Don't forget to handle remaining elements"
        ],
        "maximum-subarray": [
            "Consider Kadane's algorithm",
            "Keep track of the maximum sum ending at current position",
            "Update global maximum as you go"
        ],
        "palindrome-check": [
            "Use two pointers from both ends",
            "Compare characters while moving towards center",
            "Consider handling spaces and case sensitivity"
        ],
        "aws-lambda-deploy": [
            "Make sure your IAM role has lambda:CreateFunction permission",
            "Use the AWS CLI command: aws lambda create-function",
            "Don't forget to zip your code first"
        ],
        "docker-compose-setup": [
            "Start with version: '3.8' in your compose file",
            "Define services with 'services:' key",
            "Remember to map ports with 'ports:' directive"
        ],
        "kubernetes-pod-debug": [
            "Use kubectl logs <pod-name> to check logs",
            "kubectl describe pod <pod-name> shows events",
            "Check if resource limits are causing restarts"
        ],
        "rest-api-design": [
            "Use proper HTTP methods: GET, POST, PUT, DELETE",
            "Follow RESTful naming conventions for endpoints",
            "Return appropriate status codes (200, 201, 404, etc.)"
        ],
        "sql-query-optimization": [
            "Use EXPLAIN to analyze query execution plan",
            "Add indexes on columns used in WHERE and JOIN clauses",
            "Avoid SELECT * when you only need specific columns"
        ],
        "implement-lru-cache": [
            "Combine a hash map with a doubly linked list",
            "Hash map provides O(1) access, linked list manages order",
            "Move accessed items to front, remove from tail when full"
        ],
        "detect-cycle-linked-list": [
            "Use Floyd's cycle detection (tortoise and hare)",
            "Have two pointers moving at different speeds",
            "If they meet, there's a cycle"
        ]
    }
    
    try:
        for slug, hint_texts in hints_data.items():
            challenge = db.query(CodingChallenge).filter(CodingChallenge.slug == slug).first()
            
            if not challenge:
                print(f"⚠️  Challenge '{slug}' not found, skipping hints")
                continue
            
            # Check if hints already exist
            existing_hints = db.query(ChallengeHint).filter(
                ChallengeHint.challenge_id == challenge.id
            ).count()
            
            if existing_hints > 0:
                print(f"⚠️  Hints already exist for '{slug}', skipping")
                continue
            
            # Add hints
            for order, hint_text in enumerate(hint_texts, start=1):
                hint = ChallengeHint(
                    challenge_id=challenge.id,
                    hint_text=hint_text,
                    hint_order=order,
                    cost_coins=(order * 5)  # Progressive cost: 5, 10, 15 coins
                )
                db.add(hint)
            
            print(f"✅ Added {len(hint_texts)} hints to '{slug}'")
        
        db.commit()
        print("\n✅ All hints seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding hints: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding hints for coding challenges...\n")
    seed_hints()
