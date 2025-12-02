"""
Script to check database statistics and identify data gaps
"""
import asyncio
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.models.database import (
    User, Student, Tutor, Coordinator,
    Session, SessionFeedback, SessionParticipant,
    Subject, ProgressTracking, LearningAchievements,
    Forum, ForumPost, ForumMember,
    Notifications, TutorRegistration,
    StudyGroup, StudyGroupMember
)

async def check_database():
    print("\n" + "="*80)
    print("DATABASE STATISTICS REPORT")
    print("="*80 + "\n")
    
    async for db in get_db():
        # Users & Profiles
        print("📊 USERS & PROFILES")
        print("-" * 80)
        total_users = await db.scalar(select(func.count(User.user_id)))
        students_count = await db.scalar(select(func.count(Student.student_id)))
        tutors_count = await db.scalar(select(func.count(Tutor.tutor_id)))
        coordinators_count = await db.scalar(select(func.count(Coordinator.coordinator_id)))
        
        print(f"Total Users: {total_users}")
        print(f"  - Students: {students_count}")
        print(f"  - Tutors: {tutors_count}")
        print(f"  - Coordinators: {coordinators_count}")
        print(f"  - Missing profiles: {total_users - students_count - tutors_count - coordinators_count}")
        
        # Sessions
        print("\n📚 SESSIONS")
        print("-" * 80)
        total_sessions = await db.scalar(select(func.count(Session.session_id)))
        pending_sessions = await db.scalar(
            select(func.count(Session.session_id)).where(Session.status == 'pending')
        )
        scheduled_sessions = await db.scalar(
            select(func.count(Session.session_id)).where(Session.status == 'scheduled')
        )
        completed_sessions = await db.scalar(
            select(func.count(Session.session_id)).where(Session.status == 'completed')
        )
        cancelled_sessions = await db.scalar(
            select(func.count(Session.session_id)).where(Session.status == 'cancelled')
        )
        
        print(f"Total Sessions: {total_sessions}")
        print(f"  - Pending: {pending_sessions}")
        print(f"  - Scheduled: {scheduled_sessions}")
        print(f"  - Completed: {completed_sessions}")
        print(f"  - Cancelled: {cancelled_sessions}")
        
        if total_sessions > 0:
            print(f"  - Completion Rate: {(completed_sessions / total_sessions * 100):.1f}%")
        
        # Session Feedback
        feedback_count = await db.scalar(select(func.count(SessionFeedback.feedback_id)))
        print(f"\nSession Feedback: {feedback_count} / {completed_sessions} completed sessions")
        if completed_sessions > 0:
            print(f"  - Feedback Coverage: {(feedback_count / completed_sessions * 100):.1f}%")
        
        if feedback_count > 0:
            avg_rating = await db.scalar(select(func.avg(SessionFeedback.rating)))
            print(f"  - Average Rating: {avg_rating:.2f}/5")
        
        # Subjects
        print("\n📖 SUBJECTS")
        print("-" * 80)
        total_subjects = await db.scalar(select(func.count(Subject.subject_id)))
        subjects_with_sessions = await db.scalar(
            select(func.count(func.distinct(Session.subject_id))).where(Session.subject_id.isnot(None))
        )
        print(f"Total Subjects: {total_subjects}")
        print(f"Subjects with Sessions: {subjects_with_sessions}")
        print(f"Unused Subjects: {total_subjects - subjects_with_sessions}")
        
        # Progress Tracking
        print("\n📈 PROGRESS TRACKING")
        print("-" * 80)
        total_progress = await db.scalar(select(func.count(ProgressTracking.progress_id)))
        students_with_progress = await db.scalar(
            select(func.count(func.distinct(ProgressTracking.student_id)))
        )
        print(f"Total Progress Entries: {total_progress}")
        print(f"Students with Progress: {students_with_progress} / {students_count}")
        if students_count > 0:
            print(f"  - Coverage: {(students_with_progress / students_count * 100):.1f}%")
        
        if total_progress > 0:
            avg_understanding = await db.scalar(select(func.avg(ProgressTracking.understanding_level)))
            print(f"  - Average Understanding Level: {avg_understanding:.2f}/5")
        
        # Learning Achievements
        achievements_count = await db.scalar(select(func.count(LearningAchievements.achievement_id)))
        print(f"\nLearning Achievements: {achievements_count}")
        
        # Forum
        print("\n💬 FORUM")
        print("-" * 80)
        total_forums = await db.scalar(select(func.count(Forum.forum_id)))
        total_posts = await db.scalar(select(func.count(ForumPost.post_id)))
        top_level_posts = await db.scalar(
            select(func.count(ForumPost.post_id)).where(ForumPost.parent_post_id.is_(None))
        )
        replies = total_posts - top_level_posts
        
        print(f"Total Forums: {total_forums}")
        print(f"Total Posts: {total_posts}")
        print(f"  - Top-level Threads: {top_level_posts}")
        print(f"  - Replies: {replies}")
        
        if total_posts > 0:
            total_upvotes = await db.scalar(select(func.sum(ForumPost.upvote_count)))
            print(f"  - Total Upvotes: {total_upvotes or 0}")
            print(f"  - Avg Upvotes per Post: {((total_upvotes or 0) / total_posts):.1f}")
        
        forum_members = await db.scalar(select(func.count(ForumMember.member_id)))
        print(f"Forum Members: {forum_members}")
        
        # Notifications
        print("\n🔔 NOTIFICATIONS")
        print("-" * 80)
        total_notifications = await db.scalar(select(func.count(Notifications.notification_id)))
        unread_notifications = await db.scalar(
            select(func.count(Notifications.notification_id)).where(Notifications.is_read == False)
        )
        print(f"Total Notifications: {total_notifications}")
        print(f"  - Unread: {unread_notifications}")
        print(f"  - Read: {total_notifications - unread_notifications}")
        
        if total_notifications > 0:
            # Count by type
            result = await db.execute(
                select(
                    Notifications.type,
                    func.count(Notifications.notification_id)
                ).group_by(Notifications.type)
            )
            print("\n  By Type:")
            for row in result:
                print(f"    - {row[0]}: {row[1]}")
        
        # Study Groups
        print("\n👥 STUDY GROUPS")
        print("-" * 80)
        total_groups = await db.scalar(select(func.count(StudyGroup.group_id)))
        group_members = await db.scalar(select(func.count(StudyGroupMember.member_id)))
        print(f"Total Study Groups: {total_groups}")
        print(f"Total Group Members: {group_members}")
        if total_groups > 0:
            print(f"  - Avg Members per Group: {(group_members / total_groups):.1f}")
        
        # Tutor Registrations
        print("\n📝 TUTOR REGISTRATIONS")
        print("-" * 80)
        total_registrations = await db.scalar(select(func.count(TutorRegistration.registration_id)))
        pending_registrations = await db.scalar(
            select(func.count(TutorRegistration.registration_id)).where(TutorRegistration.status == 'pending')
        )
        approved_registrations = await db.scalar(
            select(func.count(TutorRegistration.registration_id)).where(TutorRegistration.status == 'approved')
        )
        print(f"Total Registrations: {total_registrations}")
        print(f"  - Pending: {pending_registrations}")
        print(f"  - Approved: {approved_registrations}")
        
        # Data Gaps Summary
        print("\n" + "="*80)
        print("⚠️  DATA GAPS IDENTIFIED")
        print("="*80)
        
        gaps = []
        if total_notifications == 0:
            gaps.append("❌ No notifications in database")
        if top_level_posts < 5:
            gaps.append(f"❌ Only {top_level_posts} forum threads (recommend 15-20)")
        if feedback_count < completed_sessions * 0.5:
            gaps.append(f"❌ Low feedback coverage: {feedback_count}/{completed_sessions} sessions")
        if students_with_progress < students_count * 0.3:
            gaps.append(f"❌ Low progress tracking: {students_with_progress}/{students_count} students")
        if completed_sessions < total_sessions * 0.3:
            gaps.append(f"❌ Low completion rate: {completed_sessions}/{total_sessions} sessions ({(completed_sessions/total_sessions*100):.1f}%)")
        if achievements_count == 0:
            gaps.append("❌ No learning achievements recorded")
        
        if gaps:
            for gap in gaps:
                print(gap)
        else:
            print("✅ No major data gaps detected")
        
        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80 + "\n")
        
        break

if __name__ == "__main__":
    asyncio.run(check_database())
