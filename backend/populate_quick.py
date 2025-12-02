"""
Simple population script - focuses on critical data only
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import get_db
from app.models.database import (
    User, Student, Session, SessionFeedback,
    ProgressTracking, ForumPost, Forum, Notifications
)

async def populate():
    print("Starting population...")
    
    async for db in get_db():
        # Get data
        students = (await db.execute(select(Student))).scalars().all()
        sessions = (await db.execute(select(Session))).scalars().all()
        forum = (await db.execute(select(Forum))).first()
        users = (await db.execute(select(User))).scalars().all()
        
        if not forum:
            print("No forum found")
            return
        forum = forum[0]
        
        print(f"Found: {len(students)} students, {len(sessions)} sessions, {len(users)} users")
        
        # 1. Complete sessions
        completed = 0
        for sess in sessions[:10]:  # Only first 10
            if sess.status not in ['completed', 'cancelled'] and sess.student_id:
                sess.status = 'completed'
                sess.end_time = datetime.now() - timedelta(days=random.randint(1, 30))
                
                # Add feedback
                student_obj = await db.get(Student, sess.student_id)
                if student_obj:
                    rating = random.choice([4, 5])
                    feedback = SessionFeedback(
                        session_id=sess.session_id,
                        reviewer_id=student_obj.user_id,
                        reviewer_type='student',
                        rating=rating,
                        comment=f"Buổi học tốt!",
                        is_public=True
                    )
                    db.add(feedback)
                completed += 1
        
        await db.commit()
        print(f"Completed {completed} sessions")
        
        # 2. Add forum posts
        posts = [
            ("Cách học DS&A hiệu quả?", "Mình cần tips học cấu trúc dữ liệu"),
            ("Share tài liệu Calculus", "Ai có tài liệu tốt share mình với!"),
            ("Tips làm OOP", "Làm sao design class tốt?"),
            ("Đề thi năm ngoái", "Có ai có đề thi không ạ?"),
            ("Tìm teammate Web Dev", "Cần 2 bạn làm đồ án React"),
        ]
        
        for title, content in posts:
            author = random.choice(users)
            post = ForumPost(
                forum_id=forum.forum_id,
                author_id=author.user_id,
                parent_post_id=None,
                title=title,
                content=content,
                upvote_count=random.randint(0, 10),
                is_pinned=False,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(post)
        
        await db.commit()
        print("Added 5 forum posts")
        
        # 3. Add notifications
        notif_count = 0
        for student in students[:10]:
            student_user = (await db.execute(
                select(User).where(User.user_id == student.user_id)
            )).scalar_one_or_none()
            
            if student_user:
                # Session reminder
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='session_reminder',
                    title='Nhắc nhở buổi học',
                    message='Buổi học sắp diễn ra vào ngày mai!',
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 15))
                )
                db.add(notif)
                notif_count += 1
        
        await db.commit()
        print(f"Added {notif_count} notifications")
        
        print("\n=== DONE ===")
        break

if __name__ == "__main__":
    asyncio.run(populate())
