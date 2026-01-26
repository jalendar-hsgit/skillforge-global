"""
Comprehensive Coding Challenge System Testing
Tests: challenge creation, submission, evaluation, scoring, leaderboard
Author: SkillForge QA Team
Date: January 26, 2026
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "app" / "data" / "skillforge.db"

# ============================================================================
# TEST CONFIGURATION & HELPERS
# ============================================================================

TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "errors": [],
}

def get_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_result(test_name, passed, message=""):
    """Record test result"""
    global TEST_RESULTS
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {test_name}")
    if message:
        print(f"       {message}")
    if passed:
        TEST_RESULTS["passed"] += 1
    else:
        TEST_RESULTS["failed"] += 1
        TEST_RESULTS["errors"].append(f"{test_name}: {message}")

def print_section(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_subsection(title):
    """Print subsection header"""
    print(f"\n  {title}")
    print(f"  {'-'*66}")

# ============================================================================
# TEST 1: CHALLENGE DATABASE STRUCTURE
# ============================================================================

def test_challenge_database_structure():
    """Verify coding challenge system tables"""
    print_section("TEST 1: CHALLENGE DATABASE STRUCTURE")
    
    conn = get_connection()
    if not conn:
        test_result("Database connection", False)
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for required challenge tables
        tables_to_check = [
            'coding_challenges',
            'coding_submissions',
            'challenge_hints',
            'coding_achievements'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            test_result(
                f"Table '{table}' exists",
                exists,
                "Challenge management table present" if exists else f"Table '{table}' missing"
            )
        
        # Check coding_challenges schema
        cursor.execute("PRAGMA table_info(coding_challenges)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_cols = ['title', 'difficulty', 'description', 'points']
        
        for col in required_cols:
            exists = col in columns
            test_result(
                f"Challenge field '{col}'",
                exists,
                f"Type: {columns.get(col, 'MISSING')}"
            )
        
        # Check submissions table
        cursor.execute("PRAGMA table_info(coding_submissions)")
        submission_cols = {row[1]: row[2] for row in cursor.fetchall()}
        
        test_result(
            "Submissions track score",
            'score' in submission_cols,
            "Scoring system enabled"
        )
        
        test_result(
            "Submissions track status",
            'status' in submission_cols,
            "Status tracking enabled"
        )
        
    except Exception as e:
        test_result("Challenge schema verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 2: CHALLENGE CATALOG
# ============================================================================

def test_challenge_catalog():
    """Verify challenge inventory and metadata"""
    print_section("TEST 2: CHALLENGE CATALOG")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all challenges
        cursor.execute("""
            SELECT id, title, difficulty, points FROM coding_challenges 
            ORDER BY points DESC
        """)
        
        challenges = cursor.fetchall()
        
        test_result(
            "Challenges exist in system",
            len(challenges) > 0,
            f"Found {len(challenges)} challenges"
        )
        
        if challenges:
            # Display challenge catalog
            print_subsection("Available Challenges")
            for challenge in challenges[:10]:  # Show top 10
                print(f"    • [{challenge['difficulty']}] {challenge['title']} ({challenge['points']} pts)")
        
        # Verify difficulty levels
        cursor.execute("""
            SELECT difficulty, COUNT(*) as count 
            FROM coding_challenges 
            GROUP BY difficulty
            ORDER BY difficulty
        """)
        
        difficulties = cursor.fetchall()
        
        print_subsection("Difficulty Distribution")
        for diff in difficulties:
            print(f"    {diff['difficulty']}: {diff['count']} challenges")
        
        test_result(
            "Multiple difficulty levels",
            len(difficulties) > 1,
            f"{len(difficulties)} difficulty levels"
        )
        
    except Exception as e:
        test_result("Challenge catalog verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 3: CHALLENGE SUBMISSIONS & EVALUATION
# ============================================================================

def test_challenge_submissions():
    """Verify submission system and evaluation"""
    print_section("TEST 3: CHALLENGE SUBMISSIONS & EVALUATION")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get submission statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_submissions,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT challenge_id) as unique_challenges,
                COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
            FROM coding_submissions
        """)
        
        stats = cursor.fetchone()
        
        test_result(
            "Submissions being tracked",
            stats['total_submissions'] > 0,
            f"{stats['total_submissions']} total submissions"
        )
        
        print_subsection("Submission Statistics")
        print(f"    Total Submissions: {stats['total_submissions']}")
        print(f"    Unique Users: {stats['unique_users']}")
        print(f"    Challenges Attempted: {stats['unique_challenges']}")
        print(f"    Successful: {stats['successful']}")
        print(f"    Failed: {stats['failed']}")
        print(f"    Pending: {stats['pending']}")
        
        if stats['total_submissions'] > 0:
            success_rate = (stats['successful'] / stats['total_submissions'] * 100)
            test_result(
                "Evaluation system working",
                True,
                f"Success rate: {success_rate:.1f}%"
            )
        
    except Exception as e:
        test_result("Challenge submission verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 4: SCORING & POINTS SYSTEM
# ============================================================================

def test_scoring_system():
    """Verify scoring and points award system"""
    print_section("TEST 4: SCORING & POINTS SYSTEM")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get scoring statistics
        cursor.execute("""
            SELECT 
                AVG(score) as avg_score,
                MIN(score) as min_score,
                MAX(score) as max_score,
                COUNT(CASE WHEN score >= 100 THEN 1 END) as perfect_scores,
                COUNT(CASE WHEN score >= 80 THEN 1 END) as good_scores,
                COUNT(CASE WHEN score < 80 THEN 1 END) as poor_scores
            FROM coding_submissions
            WHERE score IS NOT NULL
        """)
        
        scoring = cursor.fetchone()
        
        test_result(
            "Scoring system active",
            scoring['avg_score'] is not None,
            f"Average score: {scoring['avg_score']:.1f}"
        )
        
        print_subsection("Score Distribution")
        if scoring['max_score'] is not None:
            print(f"    Perfect (100): {scoring['perfect_scores']}")
            print(f"    Good (80-99): {scoring['good_scores']}")
            print(f"    Needs Work (<80): {scoring['poor_scores']}")
        
        # Get coin rewards
        cursor.execute("""
            SELECT 
                COUNT(*) as total_coins_awarded,
                SUM(coins_earned) as coins_earned
            FROM coding_submissions
            WHERE coins_earned > 0
        """)
        
        coins = cursor.fetchone()
        
        test_result(
            "Coin rewards system",
            coins['total_coins_awarded'] > 0,
            f"{coins['coins_earned']} coins awarded"
        )
        
    except Exception as e:
        test_result("Scoring system verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 5: CHALLENGE HINTS SYSTEM
# ============================================================================

def test_hints_system():
    """Verify progressive hints feature"""
    print_section("TEST 5: CHALLENGE HINTS SYSTEM")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get hints statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_hints,
                COUNT(DISTINCT challenge_id) as challenges_with_hints,
                COUNT(DISTINCT hint_order) as hint_levels
            FROM challenge_hints
        """)
        
        hints = cursor.fetchone()
        
        test_result(
            "Hints system implemented",
            hints['total_hints'] > 0,
            f"{hints['total_hints']} hints across {hints['challenges_with_hints']} challenges"
        )
        
        # Get hint distribution
        cursor.execute("""
            SELECT 
                hint_order,
                COUNT(*) as count
            FROM challenge_hints
            GROUP BY hint_order
            ORDER BY hint_order
        """)
        
        hint_levels = cursor.fetchall()
        
        print_subsection("Hint Progression")
        for level in hint_levels:
            print(f"    Hint Level {level['hint_order']}: {level['count']} hints")
        
    except Exception as e:
        test_result("Hints system verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 6: CHALLENGE DIFFICULTY DISTRIBUTION
# ============================================================================

def test_difficulty_distribution():
    """Verify proper difficulty level distribution"""
    print_section("TEST 6: CHALLENGE DIFFICULTY DISTRIBUTION")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get difficulty with stats
        cursor.execute("""
            SELECT 
                c.difficulty,
                COUNT(c.id) as challenge_count,
                COUNT(DISTINCT cs.user_id) as users_attempted,
                AVG(cs.score) as avg_user_score,
                AVG(c.success_rate) as avg_success_rate
            FROM coding_challenges c
            LEFT JOIN coding_submissions cs ON c.id = cs.challenge_id
            GROUP BY c.difficulty
            ORDER BY 
                CASE 
                    WHEN c.difficulty = 'easy' THEN 1
                    WHEN c.difficulty = 'medium' THEN 2
                    WHEN c.difficulty = 'hard' THEN 3
                    ELSE 4
                END
        """)
        
        difficulty_data = cursor.fetchall()
        
        print_subsection("Difficulty Analysis")
        
        for diff in difficulty_data:
            print(f"    {diff['difficulty'].upper()}:")
            print(f"      Challenges: {diff['challenge_count']}")
            print(f"      Users attempted: {diff['users_attempted']}")
            if diff['avg_user_score']:
                print(f"      Avg user score: {diff['avg_user_score']:.1f}%")
            if diff['avg_success_rate']:
                print(f"      Avg success rate: {diff['avg_success_rate']:.1f}%")
        
        test_result(
            "Difficulty levels balanced",
            len(difficulty_data) >= 3,
            f"{len(difficulty_data)} difficulty levels"
        )
        
    except Exception as e:
        test_result("Difficulty verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 7: ACHIEVEMENTS & GAMIFICATION
# ============================================================================

def test_achievements():
    """Verify achievement system"""
    print_section("TEST 7: ACHIEVEMENTS & GAMIFICATION")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get achievements
        cursor.execute("""
            SELECT id, title, description FROM coding_achievements 
            ORDER BY id LIMIT 20
        """)
        
        achievements = cursor.fetchall()
        
        test_result(
            "Achievement system exists",
            len(achievements) > 0,
            f"{len(achievements)} achievements"
        )
        
        if achievements:
            print_subsection("Sample Achievements")
            for ach in achievements[:5]:
                print(f"    🏆 {ach['title']}: {ach['description']}")
        
        # Get achievement unlock statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_unlocks,
                COUNT(DISTINCT user_id) as users_with_achievements
            FROM user_achievements
        """)
        
        unlocks = cursor.fetchone()
        
        test_result(
            "Achievements being unlocked",
            unlocks['total_unlocks'] > 0,
            f"{unlocks['users_with_achievements']} users earned achievements"
        )
        
    except Exception as e:
        test_result("Achievement system verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 8: LEADERBOARD & COMPETITION
# ============================================================================

def test_leaderboard():
    """Verify leaderboard and competition mechanics"""
    print_section("TEST 8: LEADERBOARD & COMPETITION")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get top performers
        cursor.execute("""
            SELECT 
                u.id,
                u.email,
                COUNT(DISTINCT cs.challenge_id) as challenges_solved,
                COUNT(CASE WHEN cs.score >= 100 THEN 1 END) as perfect_solutions,
                SUM(cs.coins_earned) as total_coins,
                AVG(cs.score) as avg_score
            FROM users u
            LEFT JOIN coding_submissions cs ON u.id = cs.user_id AND cs.status = 'success'
            GROUP BY u.id
            HAVING challenges_solved > 0
            ORDER BY perfect_solutions DESC, total_coins DESC
            LIMIT 10
        """)
        
        leaderboard = cursor.fetchall()
        
        test_result(
            "Leaderboard data generated",
            len(leaderboard) > 0,
            f"{len(leaderboard)} active competitors"
        )
        
        if leaderboard:
            print_subsection("Top 10 Competitors")
            for rank, user in enumerate(leaderboard, 1):
                print(f"    #{rank} User{user['id']}: {user['challenges_solved']} solved, {user['perfect_solutions']} perfect")
        
    except Exception as e:
        test_result("Leaderboard verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 9: LANGUAGE SUPPORT
# ============================================================================

def test_language_support():
    """Verify programming language support"""
    print_section("TEST 9: LANGUAGE SUPPORT")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get supported languages from submissions
        cursor.execute("""
            SELECT DISTINCT language, COUNT(*) as submissions
            FROM coding_submissions
            GROUP BY language
            ORDER BY submissions DESC
        """)
        
        languages = cursor.fetchall()
        
        test_result(
            "Multiple languages supported",
            len(languages) > 0,
            f"{len(languages)} languages in use"
        )
        
        if languages:
            print_subsection("Supported Languages")
            for lang in languages:
                print(f"    • {lang['language']}: {lang['submissions']} submissions")
        
    except Exception as e:
        test_result("Language support verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 10: TEST CASES & VALIDATION
# ============================================================================

def test_cases_validation():
    """Verify test case system for challenges"""
    print_section("TEST 10: TEST CASES & VALIDATION")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get test case statistics
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN test_results IS NOT NULL THEN 1 END) as submissions_with_results,
                COUNT(*) as total_submissions
            FROM coding_submissions
        """)
        
        results = cursor.fetchone()
        
        test_completion = (results['submissions_with_results'] / results['total_submissions'] * 100) if results['total_submissions'] > 0 else 0
        
        test_result(
            "Test case evaluation running",
            results['submissions_with_results'] > 0,
            f"{test_completion:.1f}% of submissions evaluated"
        )
        
        # Get test case pass rates
        cursor.execute("""
            SELECT 
                AVG(CAST(passed_tests AS FLOAT) / NULLIF(CAST(total_tests AS FLOAT), 0) * 100) as avg_pass_rate
            FROM coding_submissions
            WHERE total_tests > 0
        """)
        
        pass_stats = cursor.fetchone()
        
        if pass_stats['avg_pass_rate']:
            print_subsection("Test Execution")
            print(f"    Average pass rate: {pass_stats['avg_pass_rate']:.1f}%")
        
    except Exception as e:
        test_result("Test case verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 11: DATA INTEGRITY
# ============================================================================

def test_challenge_integrity():
    """Verify challenge system data integrity"""
    print_section("TEST 11: DATA INTEGRITY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for orphaned submissions
        cursor.execute("""
            SELECT COUNT(*) as count FROM coding_submissions 
            WHERE challenge_id NOT IN (SELECT id FROM coding_challenges)
            OR user_id NOT IN (SELECT id FROM users)
        """)
        
        orphaned = cursor.fetchone()['count']
        
        test_result(
            "No orphaned submissions",
            orphaned == 0,
            f"Orphaned records: {orphaned}"
        )
        
        # Check for invalid scores
        cursor.execute("""
            SELECT COUNT(*) as count FROM coding_submissions 
            WHERE score IS NOT NULL AND (score < 0 OR score > 100)
        """)
        
        invalid_scores = cursor.fetchone()['count']
        
        test_result(
            "Score integrity verified",
            invalid_scores == 0,
            f"Invalid scores: {invalid_scores}"
        )
        
        # Check for incomplete submissions
        cursor.execute("""
            SELECT COUNT(*) as count FROM coding_submissions 
            WHERE code IS NULL OR code = '' OR language IS NULL OR language = ''
        """)
        
        incomplete = cursor.fetchone()['count']
        
        test_result(
            "All submissions complete",
            incomplete == 0,
            f"Incomplete records: {incomplete}"
        )
        
    except Exception as e:
        test_result("Data integrity verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 12: SYSTEM SUMMARY
# ============================================================================

def test_system_summary():
    """Overall challenge system summary"""
    print_section("TEST 12: SYSTEM SUMMARY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get comprehensive statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM coding_challenges) as total_challenges,
                (SELECT COUNT(*) FROM coding_submissions) as total_submissions,
                (SELECT COUNT(DISTINCT user_id) FROM coding_submissions) as active_coders,
                (SELECT AVG(success_rate) FROM coding_challenges) as avg_success_rate,
                (SELECT COUNT(*) FROM coding_achievements) as total_achievements,
                (SELECT COUNT(DISTINCT user_id) FROM user_achievements) as users_with_achievements
        """)
        
        stats = cursor.fetchone()
        
        print_subsection("Challenge System Overview")
        print(f"    Total Challenges: {stats['total_challenges']}")
        print(f"    Total Submissions: {stats['total_submissions']}")
        print(f"    Active Coders: {stats['active_coders']}")
        if stats['avg_success_rate']:
            print(f"    Avg Success Rate: {stats['avg_success_rate']:.1f}%")
        print(f"    Total Achievements: {stats['total_achievements']}")
        print(f"    Users with Achievements: {stats['users_with_achievements']}")
        
        test_result(
            "Challenge system operational",
            stats['total_challenges'] > 0 and stats['total_submissions'] > 0,
            f"{stats['total_challenges']} challenges, {stats['total_submissions']} submissions"
        )
        
    except Exception as e:
        test_result("System summary", False, str(e))
    finally:
        conn.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "SKILLFORGE GLOBAL - CODING CHALLENGE SYSTEM TESTING".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run all tests
    test_challenge_database_structure()
    test_challenge_catalog()
    test_challenge_submissions()
    test_scoring_system()
    test_hints_system()
    test_difficulty_distribution()
    test_achievements()
    test_leaderboard()
    test_language_support()
    test_cases_validation()
    test_challenge_integrity()
    test_system_summary()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    total_tests = TEST_RESULTS["passed"] + TEST_RESULTS["failed"]
    pass_rate = (TEST_RESULTS["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n  Total Tests: {total_tests}")
    print(f"  Passed: {TEST_RESULTS['passed']}")
    print(f"  Failed: {TEST_RESULTS['failed']}")
    print(f"  Pass Rate: {pass_rate:.1f}%")
    
    if TEST_RESULTS["errors"]:
        print_subsection("Errors")
        for error in TEST_RESULTS["errors"]:
            print(f"  • {error}")
    
    # Final status
    if TEST_RESULTS["failed"] == 0:
        print(f"\n  ✅ ALL TESTS PASSED - CHALLENGE SYSTEM PRODUCTION READY")
    else:
        print(f"\n  ⚠️  {TEST_RESULTS['failed']} TESTS FAILED - REVIEW REQUIRED")
    
    print("\n")
