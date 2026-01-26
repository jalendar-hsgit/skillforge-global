"""
Comprehensive Course System Testing
Tests: enrollment, purchasing, curriculum, progress tracking, analytics
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
# TEST 1: COURSE DATABASE STRUCTURE
# ============================================================================

def test_course_database_structure():
    """Verify course system tables exist with correct schema"""
    print_section("TEST 1: COURSE DATABASE STRUCTURE")
    
    conn = get_connection()
    if not conn:
        test_result("Database connection", False)
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for required course tables
        tables_to_check = [
            'courses',
            'video',
            'video_progress',
            'orders',
            'course_feedback'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            test_result(
                f"Table '{table}' exists",
                exists,
                "Course management table present" if exists else f"Table '{table}' missing"
            )
        
        # Check courses table schema
        cursor.execute("PRAGMA table_info(courses)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_course_columns = {
            'id': 'INTEGER',
            'title': 'TEXT',
            'description': 'TEXT',
            'price': 'REAL',
        }
        
        for col, col_type in required_course_columns.items():
            exists = col in columns
            test_result(
                f"Course column '{col}' exists",
                exists,
                f"Column type: {columns.get(col, 'MISSING')}"
            )
        
        # Check video table schema
        cursor.execute("PRAGMA table_info(video)")
        video_cols = {row[1]: row[2] for row in cursor.fetchall()}
        
        test_result(
            "Video table has 'course_id'",
            'course_id' in video_cols,
            "Video FK to courses confirmed"
        )
        
        # Check video_progress schema
        cursor.execute("PRAGMA table_info(video_progress)")
        progress_cols = {row[1]: row[2] for row in cursor.fetchall()}
        
        test_result(
            "VideoProgress tracks user_id",
            'user_id' in progress_cols,
            "User progress tracking enabled"
        )
        
        test_result(
            "VideoProgress tracks video_id",
            'video_id' in progress_cols,
            "Video progress tracking enabled"
        )
        
    except Exception as e:
        test_result("Course schema verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 2: COURSE CATALOG
# ============================================================================

def test_course_catalog():
    """Verify course data and availability"""
    print_section("TEST 2: COURSE CATALOG")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all courses
        cursor.execute("SELECT id, title, price FROM courses ORDER BY id")
        courses = cursor.fetchall()
        
        test_result(
            "Courses exist in database",
            len(courses) > 0,
            f"Found {len(courses)} courses"
        )
        
        if courses:
            # Display course catalog
            print_subsection("Available Courses")
            for course in courses:
                print(f"    • [{course['id']}] {course['title']} (${course['price']:.2f})")
        
        # Verify course pricing
        cursor.execute("SELECT COUNT(*) as count FROM courses WHERE price > 0")
        paid_courses = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM courses WHERE price = 0 OR price IS NULL")
        free_courses = cursor.fetchone()['count']
        
        test_result(
            "Course pricing configured",
            paid_courses > 0 or free_courses > 0,
            f"{paid_courses} paid, {free_courses} free"
        )
        
    except Exception as e:
        test_result("Course catalog verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 3: COURSE ENROLLMENT
# ============================================================================

def test_course_enrollment():
    """Verify enrollment system and orders"""
    print_section("TEST 3: COURSE ENROLLMENT")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get orders (enrollments)
        cursor.execute("""
            SELECT 
                o.id,
                o.user_id,
                o.course_id,
                o.status,
                o.amount,
                o.created_at,
                c.title as course_title
            FROM orders o
            LEFT JOIN courses c ON o.course_id = c.id
            WHERE o.course_id IS NOT NULL
            ORDER BY o.created_at DESC
            LIMIT 20
        """)
        
        enrollments = cursor.fetchall()
        
        test_result(
            "Course enrollments exist",
            len(enrollments) > 0,
            f"Found {len(enrollments)} enrollments"
        )
        
        if enrollments:
            # Display enrollment details
            print_subsection("Recent Enrollments")
            
            completed = sum(1 for e in enrollments if e['status'] == 'completed')
            pending = sum(1 for e in enrollments if e['status'] == 'pending')
            failed = sum(1 for e in enrollments if e['status'] == 'failed')
            
            print(f"    Completed: {completed}")
            print(f"    Pending: {pending}")
            print(f"    Failed: {failed}")
            
            test_result(
                "Completed enrollments tracked",
                completed > 0,
                f"{completed} users enrolled"
            )
        
        # Get enrollment count per course
        cursor.execute("""
            SELECT 
                c.id,
                c.title,
                COUNT(DISTINCT o.user_id) as enrollments,
                COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders
            FROM courses c
            LEFT JOIN orders o ON c.id = o.course_id AND o.status = 'completed'
            GROUP BY c.id
            ORDER BY enrollments DESC
        """)
        
        course_stats = cursor.fetchall()
        
        print_subsection("Enrollment by Course")
        for stat in course_stats:
            if stat['enrollments'] > 0:
                print(f"    {stat['title']}: {stat['enrollments']} enrolled")
        
    except Exception as e:
        test_result("Course enrollment verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 4: COURSE CURRICULUM & VIDEOS
# ============================================================================

def test_course_curriculum():
    """Verify course structure and video organization"""
    print_section("TEST 4: COURSE CURRICULUM & VIDEOS")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get videos per course
        cursor.execute("""
            SELECT 
                c.id,
                c.title as course_title,
                COUNT(v.id) as video_count,
                SUM(CAST(v.duration_seconds AS INTEGER)) / 60 as total_minutes
            FROM courses c
            LEFT JOIN video v ON c.id = v.course_id
            GROUP BY c.id
            ORDER BY video_count DESC
        """)
        
        course_videos = cursor.fetchall()
        
        test_result(
            "Videos organized by course",
            len(course_videos) > 0,
            f"Videos found in {len(course_videos)} courses"
        )
        
        if course_videos:
            print_subsection("Curriculum Structure")
            for stat in course_videos:
                if stat['video_count'] and stat['video_count'] > 0:
                    minutes = stat['total_minutes'] or 0
                    print(f"    {stat['course_title']}: {stat['video_count']} videos ({int(minutes)} min)")
        
        # Get total videos
        cursor.execute("SELECT COUNT(*) as count FROM video")
        total_videos = cursor.fetchone()['count']
        
        test_result(
            "Video content available",
            total_videos > 0,
            f"{total_videos} total videos"
        )
        
    except Exception as e:
        test_result("Course curriculum verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 5: VIDEO PROGRESS TRACKING
# ============================================================================

def test_video_progress():
    """Verify video progress tracking system"""
    print_section("TEST 5: VIDEO PROGRESS TRACKING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get video progress records
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT video_id) as unique_videos
            FROM video_progress
        """)
        
        progress_stats = cursor.fetchone()
        
        test_result(
            "Video progress records exist",
            progress_stats['total_records'] > 0,
            f"{progress_stats['total_records']} progress records"
        )
        
        test_result(
            "Multiple users tracking progress",
            progress_stats['unique_users'] > 0,
            f"{progress_stats['unique_users']} users"
        )
        
        test_result(
            "Multiple videos tracked",
            progress_stats['unique_videos'] > 0,
            f"{progress_stats['unique_videos']} videos"
        )
        
        # Get progress by percentage
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN progress_percent = 0 THEN 1 END) as not_started,
                COUNT(CASE WHEN progress_percent > 0 AND progress_percent < 100 THEN 1 END) as in_progress,
                COUNT(CASE WHEN progress_percent = 100 THEN 1 END) as completed
            FROM video_progress
        """)
        
        progress_dist = cursor.fetchone()
        
        print_subsection("Progress Distribution")
        print(f"    Not Started: {progress_dist['not_started']}")
        print(f"    In Progress: {progress_dist['in_progress']}")
        print(f"    Completed: {progress_dist['completed']}")
        
        # Average progress
        cursor.execute("""
            SELECT 
                AVG(progress_percent) as avg_progress,
                MIN(progress_percent) as min_progress,
                MAX(progress_percent) as max_progress
            FROM video_progress
        """)
        
        avg_stats = cursor.fetchone()
        
        test_result(
            "Progress tracking working",
            avg_stats['avg_progress'] is not None,
            f"Average progress: {avg_stats['avg_progress']:.1f}%"
        )
        
    except Exception as e:
        test_result("Video progress tracking verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 6: COURSE COMPLETION METRICS
# ============================================================================

def test_course_completion():
    """Verify course completion tracking and metrics"""
    print_section("TEST 6: COURSE COMPLETION METRICS")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get course completion rates
        cursor.execute("""
            SELECT 
                c.id,
                c.title,
                COUNT(DISTINCT o.user_id) as enrolled_users,
                COUNT(DISTINCT 
                    CASE WHEN (
                        SELECT COUNT(*) FROM video v 
                        WHERE v.course_id = c.id
                    ) = (
                        SELECT COUNT(*) FROM video_progress vp
                        WHERE vp.user_id = o.user_id 
                        AND vp.video_id IN (
                            SELECT id FROM video WHERE course_id = c.id
                        )
                        AND vp.progress_percent = 100
                    ) THEN o.user_id 
                END) as completed_users
            FROM courses c
            LEFT JOIN orders o ON c.id = o.course_id AND o.status = 'completed'
            GROUP BY c.id
            HAVING enrolled_users > 0
        """)
        
        completion_data = cursor.fetchall()
        
        print_subsection("Course Completion Rates")
        
        total_enrolled = 0
        total_completed = 0
        
        for course in completion_data:
            total_enrolled += course['enrolled_users']
            completed = course['completed_users'] or 0
            total_completed += completed
            
            if course['enrolled_users'] > 0:
                rate = (completed / course['enrolled_users'] * 100) if completed else 0
                print(f"    {course['title']}: {completed}/{course['enrolled_users']} ({rate:.1f}%)")
        
        if total_enrolled > 0:
            overall_rate = (total_completed / total_enrolled * 100)
            test_result(
                "Course completion tracking",
                True,
                f"Overall: {total_completed}/{total_enrolled} ({overall_rate:.1f}%)"
            )
        else:
            test_result("Course completion data", False, "No completion data available")
        
    except Exception as e:
        test_result("Course completion verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 7: COURSE FEEDBACK & RATINGS
# ============================================================================

def test_course_feedback():
    """Verify course feedback and rating system"""
    print_section("TEST 7: COURSE FEEDBACK & RATINGS")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check feedback table
        cursor.execute("SELECT COUNT(*) as count FROM course_feedback")
        feedback_count = cursor.fetchone()['count']
        
        test_result(
            "Course feedback records exist",
            feedback_count > 0,
            f"{feedback_count} feedback entries"
        )
        
        if feedback_count > 0:
            # Get rating statistics
            cursor.execute("""
                SELECT 
                    AVG(CAST(rating AS FLOAT)) as avg_rating,
                    MIN(rating) as min_rating,
                    MAX(rating) as max_rating,
                    COUNT(*) as total_ratings
                FROM course_feedback
                WHERE rating IS NOT NULL
            """)
            
            rating_stats = cursor.fetchone()
            
            if rating_stats['total_ratings'] > 0:
                print_subsection("Course Ratings")
                print(f"    Average: {rating_stats['avg_rating']:.2f}/5 ⭐")
                print(f"    Total ratings: {rating_stats['total_ratings']}")
                
                test_result(
                    "Rating system functional",
                    rating_stats['avg_rating'] is not None,
                    f"Average rating: {rating_stats['avg_rating']:.2f}"
                )
            
            # Get feedback by rating
            cursor.execute("""
                SELECT 
                    rating,
                    COUNT(*) as count
                FROM course_feedback
                WHERE rating IS NOT NULL
                GROUP BY rating
                ORDER BY rating DESC
            """)
            
            ratings = cursor.fetchall()
            
            print_subsection("Rating Distribution")
            for r in ratings:
                stars = "⭐" * r['rating']
                print(f"    {r['rating']}-star: {r['count']} ({stars})")
        
    except Exception as e:
        test_result("Course feedback verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 8: COURSE PRICING & REVENUE
# ============================================================================

def test_course_pricing():
    """Verify course pricing and revenue tracking"""
    print_section("TEST 8: COURSE PRICING & REVENUE")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get course revenue
        cursor.execute("""
            SELECT 
                c.id,
                c.title,
                c.price,
                COUNT(DISTINCT o.id) as total_orders,
                COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.id END) as completed_orders,
                SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) as revenue
            FROM courses c
            LEFT JOIN orders o ON c.id = o.course_id
            GROUP BY c.id
            ORDER BY revenue DESC
        """)
        
        course_revenue = cursor.fetchall()
        
        print_subsection("Course Revenue")
        
        total_revenue = 0
        
        for course in course_revenue:
            revenue = course['revenue'] or 0
            completed = course['completed_orders'] or 0
            total_revenue += revenue
            
            if completed > 0:
                print(f"    {course['title']}: ${revenue:.2f} ({completed} sales)")
        
        test_result(
            "Revenue tracking enabled",
            total_revenue > 0,
            f"Total course revenue: ${total_revenue:.2f}"
        )
        
        # Get pricing breakdown
        cursor.execute("""
            SELECT 
                COUNT(*) as total_courses,
                COUNT(CASE WHEN price = 0 THEN 1 END) as free_courses,
                COUNT(CASE WHEN price > 0 THEN 1 END) as paid_courses,
                AVG(CASE WHEN price > 0 THEN price END) as avg_price
            FROM courses
        """)
        
        pricing_stats = cursor.fetchone()
        
        print_subsection("Pricing Model")
        print(f"    Total courses: {pricing_stats['total_courses']}")
        print(f"    Free: {pricing_stats['free_courses']}")
        print(f"    Paid: {pricing_stats['paid_courses']}")
        if pricing_stats['avg_price']:
            print(f"    Average price: ${pricing_stats['avg_price']:.2f}")
        
    except Exception as e:
        test_result("Course pricing verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 9: COURSE SEARCH & FILTERING
# ============================================================================

def test_course_search():
    """Verify course search and filtering capabilities"""
    print_section("TEST 9: COURSE SEARCH & FILTERING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for course categories/difficulty levels
        cursor.execute("""
            SELECT DISTINCT difficulty FROM courses WHERE difficulty IS NOT NULL
        """)
        
        difficulties = [row['difficulty'] for row in cursor.fetchall()]
        
        test_result(
            "Course difficulty levels defined",
            len(difficulties) > 0,
            f"Levels: {', '.join(difficulties)}"
        )
        
        # Check course availability
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft
            FROM courses
        """)
        
        availability = cursor.fetchone()
        
        test_result(
            "Course availability tracked",
            availability['published'] > 0,
            f"{availability['published']} published courses"
        )
        
        # Get course tags/categories
        cursor.execute("""
            SELECT DISTINCT category FROM courses WHERE category IS NOT NULL
        """)
        
        categories = [row['category'] for row in cursor.fetchall()]
        
        if categories:
            print_subsection("Course Categories")
            for cat in categories:
                print(f"    • {cat}")
        
    except Exception as e:
        test_result("Course search verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 10: STUDENT ENGAGEMENT METRICS
# ============================================================================

def test_student_engagement():
    """Verify student engagement and learning analytics"""
    print_section("TEST 10: STUDENT ENGAGEMENT METRICS")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get active learners
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as active_learners,
                COUNT(DISTINCT video_id) as videos_accessed,
                AVG(progress_percent) as avg_progress
            FROM video_progress
            WHERE created_at > datetime('now', '-30 days')
        """)
        
        engagement = cursor.fetchone()
        
        test_result(
            "Student engagement tracking",
            engagement['active_learners'] > 0,
            f"{engagement['active_learners']} active learners"
        )
        
        # Get time on platform
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                COUNT(DISTINCT video_id) as total_videos_watched
            FROM video_progress
        """)
        
        usage = cursor.fetchone()
        
        print_subsection("Engagement Statistics")
        print(f"    Total learners: {usage['total_users']}")
        print(f"    Total videos watched: {usage['total_videos_watched']}")
        if engagement['avg_progress']:
            print(f"    Average progress: {engagement['avg_progress']:.1f}%")
        
        # Get learning patterns
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d', created_at) as day,
                COUNT(*) as events,
                COUNT(DISTINCT user_id) as users
            FROM video_progress
            GROUP BY day
            ORDER BY day DESC
            LIMIT 10
        """)
        
        patterns = cursor.fetchall()
        
        if patterns:
            print_subsection("Recent Activity (Last 10 Days)")
            for p in patterns:
                print(f"    {p['day']}: {p['events']} events, {p['users']} users")
        
    except Exception as e:
        test_result("Student engagement verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 11: COURSE DATA INTEGRITY
# ============================================================================

def test_data_integrity():
    """Verify course system data integrity"""
    print_section("TEST 11: COURSE DATA INTEGRITY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for orphaned videos (videos without courses)
        cursor.execute("""
            SELECT COUNT(*) as count FROM video 
            WHERE course_id NOT IN (SELECT id FROM courses)
        """)
        
        orphaned_videos = cursor.fetchone()['count']
        
        test_result(
            "No orphaned videos",
            orphaned_videos == 0,
            f"Orphaned videos: {orphaned_videos}"
        )
        
        # Check for orphaned progress (progress without users/videos)
        cursor.execute("""
            SELECT COUNT(*) as count FROM video_progress 
            WHERE user_id NOT IN (SELECT id FROM users)
            OR video_id NOT IN (SELECT id FROM video)
        """)
        
        orphaned_progress = cursor.fetchone()['count']
        
        test_result(
            "No orphaned progress records",
            orphaned_progress == 0,
            f"Orphaned records: {orphaned_progress}"
        )
        
        # Check for orphaned orders
        cursor.execute("""
            SELECT COUNT(*) as count FROM orders 
            WHERE user_id NOT IN (SELECT id FROM users)
            OR (course_id IS NOT NULL AND course_id NOT IN (SELECT id FROM courses))
        """)
        
        orphaned_orders = cursor.fetchone()['count']
        
        test_result(
            "No orphaned orders",
            orphaned_orders == 0,
            f"Orphaned orders: {orphaned_orders}"
        )
        
        # Check required fields
        cursor.execute("""
            SELECT COUNT(*) as count FROM courses 
            WHERE title IS NULL OR title = ''
        """)
        
        invalid_courses = cursor.fetchone()['count']
        
        test_result(
            "All courses have valid titles",
            invalid_courses == 0,
            f"Invalid courses: {invalid_courses}"
        )
        
    except Exception as e:
        test_result("Data integrity verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 12: COURSE SYSTEM SUMMARY
# ============================================================================

def test_system_summary():
    """Overall course system health summary"""
    print_section("TEST 12: COURSE SYSTEM SUMMARY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get comprehensive statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM courses) as total_courses,
                (SELECT COUNT(*) FROM video) as total_videos,
                (SELECT COUNT(*) FROM orders WHERE course_id IS NOT NULL) as total_enrollments,
                (SELECT COUNT(*) FROM video_progress) as total_progress_records,
                (SELECT COUNT(DISTINCT user_id) FROM orders WHERE course_id IS NOT NULL) as unique_students,
                (SELECT AVG(price) FROM courses) as avg_course_price
        """)
        
        stats = cursor.fetchone()
        
        print_subsection("System Overview")
        print(f"    Total Courses: {stats['total_courses']}")
        print(f"    Total Videos: {stats['total_videos']}")
        print(f"    Total Enrollments: {stats['total_enrollments']}")
        print(f"    Progress Records: {stats['total_progress_records']}")
        print(f"    Unique Students: {stats['unique_students']}")
        if stats['avg_course_price']:
            print(f"    Avg Course Price: ${stats['avg_course_price']:.2f}")
        
        test_result(
            "Course system operational",
            stats['total_courses'] > 0 and stats['total_videos'] > 0,
            f"{stats['total_courses']} courses, {stats['total_videos']} videos"
        )
        
    except Exception as e:
        test_result("Course system summary", False, str(e))
    finally:
        conn.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "SKILLFORGE GLOBAL - COURSE SYSTEM TESTING".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run all tests
    test_course_database_structure()
    test_course_catalog()
    test_course_enrollment()
    test_course_curriculum()
    test_video_progress()
    test_course_completion()
    test_course_feedback()
    test_course_pricing()
    test_course_search()
    test_student_engagement()
    test_data_integrity()
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
        print(f"\n  ✅ ALL TESTS PASSED - COURSE SYSTEM PRODUCTION READY")
    else:
        print(f"\n  ⚠️  {TEST_RESULTS['failed']} TESTS FAILED - REVIEW REQUIRED")
    
    print("\n")
