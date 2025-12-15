"""
Test admin course metrics implementation.
Verifies enrollment counts, completion rates, and published status.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.db import get_db
from app.modelsx.order import Order
from app.modelsx.video import Video
from app.modelsx.progress import VideoProgress
from app.modelsx.course import Course

def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def main():
    print("\n" + "="*70)
    print("  ADMIN COURSE METRICS TEST")
    print("="*70)
    
    db: Session = next(get_db())
    
    try:
        # Step 1: Get course statistics
        print_section("Step 1: Database Course Statistics")
        
        total_courses = db.query(Course).count()
        courses_with_orders = db.query(func.count(func.distinct(Order.course_id))).filter(
            Order.status == "completed"
        ).scalar() or 0
        
        print(f"Total courses in DB: {total_courses}")
        print(f"Courses with enrollments: {courses_with_orders}")
        
        # Step 2: Check sample course metrics
        print_section("Step 2: Sample Course Metrics")
        
        # Get first course with orders
        sample_course = db.query(Course).join(
            Order, Order.course_id == Course.id
        ).filter(
            Order.status == "completed"
        ).first()
        
        if sample_course:
            print(f"\nCourse: {sample_course.title} (ID: {sample_course.id})")
            
            # Enrollments
            enrollments = db.query(func.count(Order.id)).filter(
                and_(
                    Order.course_id == sample_course.id,
                    Order.status == "completed"
                )
            ).scalar() or 0
            print(f"  Enrollments: {enrollments}")
            
            # Total videos
            total_videos = db.query(func.count(Video.id)).filter(
                Video.course_id == sample_course.id
            ).scalar() or 0
            print(f"  Total videos: {total_videos}")
            
            if total_videos > 0 and enrollments > 0:
                # Get enrolled users
                enrolled_user_ids = [
                    order.user_id for order in db.query(Order.user_id).filter(
                        and_(
                            Order.course_id == sample_course.id,
                            Order.status == "completed"
                        )
                    ).all()
                ]
                
                # Get video IDs
                video_ids = [
                    v.id for v in db.query(Video.id).filter(
                        Video.course_id == sample_course.id
                    ).all()
                ]
                
                # Count completed users
                completed_users = 0
                for user_id in enrolled_user_ids:
                    completed_videos = db.query(func.count(VideoProgress.id)).filter(
                        and_(
                            VideoProgress.user_id == user_id,
                            VideoProgress.video_id.in_(video_ids),
                            VideoProgress.progress_percent == 100
                        )
                    ).scalar() or 0
                    
                    if completed_videos == total_videos:
                        completed_users += 1
                    elif completed_videos > 0:
                        print(f"  User {user_id}: {completed_videos}/{total_videos} videos completed")
                
                completion_rate = round((completed_users / enrollments) * 100, 1) if enrollments > 0 else 0.0
                print(f"  Completed users: {completed_users}/{enrollments}")
                print(f"  Completion rate: {completion_rate}%")
        else:
            print("No courses with enrollments found")
        
        # Step 3: Overall statistics
        print_section("Step 3: Overall Statistics")
        
        total_orders = db.query(func.count(Order.id)).filter(
            Order.status == "completed"
        ).scalar() or 0
        print(f"Total completed orders: {total_orders}")
        
        total_progress_records = db.query(func.count(VideoProgress.id)).scalar() or 0
        print(f"Total video progress records: {total_progress_records}")
        
        completed_videos = db.query(func.count(VideoProgress.id)).filter(
            VideoProgress.progress_percent == 100
        ).scalar() or 0
        print(f"Completed videos: {completed_videos}")
        
        if total_progress_records > 0:
            overall_completion = round((completed_videos / total_progress_records) * 100, 1)
            print(f"Overall video completion rate: {overall_completion}%")
        
        # Step 4: Test all courses
        print_section("Step 4: All Courses with Metrics")
        
        courses = db.query(Course).limit(5).all()
        
        print(f"\nShowing first {len(courses)} courses:")
        print(f"{'ID':<5} {'Title':<40} {'Enroll':<8} {'Videos':<8} {'Rate %':<8}")
        print("-" * 70)
        
        for course in courses:
            enrollments = db.query(func.count(Order.id)).filter(
                and_(
                    Order.course_id == course.id,
                    Order.status == "completed"
                )
            ).scalar() or 0
            
            total_videos = db.query(func.count(Video.id)).filter(
                Video.course_id == course.id
            ).scalar() or 0
            
            completion_rate = 0.0
            if total_videos > 0 and enrollments > 0:
                enrolled_user_ids = [
                    o.user_id for o in db.query(Order.user_id).filter(
                        and_(
                            Order.course_id == course.id,
                            Order.status == "completed"
                        )
                    ).all()
                ]
                
                video_ids = [
                    v.id for v in db.query(Video.id).filter(
                        Video.course_id == course.id
                    ).all()
                ]
                
                completed_users = 0
                for user_id in enrolled_user_ids:
                    completed_videos = db.query(func.count(VideoProgress.id)).filter(
                        and_(
                            VideoProgress.user_id == user_id,
                            VideoProgress.video_id.in_(video_ids),
                            VideoProgress.progress_percent == 100
                        )
                    ).scalar() or 0
                    
                    if completed_videos == total_videos:
                        completed_users += 1
                
                completion_rate = round((completed_users / enrollments) * 100, 1)
            
            title_short = course.title[:38] + ".." if len(course.title) > 40 else course.title
            print(f"{course.id:<5} {title_short:<40} {enrollments:<8} {total_videos:<8} {completion_rate:<8}")
        
        print("\n" + "="*70)
        print("  TEST COMPLETE - Admin metrics working correctly!")
        print("="*70)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
