"""
Complete database population script with proper constraints
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.database import (
    User, Student, Tutor, Session, SessionFeedback,
    ProgressTracking, ForumPost, Forum, Notifications, Subject
)

# Valid notification types from database constraint
NOTIFICATION_TYPES = [
    'session_created', 'session_updated', 'session_cancelled',
    'registration_approved', 'registration_rejected', 'feedback_received',
    'material_uploaded', 'forum_reply', 'group_invite',
    'achievement_earned', 'system_announcement'
]

FORUM_POSTS = [
    ("Cách học hiệu quả môn Cấu trúc dữ liệu?", "Mình đang gặp khó khăn với phần Tree và Graph, các bạn có tips gì không?"),
    ("Share tài liệu ôn thi Calculus 1", "Ai có tài liệu tốt cho phần tích phân và chuỗi số share mình với!"),
    ("Kinh nghiệm học Linear Algebra", "Môn này khó quá, các bạn học như thế nào để hiểu bản chất?"),
    ("Tips làm bài tập lớn OOP", "Làm sao để thiết kế class diagram một cách khoa học nhỉ?"),
    ("Chuẩn bị cho kỳ thi giữa kỳ Database", "Phần normalization và indexing cần ôn như thế nào?"),
    ("Đề thi Cấu trúc dữ liệu năm ngoái", "Có ai còn lưu đề thi năm trước không ạ?"),
    ("Lịch thi cuối kỳ kỳ này ra chưa nhỉ?", "Mình chưa thấy thông báo gì về lịch thi cả."),
    ("Kinh nghiệm thi vấn đáp OOP", "Giảng viên thường hỏi những câu gì trong phần vấn đáp?"),
    ("Review trước kỳ thi Algorithms", "Cùng nhau ôn tập các thuật toán sorting và searching nào!"),
    ("Tìm teammate làm đồ án Web Development", "Cần 2 bạn có kinh nghiệm React và Node.js."),
    ("Share idea cho đồ án cuối kỳ AI", "Các bạn làm đề tài gì cho môn Machine Learning?"),
    ("Hỏi về deploy project lên cloud", "Deploy lên AWS hay Google Cloud tốt hơn nhỉ?"),
    ("Intern ở startup hay công ty lớn?", "Các bạn nghĩ thế nào về việc chọn nơi thực tập?"),
    ("Roadmap để trở thành Backend Developer", "Nên học những gì để đi làm Backend?"),
    ("CLB lập trình tuyển thành viên", "CLB Code For Fun đang tuyển member nhiệt tình!"),
]

PROGRESS_TEMPLATES = {
    2: {
        'topics': ['Khái niệm cơ bản', 'Giới thiệu', 'Lý thuyết nền tảng'],
        'strengths': 'Đi học đúng giờ, Có động lực học',
        'weaknesses': 'Chưa nắm vững lý thuyết, Thiếu thực hành, Cần ôn lại kiến thức nền',
        'feedback': 'Cần dành nhiều thời gian hơn cho việc học và thực hành.'
    },
    3: {
        'topics': ['Lý thuyết cơ bản', 'Bài tập đơn giản', 'Ứng dụng cơ bản'],
        'strengths': 'Hiểu được khái niệm, Làm được bài tập cơ bản',
        'weaknesses': 'Chưa vững phần nâng cao, Cần cải thiện tốc độ',
        'feedback': 'Tiến bộ tốt! Tiếp tục luyện tập thêm các bài tập nâng cao.'
    },
    4: {
        'topics': ['Lý thuyết nâng cao', 'Bài tập phức tạp', 'Ứng dụng thực tế', 'Case studies'],
        'strengths': 'Tư duy logic tốt, Làm bài nhanh, Hiểu sâu vấn đề',
        'weaknesses': 'Một số chi tiết nhỏ cần chú ý, Code có thể optimize hơn',
        'feedback': 'Rất tốt! Học sinh hiểu sâu và áp dụng tốt. Cần chú ý thêm về optimization.'
    },
    5: {
        'topics': ['Toàn bộ chương trình', 'Bài tập nâng cao', 'Dự án thực tế', 'Research topics'],
        'strengths': 'Xuất sắc, Tư duy sắc bén, Tự học tốt, Giúp đỡ bạn khác',
        'weaknesses': '',
        'feedback': 'Xuất sắc! Học sinh nắm vững kiến thức và có khả năng tự học tốt.'
    }
}

async def populate():
    print("\n" + "="*80)
    print("POPULATING DATABASE WITH COMPLETE SAMPLE DATA")
    print("="*80 + "\n")
    
    async for db in get_db():
        # Get existing data
        students = (await db.execute(select(Student))).scalars().all()
        tutors = (await db.execute(select(Tutor))).scalars().all()
        sessions = (await db.execute(select(Session))).scalars().all()
        subjects = (await db.execute(select(Subject))).scalars().all()
        forum = (await db.execute(select(Forum))).first()
        users = (await db.execute(select(User))).scalars().all()
        
        if not forum:
            print("❌ No forum found. Creating one...")
            forum_obj = Forum(
                creator_id=users[0].user_id,
                forum_name="General Discussion",
                description="Diễn đàn thảo luận chung",
                is_public=True,
                member_count=len(users)
            )
            db.add(forum_obj)
            await db.commit()
            await db.refresh(forum_obj)
            forum = forum_obj
        else:
            forum = forum[0]
        
        print(f"📊 Current data: {len(students)} students, {len(tutors)} tutors, {len(sessions)} sessions")
        print(f"📊 {len(subjects)} subjects, {len(users)} users\n")
        
        # 1. Complete more sessions
        print("📚 Completing sessions and adding feedback...")
        completed_count = 0
        feedback_count = 0
        
        for sess in sessions:
            if sess.status not in ['completed', 'cancelled'] and sess.student_id:
                # 60% chance to complete
                if random.random() < 0.6:
                    sess.status = 'completed'
                    # Set end_time as datetime (not just time)
                    if sess.scheduled_date:
                        from datetime import datetime as dt, time
                        # Combine date with a random hour
                        end_hour = random.randint(14, 20)
                        sess.end_time = time(end_hour, random.choice([0, 30]))
                    
                    completed_count += 1
                    
                    # Add feedback (70% of completed)
                    if random.random() < 0.7:
                        student_obj = await db.get(Student, sess.student_id)
                        if student_obj:
                            rating = random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0]
                            feedback = SessionFeedback(
                                session_id=sess.session_id,
                                reviewer_id=student_obj.user_id,
                                reviewer_type='student',
                                rating=rating,
                                comment=f"Buổi học rất {'xuất sắc' if rating == 5 else 'tốt' if rating == 4 else 'khá'}! Tutor nhiệt tình.",
                                is_public=True,
                                is_anonymous=False
                            )
                            db.add(feedback)
                            feedback_count += 1
        
        await db.commit()
        print(f"✅ Completed {completed_count} sessions, added {feedback_count} feedbacks\n")
        
        # 2. Add progress tracking
        print("📈 Adding progress tracking...")
        completed_sessions = (await db.execute(
            select(Session).where(Session.status == 'completed')
        )).scalars().all()
        
        progress_count = 0
        for sess in completed_sessions:
            if sess.subject_id and sess.student_id:
                # Check if already has progress
                existing = await db.execute(
                    select(ProgressTracking).where(ProgressTracking.session_id == sess.session_id)
                )
                if existing.scalar_one_or_none():
                    continue
                
                # 60% chance
                if random.random() < 0.6:
                    level = random.choices([2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.3])[0]
                    template = PROGRESS_TEMPLATES[level]
                    
                    # Select 1-3 random topics
                    num_topics = random.randint(1, min(3, len(template['topics'])))
                    topics = random.sample(template['topics'], num_topics)
                    
                    progress = ProgressTracking(
                        session_id=sess.session_id,
                        student_id=sess.student_id,
                        subject_id=sess.subject_id,
                        topics_covered=topics,  # Now correctly ARRAY(Text)
                        understanding_level=level,
                        strengths=template['strengths'],
                        weaknesses=template['weaknesses'] if template['weaknesses'] else None,
                        tutor_feedback=template['feedback'],
                        homework_assigned=f"Bài tập chương {random.randint(1, 10)}" if random.random() < 0.5 else None,
                        homework_completed=random.choice([True, True, False]),
                        homework_grade=random.randint(70, 100) if random.random() < 0.4 else None
                    )
                    db.add(progress)
                    progress_count += 1
        
        await db.commit()
        print(f"✅ Added {progress_count} progress entries\n")
        
        # 3. Add forum posts
        print("💬 Adding forum posts...")
        existing_posts = await db.scalar(select(func.count(ForumPost.post_id)))
        posts_to_add = max(0, 15 - existing_posts)
        
        post_count = 0
        for title, content in FORUM_POSTS[:posts_to_add]:
            author = random.choice(users)
            post = ForumPost(
                forum_id=forum.forum_id,
                author_id=author.user_id,
                parent_post_id=None,
                title=title,
                content=content,
                upvote_count=random.randint(0, 15),
                is_pinned=False,
                created_at=datetime.now() - timedelta(days=random.randint(1, 60))
            )
            db.add(post)
            post_count += 1
        
        await db.commit()
        print(f"✅ Added {post_count} forum posts\n")
        
        # 4. Add replies to some posts
        print("💬 Adding replies...")
        all_posts = (await db.execute(
            select(ForumPost).where(ForumPost.parent_post_id == None).limit(10)
        )).scalars().all()
        
        reply_count = 0
        for post in all_posts:
            num_replies = random.randint(1, 4)
            for _ in range(num_replies):
                author = random.choice(users)
                reply = ForumPost(
                    forum_id=forum.forum_id,
                    author_id=author.user_id,
                    parent_post_id=post.post_id,
                    title=None,
                    content=random.choice([
                        'Mình cũng đang gặp vấn đề tương tự!',
                        'Bạn thử tham khảo tài liệu này xem...',
                        'Mình nghĩ cách tốt nhất là...',
                        'Có thể giải thích rõ hơn được không?',
                        'Thanks bạn đã share! Rất hữu ích!',
                        'Mình đã giải quyết vấn đề này bằng cách...'
                    ]),
                    upvote_count=random.randint(0, 8),
                    is_pinned=False,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48))
                )
                db.add(reply)
                reply_count += 1
        
        await db.commit()
        print(f"✅ Added {reply_count} replies\n")
        
        # 5. Add notifications
        print("🔔 Adding notifications...")
        notif_count = 0
        
        for student in students[:15]:
            student_user = await db.execute(
                select(User).where(User.user_id == student.user_id)
            )
            student_user = student_user.scalar_one_or_none()
            if not student_user:
                continue
            
            # Session created notifications
            for _ in range(random.randint(1, 2)):
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='session_created',
                    title='Phiên học mới được tạo',
                    message=f'Bạn có phiên học mới về {random.choice([s.subject_name for s in subjects])}',
                    is_read=random.choice([True, True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 20))
                )
                db.add(notif)
                notif_count += 1
            
            # Feedback received
            if random.random() < 0.5:
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='feedback_received',
                    title='Nhận được đánh giá',
                    message='Tutor đã đánh giá phiên học của bạn',
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 15))
                )
                db.add(notif)
                notif_count += 1
            
            # Forum reply
            if random.random() < 0.4:
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='forum_reply',
                    title='Có người trả lời bài viết của bạn',
                    message='Bài viết của bạn có câu trả lời mới',
                    is_read=random.choice([True, True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 10))
                )
                db.add(notif)
                notif_count += 1
        
        await db.commit()
        print(f"✅ Added {notif_count} notifications\n")
        
        # Final stats
        print("="*80)
        print("POPULATION COMPLETED - FINAL STATS")
        print("="*80 + "\n")
        
        total_sessions = await db.scalar(select(func.count(Session.session_id)))
        completed = await db.scalar(
            select(func.count(Session.session_id)).where(Session.status == 'completed')
        )
        total_progress = await db.scalar(select(func.count(ProgressTracking.progress_id)))
        total_forum = await db.scalar(select(func.count(ForumPost.post_id)))
        total_notif = await db.scalar(select(func.count(Notifications.notification_id)))
        total_feedback = await db.scalar(select(func.count(SessionFeedback.feedback_id)))
        
        print(f"✅ Sessions: {completed}/{total_sessions} completed ({completed/total_sessions*100:.1f}%)")
        print(f"✅ Progress Tracking: {total_progress} entries")
        print(f"✅ Forum Posts: {total_forum} posts")
        print(f"✅ Notifications: {total_notif} notifications")
        print(f"✅ Session Feedback: {total_feedback} feedbacks\n")
        
        print("="*80)
        print("Done! Database now has realistic sample data.")
        print("="*80 + "\n")
        
        break

if __name__ == "__main__":
    asyncio.run(populate())
