"""
Script to populate database with realistic sample data
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.core.database import get_db
from app.models.database import (
    User, Student, Tutor,
    Session, SessionFeedback, ProgressTracking,
    Forum, ForumPost, Notifications, Subject
)

# Sample data
FORUM_CATEGORIES = {
    'study': [
        ('Cách học hiệu quả cho môn Cấu trúc dữ liệu?', 'Mình đang gặp khó khăn với phần Tree và Graph, các bạn có tips gì không?'),
        ('Share tài liệu ôn thi Calculus 1', 'Ai có tài liệu tốt cho phần tích phân và chuỗi số share mình với!'),
        ('Kinh nghiệm học Linear Algebra', 'Môn này khó quá, các bạn học như thế nào để hiểu bản chất?'),
        ('Tips làm bài tập lớn OOP', 'Làm sao để thiết kế class diagram một cách khoa học nhỉ?'),
        ('Chuẩn bị cho kỳ thi giữa kỳ Database', 'Phần normalization và indexing cần ôn như thế nào?'),
    ],
    'exam': [
        ('Đề thi Cấu trúc dữ liệu năm ngoái', 'Có ai còn lưu đề thi năm trước không ạ?'),
        ('Lịch thi cuối kỳ kỳ này ra chưa nhỉ?', 'Mình chưa thấy thông báo gì về lịch thi cả.'),
        ('Kinh nghiệm thi vấn đáp OOP', 'Giảng viên thường hỏi những câu gì trong phần vấn đáp?'),
        ('Review trước kỳ thi Algorithms', 'Cùng nhau ôn tập các thuật toán sorting và searching nào!'),
    ],
    'project': [
        ('Tìm teammate làm đồ án Web Development', 'Cần 2 bạn có kinh nghiệm React và Node.js.'),
        ('Share idea cho đồ án cuối kỳ AI', 'Các bạn làm đề tài gì cho môn Machine Learning?'),
        ('Hỏi về deploy project lên cloud', 'Deploy lên AWS hay Google Cloud tốt hơn nhỉ?'),
    ],
    'career': [
        ('Intern ở startup hay công ty lớn?', 'Các bạn nghĩ thế nào về việc chọn nơi thực tập?'),
        ('Roadmap để trở thành Backend Developer', 'Nên học những gì để đi làm Backend?'),
        ('Chia sẻ kinh nghiệm phỏng vấn FPT', 'Mình vừa pass vòng 1 FPT, chia sẻ cho mọi người!'),
    ],
    'other': [
        ('CLB lập trình tuyển thành viên', 'CLB Code For Fun đang tuyển member nhiệt tình!'),
        ('Gợi ý laptop cho sinh viên IT', 'Budget 20tr nên mua máy gì các bạn?'),
    ]
}

PROGRESS_FEEDBACK_TEMPLATES = {
    'understanding_2': {
        'topics': ['Khái niệm cơ bản', 'Giới thiệu'],
        'strengths': ['Đi học đúng giờ', 'Có động lực học'],
        'weaknesses': ['Chưa nắm vững lý thuyết', 'Thiếu thực hành', 'Cần ôn lại kiến thức nền'],
        'feedback': 'Cần dành nhiều thời gian hơn cho việc học và thực hành. Nên ôn lại kiến thức cơ bản.'
    },
    'understanding_3': {
        'topics': ['Lý thuyết cơ bản', 'Bài tập đơn giản'],
        'strengths': ['Hiểu được khái niệm', 'Làm được bài tập cơ bản'],
        'weaknesses': ['Chưa vững phần nâng cao', 'Cần cải thiện tốc độ'],
        'feedback': 'Tiến bộ tốt! Tiếp tục luyện tập thêm các bài tập nâng cao để nắm vững hơn.'
    },
    'understanding_4': {
        'topics': ['Lý thuyết nâng cao', 'Bài tập phức tạp', 'Ứng dụng thực tế'],
        'strengths': ['Tư duy logic tốt', 'Làm bài nhanh', 'Hiểu sâu vấn đề'],
        'weaknesses': ['Một số chi tiết nhỏ cần chú ý', 'Code có thể optimize hơn'],
        'feedback': 'Rất tốt! Học sinh hiểu sâu và áp dụng tốt. Cần chú ý thêm về optimization và edge cases.'
    },
    'understanding_5': {
        'topics': ['Toàn bộ chương trình', 'Bài tập nâng cao', 'Dự án thực tế'],
        'strengths': ['Xuất sắc', 'Tư duy sắc bén', 'Tự học tốt', 'Giúp đỡ bạn khác'],
        'weaknesses': [],
        'feedback': 'Xuất sắc! Học sinh nắm vững kiến thức và có khả năng tự học tốt. Tiếp tục phát huy!'
    }
}

NOTIFICATION_TEMPLATES = {
    'session_reminder': {
        'title': 'Nhắc nhở buổi học',
        'message': 'Buổi học {} sắp diễn ra vào {}. Hãy chuẩn bị tài liệu và đến đúng giờ nhé!'
    },
    'session_completed': {
        'title': 'Buổi học hoàn thành',
        'message': 'Buổi học {} đã hoàn thành. Đừng quên đánh giá tutor và chia sẻ feedback nhé!'
    },
    'new_forum_post': {
        'title': 'Bài viết mới',
        'message': 'Có bài viết mới trong diễn đàn: "{}"'
    },
    'achievement_earned': {
        'title': 'Đạt thành tựu mới',
        'message': 'Chúc mừng! Bạn đã đạt thành tựu: {}'
    },
    'feedback_received': {
        'title': 'Nhận được đánh giá',
        'message': 'Bạn nhận được đánh giá {} sao cho buổi học {}'
    }
}

async def populate_data():
    print("\n" + "="*80)
    print("POPULATING DATABASE WITH SAMPLE DATA")
    print("="*80 + "\n")
    
    async for db in get_db():
        # Get existing data
        students = (await db.execute(select(Student))).scalars().all()
        tutors = (await db.execute(select(Tutor))).scalars().all()
        subjects = (await db.execute(select(Subject))).scalars().all()
        sessions = (await db.execute(select(Session))).scalars().all()
        forum = (await db.execute(select(Forum))).first()
        
        if not forum:
            print("❌ No forum found. Please create a forum first.")
            return
        
        forum = forum[0]
        
        # Get users for forum posts
        users = (await db.execute(select(User))).scalars().all()
        
        print(f"📊 Found: {len(students)} students, {len(tutors)} tutors, {len(subjects)} subjects")
        print(f"📊 Found: {len(sessions)} sessions, {len(users)} users\n")
        
        # 1. Complete more sessions and add feedback
        print("📚 Completing sessions and adding feedback...")
        completed_count = 0
        for session in sessions:
            if session.status not in ['completed', 'cancelled'] and session.student_id:
                # 60% chance to complete
                if random.random() < 0.6:
                    session.status = 'completed'
                    session.end_time = datetime.now() - timedelta(days=random.randint(1, 30))
                    
                    # Add feedback (80% of completed sessions)
                    if random.random() < 0.8:
                        rating = random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0]
                        
                        # Get student user_id
                        student_obj = await db.get(Student, session.student_id)
                        
                        if student_obj:
                            feedback = SessionFeedback(
                                session_id=session.session_id,
                                reviewer_id=student_obj.user_id,
                                reviewer_type='student',
                                rating=rating,
                                comment=f"Buổi học rất bổ ích. Tutor giảng dạy {'xuất sắc' if rating == 5 else 'tốt' if rating == 4 else 'khá'}!",
                                tags=[],
                                is_public=True,
                                is_anonymous=False,
                                created_at=session.end_time + timedelta(hours=random.randint(1, 24))
                            )
                            db.add(feedback)
                    
                    completed_count += 1
        
        await db.commit()
        print(f"✅ Completed {completed_count} sessions")
        
        # 2. Add progress tracking for more students
        print("\n📈 Adding progress tracking entries...")
        progress_count = 0
        
        # Refresh sessions to get updated data
        completed_sessions = (await db.execute(
            select(Session).where(Session.status == 'completed')
        )).scalars().all()
        
        for session in completed_sessions:
            # 70% chance to have progress tracking
            if random.random() < 0.7 and session.subject_id and session.student_id:
                level = random.choices([2, 3, 4, 5], weights=[0.1, 0.2, 0.4, 0.3])[0]
                template = PROGRESS_FEEDBACK_TEMPLATES[f'understanding_{level}']
                
                # Topics as comma-separated text string
                topics_text = ", ".join(random.sample(template['topics'], min(len(template['topics']), random.randint(1, 3))))
                strengths_text = ", ".join(random.sample(template['strengths'], min(len(template['strengths']), random.randint(1, 2))))
                weaknesses_text = ", ".join(random.sample(template['weaknesses'], min(len(template['weaknesses']), random.randint(0, 2)))) if template['weaknesses'] else None
                
                progress = ProgressTracking(
                    session_id=session.session_id,
                    student_id=session.student_id,
                    subject_id=session.subject_id,
                    understanding_level=level,
                    topics_covered=topics_text,  # TEXT field, not array
                    strengths=strengths_text,
                    weaknesses=weaknesses_text,
                    tutor_feedback=template['feedback'],
                    notes=None,
                    homework_assigned="Bài tập chương " + str(random.randint(1, 10)) if random.random() < 0.6 else None,
                    homework_completed=random.choice([True, True, True, False]),  # 75% complete
                    homework_grade=random.randint(70, 100) if random.random() < 0.5 else None
                )
                db.add(progress)
                progress_count += 1
        
        await db.commit()
        print(f"✅ Added {progress_count} progress tracking entries")
        
        # 3. Create forum posts
        print("\n💬 Creating forum posts...")
        post_count = 0
        
        for category, posts_data in FORUM_CATEGORIES.items():
            for title, content in posts_data:
                author = random.choice(users)
                post = ForumPost(
                    forum_id=forum.forum_id,
                    author_id=author.user_id,
                    parent_post_id=None,
                    title=title,
                    content=content,
                    upvote_count=random.randint(0, 15),
                    is_pinned=False,
                    tags=[category],
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60))
                )
                db.add(post)
                post_count += 1
        
        await db.commit()
        print(f"✅ Created {post_count} forum posts")
        
        # Refresh to get post IDs
        await db.commit()
        all_posts = (await db.execute(select(ForumPost).where(ForumPost.parent_post_id == None))).scalars().all()
        
        # Add replies to some posts
        print("\n💬 Adding replies to forum posts...")
        reply_count = 0
        for post in all_posts[:10]:  # Add replies to first 10 posts
            num_replies = random.randint(1, 5)
            for _ in range(num_replies):
                author = random.choice(users)
                reply = ForumPost(
                    forum_id=forum.forum_id,
                    author_id=author.user_id,
                    parent_post_id=post.post_id,
                    title=None,
                    content=random.choice([
                        'Mình cũng đang gặp vấn đề tương tự!',
                        'Bạn thử tham khảo tài liệu này xem: ...',
                        'Mình nghĩ cách tốt nhất là...',
                        'Có thể giải thích rõ hơn được không?',
                        'Thanks bạn đã share! Rất hữu ích!',
                        'Mình đã giải quyết vấn đề này bằng cách...'
                    ]),
                    upvote_count=random.randint(0, 8),
                    is_pinned=False,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 72))
                )
                db.add(reply)
                reply_count += 1
        
        await db.commit()
        print(f"✅ Added {reply_count} replies")
        
        # 4. Create notifications
        print("\n🔔 Creating notifications...")
        notification_count = 0
        
        for student in students[:15]:  # Create notifications for first 15 students
            student_user = (await db.execute(
                select(User).where(User.user_id == student.user_id)
            )).scalar_one_or_none()
            
            if not student_user:
                continue
            
            # Session reminders
            for i in range(random.randint(2, 4)):
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='session_reminder',
                    title='Nhắc nhở buổi học',
                    message=f'Buổi học Môn {random.choice([s.subject_name for s in subjects])} sắp diễn ra vào ngày mai. Hãy chuẩn bị tài liệu!',
                    is_read=random.choice([True, True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(notif)
                notification_count += 1
            
            # Session completed
            for i in range(random.randint(1, 2)):
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='session_completed',
                    title='Buổi học hoàn thành',
                    message='Buổi học vừa hoàn thành. Đừng quên đánh giá tutor nhé!',
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 20))
                )
                db.add(notif)
                notification_count += 1
            
            # New forum posts
            if random.random() < 0.7:
                notif = Notifications(
                    user_id=student_user.user_id,
                    type='new_forum_post',
                    title='Bài viết mới',
                    message=f'Có bài viết mới trong diễn đàn: "{random.choice([t for cat in FORUM_CATEGORIES.values() for t, c in cat])[0]}"',
                    is_read=random.choice([True, True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 15))
                )
                db.add(notif)
                notification_count += 1
        
        await db.commit()
        print(f"✅ Created {notification_count} notifications")
        
        # Summary
        print("\n" + "="*80)
        print("POPULATION COMPLETED")
        print("="*80)
        
        # Get final counts
        total_completed = await db.scalar(select(func.count(Session.session_id)).where(Session.status == 'completed'))
        total_progress = await db.scalar(select(func.count(ProgressTracking.progress_id)))
        total_forum_posts = await db.scalar(select(func.count(ForumPost.post_id)))
        total_notifications = await db.scalar(select(func.count(Notifications.notification_id)))
        
        print(f"\n✅ Final Database State:")
        print(f"   - Completed Sessions: {total_completed}")
        print(f"   - Progress Entries: {total_progress}")
        print(f"   - Forum Posts: {total_forum_posts}")
        print(f"   - Notifications: {total_notifications}\n")
        
        break

if __name__ == "__main__":
    from sqlalchemy import func
    asyncio.run(populate_data())
