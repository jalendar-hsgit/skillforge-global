"""
Comprehensive Job Application Tracking System Testing
Tests: job applications, status tracking, interviews, offers, salary negotiation
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
# TEST 1: JOB TRACKING DATABASE STRUCTURE
# ============================================================================

def test_job_database_structure():
    """Verify job tracking system tables"""
    print_section("TEST 1: JOB TRACKING DATABASE STRUCTURE")
    
    conn = get_connection()
    if not conn:
        test_result("Database connection", False)
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for job tracking tables
        tables_to_check = [
            'job_application_tracker',
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            test_result(
                f"Table '{table}' exists",
                exists,
                "Job tracking table present" if exists else f"Table '{table}' missing"
            )
        
        # Check job application schema
        cursor.execute("PRAGMA table_info(job_application_tracker)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_cols = [
            'id', 'user_id', 'company_name', 'position_title',
            'status', 'application_date'
        ]
        
        for col in required_cols:
            exists = col in columns
            test_result(
                f"Job column '{col}' exists",
                exists,
                f"Type: {columns.get(col, 'MISSING')}"
            )
        
        # Verify important fields
        test_result(
            "Salary tracking enabled",
            'salary_min' in columns and 'salary_max' in columns,
            "Min/max salary fields present"
        )
        
        test_result(
            "Interview tracking enabled",
            'interviews' in columns,
            "Interviews field (JSON) present"
        )
        
    except Exception as e:
        test_result("Job schema verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 2: JOB APPLICATION INVENTORY
# ============================================================================

def test_job_applications():
    """Verify job application data and statistics"""
    print_section("TEST 2: JOB APPLICATION INVENTORY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get job applications
        cursor.execute("""
            SELECT 
                id,
                company_name,
                position_title,
                status,
                application_date
            FROM job_application_tracker
            ORDER BY application_date DESC
        """)
        
        applications = cursor.fetchall()
        
        test_result(
            "Job applications tracked",
            len(applications) > 0,
            f"Found {len(applications)} applications"
        )
        
        if applications:
            # Display applications
            print_subsection("Recent Applications")
            for app in applications[:10]:
                print(f"    • [{app['status']}] {app['company_name']} - {app['position_title']}")
        
    except Exception as e:
        test_result("Job application verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 3: APPLICATION STATUS TRACKING
# ============================================================================

def test_application_status():
    """Verify application status distribution and workflow"""
    print_section("TEST 3: APPLICATION STATUS TRACKING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get status distribution
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM job_application_tracker
            GROUP BY status
            ORDER BY count DESC
        """)
        
        status_dist = cursor.fetchall()
        
        print_subsection("Application Status Distribution")
        
        total = 0
        for status in status_dist:
            print(f"    {status['status']}: {status['count']}")
            total += status['count']
        
        test_result(
            "Multiple status types tracked",
            len(status_dist) > 0,
            f"{len(status_dist)} different statuses"
        )
        
        # Get status progression
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN status = 'wishlist' THEN 1
                    WHEN status = 'applied' THEN 2
                    WHEN status = 'screening' THEN 3
                    WHEN status = 'interview' THEN 4
                    WHEN status = 'assessment' THEN 5
                    WHEN status = 'offer' THEN 6
                    WHEN status = 'accepted' THEN 7
                    WHEN status = 'rejected' THEN 8
                    WHEN status = 'withdrawn' THEN 9
                END as stage,
                COUNT(*) as count
            FROM job_application_tracker
            GROUP BY status
            ORDER BY stage
        """)
        
        progression = cursor.fetchall()
        
        print_subsection("Application Pipeline")
        if progression:
            pipeline_stages = ['Wishlist', 'Applied', 'Screening', 'Interview', 'Assessment', 'Offer', 'Accepted', 'Rejected', 'Withdrawn']
            for stage in progression:
                if stage['count'] > 0:
                    print(f"    → {stage['count']} applications in this stage")
        
    except Exception as e:
        test_result("Application status verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 4: INTERVIEW TRACKING
# ============================================================================

def test_interview_tracking():
    """Verify interview scheduling and management"""
    print_section("TEST 4: INTERVIEW TRACKING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get applications with interviews
        cursor.execute("""
            SELECT 
                COUNT(*) as total_apps,
                COUNT(CASE WHEN interviews IS NOT NULL AND interviews != '[]' THEN 1 END) as with_interviews
            FROM job_application_tracker
        """)
        
        interview_stats = cursor.fetchone()
        
        test_result(
            "Interview tracking enabled",
            interview_stats['with_interviews'] > 0,
            f"{interview_stats['with_interviews']} applications with interviews"
        )
        
        # Get interview statistics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT company_name) as companies_with_interviews,
                COUNT(DISTINCT user_id) as users_with_interviews
            FROM job_application_tracker
            WHERE interviews IS NOT NULL AND interviews != '[]'
        """)
        
        interview_data = cursor.fetchone()
        
        print_subsection("Interview Statistics")
        print(f"    Companies interviewing: {interview_data['companies_with_interviews']}")
        print(f"    Users with interviews: {interview_data['users_with_interviews']}")
        
        # Get applications by interview type
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN interviews LIKE '%phone%' THEN 1 END) as phone_interviews,
                COUNT(CASE WHEN interviews LIKE '%video%' THEN 1 END) as video_interviews,
                COUNT(CASE WHEN interviews LIKE '%in-person%' OR interviews LIKE '%in person%' THEN 1 END) as in_person_interviews
            FROM job_application_tracker
        """)
        
        interview_types = cursor.fetchone()
        
        print_subsection("Interview Types")
        print(f"    Phone: {interview_types['phone_interviews']}")
        print(f"    Video: {interview_types['video_interviews']}")
        print(f"    In-Person: {interview_types['in_person_interviews']}")
        
    except Exception as e:
        test_result("Interview tracking verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 5: OFFER TRACKING
# ============================================================================

def test_offer_tracking():
    """Verify job offer management"""
    print_section("TEST 5: OFFER TRACKING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get offers
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'offer' THEN 1 END) as pending_offers,
                COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_offers,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_offers
            FROM job_application_tracker
        """)
        
        offer_stats = cursor.fetchone()
        
        print_subsection("Offer Statistics")
        print(f"    Pending Offers: {offer_stats['pending_offers']}")
        print(f"    Accepted: {offer_stats['accepted_offers']}")
        print(f"    Rejected: {offer_stats['rejected_offers']}")
        
        test_result(
            "Offer tracking enabled",
            offer_stats['pending_offers'] > 0 or offer_stats['accepted_offers'] > 0,
            f"{offer_stats['accepted_offers']} offers accepted"
        )
        
    except Exception as e:
        test_result("Offer tracking verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 6: SALARY INFORMATION TRACKING
# ============================================================================

def test_salary_tracking():
    """Verify salary negotiation and tracking"""
    print_section("TEST 6: SALARY INFORMATION TRACKING")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get salary statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_apps,
                COUNT(CASE WHEN salary_min IS NOT NULL THEN 1 END) as with_salary_info,
                AVG(CASE WHEN salary_min IS NOT NULL THEN salary_min END) as avg_min_salary,
                AVG(CASE WHEN salary_max IS NOT NULL THEN salary_max END) as avg_max_salary,
                MIN(salary_min) as lowest_salary,
                MAX(salary_max) as highest_salary
            FROM job_application_tracker
        """)
        
        salary_stats = cursor.fetchone()
        
        test_result(
            "Salary tracking enabled",
            salary_stats['with_salary_info'] > 0,
            f"{salary_stats['with_salary_info']} positions with salary data"
        )
        
        if salary_stats['with_salary_info'] > 0:
            print_subsection("Salary Analysis")
            print(f"    Positions with salary: {salary_stats['with_salary_info']}")
            if salary_stats['avg_min_salary']:
                print(f"    Average min: ${salary_stats['avg_min_salary']:,.0f}")
                print(f"    Average max: ${salary_stats['avg_max_salary']:,.0f}")
            if salary_stats['lowest_salary']:
                print(f"    Range: ${salary_stats['lowest_salary']:,.0f} - ${salary_stats['highest_salary']:,.0f}")
        
    except Exception as e:
        test_result("Salary tracking verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 7: APPLICATION TIMELINE
# ============================================================================

def test_application_timeline():
    """Verify application date tracking and timeline"""
    print_section("TEST 7: APPLICATION TIMELINE")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get application timeline
        cursor.execute("""
            SELECT 
                DATE(application_date) as app_date,
                COUNT(*) as applications
            FROM job_application_tracker
            WHERE application_date IS NOT NULL
            GROUP BY DATE(application_date)
            ORDER BY app_date DESC
            LIMIT 10
        """)
        
        timeline = cursor.fetchall()
        
        print_subsection("Application Timeline (Last 10 Days)")
        for entry in timeline:
            print(f"    {entry['app_date']}: {entry['applications']} applications")
        
        test_result(
            "Application dates tracked",
            len(timeline) > 0,
            f"Applications spanning {len(timeline)} days"
        )
        
        # Get average days in each status
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count,
                AVG(CAST((julianday('now') - julianday(application_date)) AS INTEGER)) as avg_days
            FROM job_application_tracker
            WHERE application_date IS NOT NULL
            GROUP BY status
            ORDER BY avg_days DESC
        """)
        
        status_timeline = cursor.fetchall()
        
        print_subsection("Average Days in Status")
        for st in status_timeline:
            if st['avg_days']:
                print(f"    {st['status']}: {st['avg_days']:.1f} days (n={st['count']})")
        
    except Exception as e:
        test_result("Application timeline verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 8: COMPANY & POSITION DIVERSITY
# ============================================================================

def test_company_diversity():
    """Verify job search diversity across companies"""
    print_section("TEST 8: COMPANY & POSITION DIVERSITY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get top companies being applied to
        cursor.execute("""
            SELECT 
                company_name,
                COUNT(*) as applications,
                COUNT(DISTINCT status) as unique_statuses
            FROM job_application_tracker
            GROUP BY company_name
            ORDER BY applications DESC
            LIMIT 10
        """)
        
        top_companies = cursor.fetchall()
        
        print_subsection("Top Companies")
        for company in top_companies:
            print(f"    {company['company_name']}: {company['applications']} applications")
        
        # Get job type distribution
        cursor.execute("""
            SELECT 
                job_type,
                COUNT(*) as count
            FROM job_application_tracker
            WHERE job_type IS NOT NULL
            GROUP BY job_type
        """)
        
        job_types = cursor.fetchall()
        
        print_subsection("Job Types")
        for jtype in job_types:
            print(f"    {jtype['job_type']}: {jtype['count']}")
        
        test_result(
            "Diverse job search",
            len(top_companies) > 3,
            f"Applied to {len(top_companies)} companies"
        )
        
    except Exception as e:
        test_result("Company diversity verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 9: FOLLOW-UP & REMINDER SYSTEM
# ============================================================================

def test_followup_tracking():
    """Verify follow-up and reminder management"""
    print_section("TEST 9: FOLLOW-UP & REMINDER SYSTEM")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get follow-ups needed
        cursor.execute("""
            SELECT 
                COUNT(*) as total_apps,
                COUNT(CASE WHEN follow_up_date IS NOT NULL THEN 1 END) as with_followups,
                COUNT(CASE WHEN follow_up_date < datetime('now') THEN 1 END) as overdue_followups
            FROM job_application_tracker
        """)
        
        followup_stats = cursor.fetchone()
        
        test_result(
            "Follow-up tracking enabled",
            followup_stats['with_followups'] > 0,
            f"{followup_stats['with_followups']} applications with follow-up dates"
        )
        
        print_subsection("Follow-up Status")
        print(f"    Total with follow-ups: {followup_stats['with_followups']}")
        print(f"    Overdue: {followup_stats['overdue_followups']}")
        
    except Exception as e:
        test_result("Follow-up tracking verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 10: JOB SEARCH ANALYTICS
# ============================================================================

def test_search_analytics():
    """Verify job search analytics and insights"""
    print_section("TEST 10: JOB SEARCH ANALYTICS")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get conversion rates
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applications,
                COUNT(CASE WHEN status = 'applied' THEN 1 END) as applied,
                COUNT(CASE WHEN status = 'screening' THEN 1 END) as screening,
                COUNT(CASE WHEN status = 'interview' THEN 1 END) as interview,
                COUNT(CASE WHEN status = 'offer' THEN 1 END) as offers,
                COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted
            FROM job_application_tracker
        """)
        
        conversion = cursor.fetchone()
        
        print_subsection("Job Search Funnel")
        print(f"    Applications: {conversion['total_applications']}")
        if conversion['applied'] > 0:
            print(f"    → Applied: {conversion['applied']} ({conversion['applied']/conversion['total_applications']*100:.0f}%)")
        if conversion['screening'] > 0:
            print(f"    → Screening: {conversion['screening']} ({conversion['screening']/conversion['applied']*100 if conversion['applied'] > 0 else 0:.0f}%)")
        if conversion['interview'] > 0:
            print(f"    → Interviews: {conversion['interview']}")
        if conversion['offers'] > 0:
            print(f"    → Offers: {conversion['offers']}")
        if conversion['accepted'] > 0:
            print(f"    → Accepted: {conversion['accepted']}")
        
        test_result(
            "Job search metrics tracked",
            conversion['total_applications'] > 0,
            f"{conversion['total_applications']} total applications"
        )
        
    except Exception as e:
        test_result("Search analytics verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 11: DATA INTEGRITY
# ============================================================================

def test_job_data_integrity():
    """Verify job tracking data integrity"""
    print_section("TEST 11: DATA INTEGRITY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Check for orphaned records
        cursor.execute("""
            SELECT COUNT(*) as count FROM job_application_tracker 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        
        orphaned = cursor.fetchone()['count']
        
        test_result(
            "No orphaned job applications",
            orphaned == 0,
            f"Orphaned records: {orphaned}"
        )
        
        # Check for required fields
        cursor.execute("""
            SELECT COUNT(*) as count FROM job_application_tracker 
            WHERE company_name IS NULL OR company_name = ''
            OR position_title IS NULL OR position_title = ''
        """)
        
        invalid = cursor.fetchone()['count']
        
        test_result(
            "All applications have required fields",
            invalid == 0,
            f"Invalid records: {invalid}"
        )
        
        # Check for logical inconsistencies (salary_min > salary_max)
        cursor.execute("""
            SELECT COUNT(*) as count FROM job_application_tracker 
            WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
            AND salary_min > salary_max
        """)
        
        invalid_salary = cursor.fetchone()['count']
        
        test_result(
            "Salary ranges are valid",
            invalid_salary == 0,
            f"Invalid salary ranges: {invalid_salary}"
        )
        
    except Exception as e:
        test_result("Data integrity verification", False, str(e))
    finally:
        conn.close()

# ============================================================================
# TEST 12: SYSTEM SUMMARY
# ============================================================================

def test_system_summary():
    """Overall job tracking system summary"""
    print_section("TEST 12: SYSTEM SUMMARY")
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get comprehensive statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(DISTINCT user_id) FROM job_application_tracker) as job_hunters,
                (SELECT COUNT(*) FROM job_application_tracker) as total_applications,
                (SELECT COUNT(DISTINCT company_name) FROM job_application_tracker) as companies_applied,
                (SELECT COUNT(CASE WHEN status = 'accepted' THEN 1 END) FROM job_application_tracker) as offers_accepted,
                (SELECT COUNT(CASE WHEN interviews IS NOT NULL AND interviews != '[]' THEN 1 END) FROM job_application_tracker) as interviews_scheduled
        """)
        
        stats = cursor.fetchone()
        
        print_subsection("Job Tracking System Overview")
        print(f"    Active Job Hunters: {stats['job_hunters']}")
        print(f"    Total Applications: {stats['total_applications']}")
        print(f"    Companies Applied To: {stats['companies_applied']}")
        print(f"    Interviews Scheduled: {stats['interviews_scheduled']}")
        print(f"    Offers Accepted: {stats['offers_accepted']}")
        
        test_result(
            "Job tracking system operational",
            stats['total_applications'] > 0,
            f"{stats['total_applications']} applications tracked"
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
    print("║" + "SKILLFORGE GLOBAL - JOB TRACKING SYSTEM TESTING".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run all tests
    test_job_database_structure()
    test_job_applications()
    test_application_status()
    test_interview_tracking()
    test_offer_tracking()
    test_salary_tracking()
    test_application_timeline()
    test_company_diversity()
    test_followup_tracking()
    test_search_analytics()
    test_job_data_integrity()
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
        print(f"\n  ✅ ALL TESTS PASSED - JOB TRACKING SYSTEM PRODUCTION READY")
    else:
        print(f"\n  ⚠️  {TEST_RESULTS['failed']} TESTS FAILED - REVIEW REQUIRED")
    
    print("\n")
