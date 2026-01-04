"""
Seed script for Forums, Learning Paths, and Code Snippets
Populates demo data for community features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, engine, Base
from app.models.user import User
from app.modelsx.forums import ForumCategory, ForumThread, ThreadType, ThreadStatus
from app.modelsx.learning_paths import LearningPath, PathChallenge, PathDifficulty, PathStatus
from app.modelsx.code_snippets import CodeSnippet
from app.modelsx.coding_practice import CodingChallenge  # Needed for PathChallenge relationship


class ForumsPathsSnippetsSeeder:
    """Seeds forums, learning paths, and code snippets demo data"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def seed_forum_categories(self):
        """Create forum categories"""
        print("\n📚 Seeding Forum Categories...")
        
        categories = [
            {
                "name": "Getting Started",
                "slug": "getting-started",
                "description": "New to SkillForge? Start here! Ask questions about the platform, find resources for beginners, and connect with fellow learners.",
                "icon_emoji": "🚀",
                "display_order": 1
            },
            {
                "name": "Python & Data Science",
                "slug": "python-data-science",
                "description": "Discuss Python programming, data analysis, machine learning, pandas, NumPy, and all things data science.",
                "icon_emoji": "🐍",
                "display_order": 2
            },
            {
                "name": "JavaScript & Web Dev",
                "slug": "javascript-web-dev",
                "description": "Frontend, backend, React, Node.js, TypeScript - all web development topics welcome!",
                "icon_emoji": "⚛️",
                "display_order": 3
            },
            {
                "name": "Algorithms & Data Structures",
                "slug": "algorithms-data-structures",
                "description": "Practice problems, interview prep, complexity analysis, and algorithm discussions.",
                "icon_emoji": "🧮",
                "display_order": 4
            },
            {
                "name": "Career & Interview Prep",
                "slug": "career-interview-prep",
                "description": "Resume reviews, interview tips, job search strategies, and career advice.",
                "icon_emoji": "💼",
                "display_order": 5
            },
            {
                "name": "Study Groups",
                "slug": "study-groups",
                "description": "Find study partners, join accountability groups, and collaborate on learning goals.",
                "icon_emoji": "👥",
                "display_order": 6
            },
            {
                "name": "Project Showcase",
                "slug": "project-showcase",
                "description": "Share your projects, get feedback, and celebrate your accomplishments!",
                "icon_emoji": "🏆",
                "display_order": 7
            },
            {
                "name": "Announcements",
                "slug": "announcements",
                "description": "Platform updates, new features, and important news from the SkillForge team.",
                "icon_emoji": "📢",
                "display_order": 0
            }
        ]
        
        created_count = 0
        for cat_data in categories:
            existing = self.db.query(ForumCategory).filter(
                ForumCategory.slug == cat_data["slug"]
            ).first()
            
            if not existing:
                category = ForumCategory(**cat_data, is_active=True)
                self.db.add(category)
                created_count += 1
                print(f"  ✅ Created category: {cat_data['name']}")
            else:
                print(f"  ⏭️  Category exists: {cat_data['name']}")
        
        self.db.commit()
        print(f"  📊 Total: {created_count} new categories created")
        return created_count
    
    def seed_forum_threads(self):
        """Create sample forum threads"""
        print("\n💬 Seeding Forum Threads...")
        
        # Get categories
        getting_started = self.db.query(ForumCategory).filter(
            ForumCategory.slug == "getting-started"
        ).first()
        
        python_cat = self.db.query(ForumCategory).filter(
            ForumCategory.slug == "python-data-science"
        ).first()
        
        algo_cat = self.db.query(ForumCategory).filter(
            ForumCategory.slug == "algorithms-data-structures"
        ).first()
        
        # Get a user to be the creator
        user = self.db.query(User).filter(User.email == "john.doe@example.com").first()
        if not user:
            user = self.db.query(User).first()
        
        if not user or not getting_started:
            print("  ⚠️  No user or categories found, skipping threads")
            return 0
        
        threads = [
            {
                "category_id": getting_started.id,
                "creator_id": user.id,
                "title": "Welcome! Introduce yourself here 👋",
                "content": """Hi everyone! 

This is the official introduction thread for SkillForge. Drop a comment and tell us:

1. What's your name?
2. Where are you from?
3. What are you learning?
4. What are your goals?

Looking forward to meeting you all!""",
                "thread_type": ThreadType.DISCUSSION.value,
                "status": ThreadStatus.OPEN.value,
                "tags": ["welcome", "introductions", "community"]
            },
            {
                "category_id": python_cat.id if python_cat else getting_started.id,
                "creator_id": user.id,
                "title": "Best resources for learning Python in 2024?",
                "content": """I'm starting my Python journey and want to make sure I'm using the best resources.

What do you recommend for:
- **Beginners**: Books, courses, tutorials
- **Practice**: Coding challenges, projects
- **Advanced**: Design patterns, best practices

Thanks for any suggestions! 🐍""",
                "thread_type": ThreadType.QUESTION.value,
                "status": ThreadStatus.OPEN.value,
                "tags": ["python", "learning", "resources", "beginner"]
            },
            {
                "category_id": algo_cat.id if algo_cat else getting_started.id,
                "creator_id": user.id,
                "title": "How to approach Two Pointer problems?",
                "content": """I keep seeing Two Pointer technique mentioned in interview prep, but I struggle with recognizing when to use it.

Can someone explain:
1. What problems are good candidates for two pointers?
2. How do you decide which direction to move the pointers?
3. Any practice problems you'd recommend?

Thanks!""",
                "thread_type": ThreadType.QUESTION.value,
                "status": ThreadStatus.OPEN.value,
                "tags": ["algorithms", "two-pointers", "interview-prep", "patterns"]
            }
        ]
        
        created_count = 0
        for thread_data in threads:
            existing = self.db.query(ForumThread).filter(
                ForumThread.title == thread_data["title"]
            ).first()
            
            if not existing:
                thread = ForumThread(**thread_data)
                self.db.add(thread)
                created_count += 1
                print(f"  ✅ Created thread: {thread_data['title'][:50]}...")
            else:
                print(f"  ⏭️  Thread exists: {thread_data['title'][:50]}...")
        
        self.db.commit()
        print(f"  📊 Total: {created_count} new threads created")
        return created_count
    
    def seed_learning_paths(self):
        """Create learning paths"""
        print("\n🛤️  Seeding Learning Paths...")
        
        # Get admin user for created_by
        admin = self.db.query(User).filter(User.email == "admin@skillforge.com").first()
        admin_id = admin.id if admin else None
        
        paths = [
            {
                "title": "Python Fundamentals",
                "description": "Master the basics of Python programming. Learn variables, data types, control flow, functions, and more. Perfect for absolute beginners.",
                "icon": "🐍",
                "difficulty": PathDifficulty.BEGINNER,
                "estimated_hours": 20,
                "status": PathStatus.PUBLISHED,
                "is_featured": True,
                "order": 1,
                "created_by": admin_id
            },
            {
                "title": "Data Structures Mastery",
                "description": "Deep dive into essential data structures: arrays, linked lists, stacks, queues, trees, graphs, and hash tables. Build a solid foundation for technical interviews.",
                "icon": "🏗️",
                "difficulty": PathDifficulty.INTERMEDIATE,
                "estimated_hours": 40,
                "status": PathStatus.PUBLISHED,
                "is_featured": True,
                "order": 2,
                "created_by": admin_id
            },
            {
                "title": "Algorithm Design Patterns",
                "description": "Learn common algorithm patterns: Two Pointers, Sliding Window, Binary Search, BFS/DFS, Dynamic Programming, and Greedy algorithms.",
                "icon": "⚡",
                "difficulty": PathDifficulty.INTERMEDIATE,
                "estimated_hours": 50,
                "status": PathStatus.PUBLISHED,
                "is_featured": True,
                "order": 3,
                "created_by": admin_id
            },
            {
                "title": "Web Development with JavaScript",
                "description": "Build modern web applications with JavaScript. Covers DOM manipulation, async programming, APIs, and popular frameworks.",
                "icon": "🌐",
                "difficulty": PathDifficulty.BEGINNER,
                "estimated_hours": 30,
                "status": PathStatus.PUBLISHED,
                "is_featured": False,
                "order": 4,
                "created_by": admin_id
            },
            {
                "title": "Interview Preparation",
                "description": "Comprehensive interview prep path covering behavioral questions, system design basics, and top coding patterns seen in FAANG interviews.",
                "icon": "💼",
                "difficulty": PathDifficulty.ADVANCED,
                "estimated_hours": 60,
                "status": PathStatus.PUBLISHED,
                "is_featured": True,
                "order": 5,
                "created_by": admin_id
            },
            {
                "title": "SQL & Database Fundamentals",
                "description": "Learn SQL from scratch. Master queries, joins, aggregations, subqueries, and database design principles.",
                "icon": "🗃️",
                "difficulty": PathDifficulty.BEGINNER,
                "estimated_hours": 15,
                "status": PathStatus.PUBLISHED,
                "is_featured": False,
                "order": 6,
                "created_by": admin_id
            }
        ]
        
        created_count = 0
        for path_data in paths:
            existing = self.db.query(LearningPath).filter(
                LearningPath.title == path_data["title"]
            ).first()
            
            if not existing:
                path = LearningPath(**path_data)
                self.db.add(path)
                created_count += 1
                print(f"  ✅ Created path: {path_data['title']}")
            else:
                print(f"  ⏭️  Path exists: {path_data['title']}")
        
        self.db.commit()
        print(f"  📊 Total: {created_count} new paths created")
        return created_count
    
    def seed_code_snippets(self):
        """Create code snippets library"""
        print("\n📝 Seeding Code Snippets...")
        
        snippets = [
            {
                "title": "Binary Search",
                "slug": "binary-search-python",
                "description": "Classic binary search implementation for sorted arrays",
                "category": "searching",
                "language": "python",
                "code": '''def binary_search(arr, target):
    """
    Binary search for target in sorted array.
    Returns index if found, -1 otherwise.
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Example usage:
# arr = [1, 3, 5, 7, 9, 11, 13]
# index = binary_search(arr, 7)  # Returns 3''',
                "explanation": "Binary search works by repeatedly dividing the search interval in half. Start with the middle element - if it matches, we're done. If the target is smaller, search the left half; if larger, search the right half. This reduces the search space by half each iteration.",
                "tags": ["searching", "binary-search", "interview", "classic"],
                "complexity": "O(log n)",
                "uses_count": 150,
                "helpful_count": 42
            },
            {
                "title": "Two Sum (Hash Map)",
                "slug": "two-sum-hashmap",
                "description": "Optimal O(n) solution using hash map for Two Sum problem",
                "category": "arrays",
                "language": "python",
                "code": '''def two_sum(nums, target):
    """
    Find two numbers that add up to target.
    Returns indices of the two numbers.
    Time: O(n), Space: O(n)
    """
    seen = {}  # value -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in seen:
            return [seen[complement], i]
        
        seen[num] = i
    
    return []

# Example usage:
# nums = [2, 7, 11, 15]
# target = 9
# result = two_sum(nums, target)  # Returns [0, 1]''',
                "explanation": "Instead of checking every pair (O(n²)), we use a hash map to remember numbers we've seen. For each number, we check if its complement (target - num) exists in our map. This gives us O(1) lookup time.",
                "tags": ["arrays", "hash-map", "two-sum", "interview", "leetcode"],
                "complexity": "O(n)",
                "uses_count": 320,
                "helpful_count": 89
            },
            {
                "title": "Merge Sort",
                "slug": "merge-sort-python",
                "description": "Divide and conquer sorting algorithm with O(n log n) complexity",
                "category": "sorting",
                "language": "python",
                "code": '''def merge_sort(arr):
    """
    Merge sort implementation.
    Time: O(n log n), Space: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """Merge two sorted arrays"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Example usage:
# arr = [64, 34, 25, 12, 22, 11, 90]
# sorted_arr = merge_sort(arr)''',
                "explanation": "Merge sort divides the array in half recursively until we have single elements (base case). Then it merges sorted subarrays back together. The merge step compares elements from both halves and builds the sorted result.",
                "tags": ["sorting", "divide-conquer", "recursive", "interview"],
                "complexity": "O(n log n)",
                "uses_count": 180,
                "helpful_count": 56
            },
            {
                "title": "BFS Level Order Traversal",
                "slug": "bfs-level-order-tree",
                "description": "Breadth-first search for binary tree level order traversal",
                "category": "trees",
                "language": "python",
                "code": '''from collections import deque

def level_order(root):
    """
    BFS level order traversal of binary tree.
    Returns list of levels, each level is a list of values.
    Time: O(n), Space: O(n)
    """
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
    
    return result

# Example usage with TreeNode class:
# root = TreeNode(3)
# root.left = TreeNode(9)
# root.right = TreeNode(20)
# levels = level_order(root)  # [[3], [9, 20]]''',
                "explanation": "BFS uses a queue to process nodes level by level. We track the size of each level before processing to know when one level ends and the next begins. This pattern is useful for many tree problems.",
                "tags": ["trees", "bfs", "traversal", "queue", "interview"],
                "complexity": "O(n)",
                "uses_count": 145,
                "helpful_count": 38
            },
            {
                "title": "Sliding Window Maximum",
                "slug": "sliding-window-max",
                "description": "Find maximum in each sliding window using deque",
                "category": "arrays",
                "language": "python",
                "code": '''from collections import deque

def max_sliding_window(nums, k):
    """
    Find max element in each sliding window of size k.
    Time: O(n), Space: O(k)
    """
    result = []
    dq = deque()  # stores indices, front is always max
    
    for i, num in enumerate(nums):
        # Remove elements outside window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        
        # Remove smaller elements (they won't be max)
        while dq and nums[dq[-1]] < num:
            dq.pop()
        
        dq.append(i)
        
        # Add max to result when window is full
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result

# Example usage:
# nums = [1, 3, -1, -3, 5, 3, 6, 7]
# k = 3
# maxes = max_sliding_window(nums, k)  # [3, 3, 5, 5, 6, 7]''',
                "explanation": "We use a monotonic decreasing deque that stores indices. The front always has the maximum for the current window. When adding a new element, we remove smaller elements from the back (they can't be max anymore) and expired indices from the front.",
                "tags": ["sliding-window", "deque", "monotonic", "hard", "interview"],
                "complexity": "O(n)",
                "uses_count": 95,
                "helpful_count": 31
            },
            {
                "title": "DFS Graph Traversal",
                "slug": "dfs-graph-traversal",
                "description": "Depth-first search for graph traversal (iterative and recursive)",
                "category": "graphs",
                "language": "python",
                "code": '''def dfs_recursive(graph, start, visited=None):
    """
    Recursive DFS traversal.
    Time: O(V + E), Space: O(V)
    """
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    
    return visited

def dfs_iterative(graph, start):
    """
    Iterative DFS using stack.
    Time: O(V + E), Space: O(V)
    """
    visited = set()
    stack = [start]
    
    while stack:
        node = stack.pop()
        
        if node not in visited:
            visited.add(node)
            print(node, end=' ')
            
            # Add neighbors in reverse for same order as recursive
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return visited

# Example usage:
# graph = {
#     'A': ['B', 'C'],
#     'B': ['A', 'D', 'E'],
#     'C': ['A', 'F'],
#     'D': ['B'],
#     'E': ['B', 'F'],
#     'F': ['C', 'E']
# }
# dfs_recursive(graph, 'A')''',
                "explanation": "DFS explores as far as possible along each branch before backtracking. Recursive version uses call stack implicitly. Iterative version uses explicit stack. Both have same time complexity but iterative avoids stack overflow for deep graphs.",
                "tags": ["graphs", "dfs", "traversal", "recursion", "stack"],
                "complexity": "O(V + E)",
                "uses_count": 210,
                "helpful_count": 67
            },
            {
                "title": "Quick Sort",
                "slug": "quick-sort-python",
                "description": "In-place quick sort with Lomuto partition scheme",
                "category": "sorting",
                "language": "python",
                "code": '''def quick_sort(arr, low=0, high=None):
    """
    Quick sort implementation (in-place).
    Time: O(n log n) avg, O(n²) worst
    Space: O(log n) for recursion stack
    """
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_idx = partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)

def partition(arr, low, high):
    """Lomuto partition scheme"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# Example usage:
# arr = [10, 7, 8, 9, 1, 5]
# quick_sort(arr)
# print(arr)  # [1, 5, 7, 8, 9, 10]''',
                "explanation": "Quick sort picks a pivot element and partitions the array so elements smaller than pivot are on the left, larger on the right. It then recursively sorts the subarrays. Lomuto partition uses the last element as pivot and maintains a boundary index.",
                "tags": ["sorting", "divide-conquer", "in-place", "interview"],
                "complexity": "O(n log n)",
                "uses_count": 165,
                "helpful_count": 48
            },
            {
                "title": "LRU Cache",
                "slug": "lru-cache-implementation",
                "description": "Least Recently Used cache with O(1) get and put operations",
                "category": "data_structures",
                "language": "python",
                "code": '''from collections import OrderedDict

class LRUCache:
    """
    LRU Cache with O(1) get and put.
    Uses OrderedDict for order tracking.
    """
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)

# Example usage:
# cache = LRUCache(2)
# cache.put(1, 1)
# cache.put(2, 2)
# cache.get(1)       # returns 1
# cache.put(3, 3)    # evicts key 2
# cache.get(2)       # returns -1''',
                "explanation": "LRU Cache evicts the least recently used item when full. We use OrderedDict which maintains insertion order. On access, we move the key to the end. When evicting, we remove from the front (oldest). This gives O(1) for both operations.",
                "tags": ["data-structures", "cache", "design", "interview", "leetcode"],
                "complexity": "O(1)",
                "uses_count": 280,
                "helpful_count": 92
            },
            {
                "title": "Fibonacci with Memoization",
                "slug": "fibonacci-memoization",
                "description": "Dynamic programming solution for Fibonacci using memoization",
                "category": "dynamic_programming",
                "language": "python",
                "code": '''def fib_memo(n, memo=None):
    """
    Fibonacci with memoization (top-down DP).
    Time: O(n), Space: O(n)
    """
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

def fib_tabulation(n):
    """
    Fibonacci with tabulation (bottom-up DP).
    Time: O(n), Space: O(1)
    """
    if n <= 1:
        return n
    
    prev2, prev1 = 0, 1
    
    for _ in range(2, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    
    return prev1

# Example usage:
# print(fib_memo(50))        # 12586269025
# print(fib_tabulation(50))  # 12586269025''',
                "explanation": "Naive recursion has O(2^n) time due to repeated calculations. Memoization stores results of subproblems. Tabulation builds solution iteratively from base cases. Space-optimized version only keeps last two values since we only need those to compute the next.",
                "tags": ["dynamic-programming", "memoization", "recursion", "classic"],
                "complexity": "O(n)",
                "uses_count": 195,
                "helpful_count": 58
            },
            {
                "title": "Valid Parentheses",
                "slug": "valid-parentheses-stack",
                "description": "Check if string has valid matching brackets using stack",
                "category": "strings",
                "language": "python",
                "code": '''def is_valid(s: str) -> bool:
    """
    Check if parentheses are valid and balanced.
    Time: O(n), Space: O(n)
    """
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    
    return len(stack) == 0

# Example usage:
# print(is_valid("()[]{}"))    # True
# print(is_valid("([)]"))      # False
# print(is_valid("{[]}"))      # True''',
                "explanation": "Use a stack to track opening brackets. When we see a closing bracket, check if it matches the most recent opening bracket (top of stack). If it matches, pop and continue. If it doesn't match or stack is empty, string is invalid. At the end, stack should be empty.",
                "tags": ["stack", "strings", "parentheses", "easy", "interview"],
                "complexity": "O(n)",
                "uses_count": 245,
                "helpful_count": 73
            }
        ]
        
        created_count = 0
        for snippet_data in snippets:
            existing = self.db.query(CodeSnippet).filter(
                CodeSnippet.slug == snippet_data["slug"]
            ).first()
            
            if not existing:
                snippet = CodeSnippet(**snippet_data)
                self.db.add(snippet)
                created_count += 1
                print(f"  ✅ Created snippet: {snippet_data['title']}")
            else:
                print(f"  ⏭️  Snippet exists: {snippet_data['title']}")
        
        self.db.commit()
        print(f"  📊 Total: {created_count} new snippets created")
        return created_count
    
    def run(self):
        """Run all seeders"""
        print("=" * 60)
        print("🌱 Forums, Learning Paths & Code Snippets Seeder")
        print("=" * 60)
        
        results = {
            "forum_categories": self.seed_forum_categories(),
            "forum_threads": self.seed_forum_threads(),
            "learning_paths": self.seed_learning_paths(),
            "code_snippets": self.seed_code_snippets()
        }
        
        print("\n" + "=" * 60)
        print("📊 SEEDING COMPLETE!")
        print("=" * 60)
        print(f"  Forum Categories: {results['forum_categories']} created")
        print(f"  Forum Threads: {results['forum_threads']} created")
        print(f"  Learning Paths: {results['learning_paths']} created")
        print(f"  Code Snippets: {results['code_snippets']} created")
        print("=" * 60)
        
        return results


def main():
    """Main entry point"""
    db = SessionLocal()
    try:
        seeder = ForumsPathsSnippetsSeeder(db)
        seeder.run()
    finally:
        db.close()


if __name__ == "__main__":
    main()
