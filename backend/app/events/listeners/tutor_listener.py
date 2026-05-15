"""
Tutor Event Listener
Handle tutor-related events
"""
import logging
from typing import Dict, Any
from sqlalchemy import select, func, insert, or_

from app.events.base_listener import BaseListener
from app.events import event_bus, EventTypes
from app.core.database import AsyncSessionLocal
from app.websocket import manager

logger = logging.getLogger(__name__)


class TutorRegistrationListener(BaseListener):
    """Handle tutor registration events"""

    async def handle(self, data: Dict[str, Any]):
        """
        Gửi notification cho tất cả admin + coordinator khi tutor tạo profile.

        Cải tiến so với cũ:
          - Chỉ SELECT user_id thay vì load toàn bộ User object vào RAM
          - Bulk INSERT thay vì loop INSERT từng row
          - Fix bug query: dùng OR + any_() đúng với PostgreSQL ARRAY column
          - WebSocket push realtime cho users đang online
        """
        try:
            full_name = data.get('full_name', 'Unknown')
            tutor_id  = data.get('tutor_id')
            user_id   = data.get('user_id')
            logger.info(f"New tutor registration: {full_name} (ID: {tutor_id})")

            from app.models.database import User, Notifications
            from sqlalchemy import any_

            async with AsyncSessionLocal() as db:
                # ① Chỉ lấy user_id — không load full User object vào RAM
                #    Fix bug: dùng any_() đúng cho PostgreSQL ARRAY column
                result = await db.execute(
                    select(User.user_id).where(
                        or_(
                            'admin' == any_(User.role),
                            'coordinator' == any_(User.role)
                        )
                    )
                )
                recipient_ids = result.scalars().all()  # list[int] — rất nhẹ

                if not recipient_ids:
                    logger.warning("No admin/coordinator found to notify")
                    return

                # ② Bulk INSERT — 1 câu SQL thay vì N câu
                message = f"{full_name} đã đăng ký làm Tutor. Vui lòng xem xét và phê duyệt."
                await db.execute(
                    insert(Notifications),
                    [
                        {
                            "user_id": uid,
                            "type":    "tutor_registration",
                            "title":   "Đơn đăng ký Tutor mới",
                            "message": message,
                            "data":    {"tutor_id": tutor_id, "user_id": user_id, "status": "pending"},
                            "is_read": False
                        }
                        for uid in recipient_ids
                    ]
                )
                await db.commit()
                logger.info(f"Bulk inserted notifications for {len(recipient_ids)} recipient(s)")

                # ③ WebSocket push — chỉ gửi cho users đang online
                ws_payload = {
                    "title":    "Đơn đăng ký Tutor mới",
                    "message":  message,
                    "tutor_id": tutor_id,
                }
                online_count = 0
                for uid in recipient_ids:
                    if manager.is_online(uid):
                        try:
                            await manager.notify_user(
                                user_id=uid,
                                notification_type="tutor_registration",
                                data=ws_payload
                            )
                            online_count += 1
                        except Exception as ws_err:
                            logger.warning(f"WebSocket push failed for user {uid}: {ws_err}")

                logger.info(f"WebSocket push: {online_count}/{len(recipient_ids)} online")

        except Exception as e:
            logger.error(f"Error in TutorRegistrationListener: {e}", exc_info=True)



class TutorSubjectRegistrationListener(BaseListener):
    """Handle tutor subject registration events"""

    async def handle(self, data: Dict[str, Any]):
        """
        Gửi notification cho coordinators + xác nhận cho tutor khi tutor đăng ký dạy môn.

        Cải tiến so với cũ:
          - Chỉ SELECT user_id (không load full User object)
          - Bulk INSERT thay vì loop INSERT
          - WebSocket push realtime cho coordinators đang online
        """
        try:
            subject_name  = data.get('subject_name', '')
            subject_code  = data.get('subject_code', '')
            full_name     = data.get('full_name', 'Unknown')
            tutor_user_id = data.get('user_id')
            logger.info(f"New subject registration: {full_name} for {subject_code} - {subject_name}")

            from app.models.database import User, Notifications
            from sqlalchemy import any_

            # Build messages
            coord_message = f"{full_name} đã đăng ký dạy môn {subject_code} - {subject_name}."
            if data.get('gpa'):
                coord_message += f" GPA: {data['gpa']}"
            if data.get('max_students'):
                coord_message += f" | Tối đa {data['max_students']} sinh viên/buổi"

            tutor_message = (
                f"Đơn đăng ký dạy môn {subject_code} - {subject_name} "
                f"của bạn đã được gửi và đang chờ phê duyệt."
            )

            notification_meta = {
                "registration_id": data.get('registration_id'),
                "tutor_id":        data.get('tutor_id'),
                "user_id":         tutor_user_id,
                "subject_id":      data.get('subject_id'),
                "subject_code":    subject_code,
                "subject_name":    subject_name,
                "status":          "pending",
                "gpa":             data.get('gpa'),
                "qualifications":  data.get('qualifications'),
                "availability":    data.get('availability', {}),
                "total_sessions":  data.get('total_sessions', 10),
                "start_date":      data.get('start_date'),
                "end_date":        data.get('end_date'),
                "max_students":    data.get('max_students', 25)
            }

            async with AsyncSessionLocal() as db:
                # ① Chỉ lấy user_id của coordinators
                result = await db.execute(
                    select(User.user_id).where('coordinator' == any_(User.role))
                )
                coordinator_ids = result.scalars().all()  # list[int]

                if coordinator_ids:
                    # ② Bulk INSERT cho coordinators — 1 query thay vì N
                    await db.execute(
                        insert(Notifications),
                        [
                            {
                                "user_id": uid,
                                "type":    "subject_registration",
                                "title":   "Đơn đăng ký dạy môn mới",
                                "message": coord_message,
                                "data":    notification_meta,
                                "is_read": False
                            }
                            for uid in coordinator_ids
                        ]
                    )
                    logger.info(f"Bulk inserted notifications for {len(coordinator_ids)} coordinator(s)")

                # ③ INSERT xác nhận cho chính tutor
                await db.execute(
                    insert(Notifications),
                    [{
                        "user_id": tutor_user_id,
                        "type":    "subject_registration_submitted",
                        "title":   "Đơn đăng ký đã được gửi",
                        "message": tutor_message,
                        "data":    notification_meta,
                        "is_read": False
                    }]
                )
                await db.commit()

                # ④ WebSocket push cho coordinators đang online
                ws_payload = {
                    "title":           "Đơn đăng ký dạy môn mới",
                    "message":         coord_message,
                    "registration_id": data.get('registration_id'),
                    "tutor_id":        data.get('tutor_id'),
                    "subject_code":    subject_code,
                    "subject_name":    subject_name,
                }
                online_count = 0
                for uid in coordinator_ids:
                    if manager.is_online(uid):
                        try:
                            await manager.notify_user(
                                user_id=uid,
                                notification_type="subject_registration",
                                data=ws_payload
                            )
                            online_count += 1
                        except Exception as ws_err:
                            logger.warning(f"WebSocket push failed for coordinator {uid}: {ws_err}")

                # ⑤ WebSocket push xác nhận cho tutor
                if manager.is_online(tutor_user_id):
                    try:
                        await manager.notify_user(
                            user_id=tutor_user_id,
                            notification_type="subject_registration_submitted",
                            data={"title": "Đơn đăng ký đã được gửi", "message": tutor_message}
                        )
                    except Exception as ws_err:
                        logger.warning(f"WebSocket push to tutor failed: {ws_err}")

                logger.info(
                    f"Done: {len(coordinator_ids)} coordinator(s) notified, "
                    f"{online_count} online push sent"
                )

        except Exception as e:
            logger.error(f"Error in TutorSubjectRegistrationListener: {e}", exc_info=True)



class TutorApprovalListener(BaseListener):
    """Handle tutor registration approval/rejection events"""
    
    async def handle(self, data: Dict[str, Any]):
        """
        Create notification for tutor when their registration is approved/rejected
        AND auto-generate sessions from schedule
        
        Expected data:
            - user_id: int
            - registration_id: int
            - tutor_id: int
            - subject_id: int
            - subject_name: str
            - status: str ('approved' or 'rejected')
            - reason: str (optional, for rejection)
            - total_sessions: int (optional, default 10)
            - start_date: str (ISO format)
            - schedule_id: int (optional, specific schedule to use)
        """
        try:
            user_id = data.get('user_id')
            subject_name = data.get('subject_name', 'môn học')
            status = data.get('status', 'approved')
            
            logger.info(f"Registration {status}: user_id={user_id}, subject={subject_name}")
            
            from app.models.database import Notifications
            
            async with AsyncSessionLocal() as db:
                if status == 'approved':
                    notification = Notifications(
                        user_id=user_id,
                        type='registration_approved',
                        title='Đơn đăng ký môn học được phê duyệt',
                        message=f'Chúc mừng! Đơn đăng ký dạy môn {subject_name} của bạn đã được phê duyệt.',
                        data={
                            "registration_id": data.get('registration_id'),
                            "subject_name": subject_name,
                            "status": "approved"
                        },
                        is_read=False
                    )
                    db.add(notification)
                    await db.commit()
                    
                    # NOTE: Sessions are NO LONGER auto-generated on approval
                    # Tutor must manually generate sessions from CourseDetail page
                    logger.info(f"✅ Registration approved. Tutor can now generate sessions manually from course detail page.")
                    
                else:  # rejected
                    reason = data.get('reason', 'Không đáp ứng yêu cầu')
                    notification = Notifications(
                        user_id=user_id,
                        type='registration_rejected',
                        title='Đơn đăng ký môn học bị từ chối',
                        message=f'Đơn đăng ký dạy môn {subject_name} của bạn đã bị từ chối. Lý do: {reason}',
                        data={
                            "registration_id": data.get('registration_id'),
                            "subject_name": subject_name,
                            "status": "rejected",
                            "reason": reason
                        },
                        is_read=False
                    )
                    db.add(notification)
                    await db.commit()
                
                logger.info(f"Created {status} notification for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error creating approval/rejection notification: {e}")
    
    async def _generate_sessions_from_schedule(
        self,
        db,
        tutor_id: int,
        subject_id: int,
        total_sessions: int,
        start_date_str: str,
        max_students: int = 5,
        schedule_id: int = None
    ):
        """Generate Session records from SessionSchedule"""
        try:
            from app.models.database import SessionSchedule, Session, Subject
            from datetime import datetime, timedelta
            
            # Get the schedule (specific one if schedule_id provided, otherwise first active)
            if schedule_id:
                schedule_result = await db.execute(
                    select(SessionSchedule).where(
                        SessionSchedule.schedule_id == schedule_id,
                        SessionSchedule.tutor_id == tutor_id,
                        SessionSchedule.subject_id == subject_id,
                        SessionSchedule.is_active == True
                    )
                )
            else:
                schedule_result = await db.execute(
                    select(SessionSchedule).where(
                        SessionSchedule.tutor_id == tutor_id,
                        SessionSchedule.subject_id == subject_id,
                        SessionSchedule.is_active == True
                    )
                )
            schedule = schedule_result.scalar_one_or_none()
            
            if not schedule:
                logger.warning(f"No active schedule found for tutor {tutor_id}, subject {subject_id}")
                return
            
            # Get subject name
            subject_result = await db.execute(
                select(Subject).where(Subject.subject_id == subject_id)
            )
            subject = subject_result.scalar_one_or_none()
            subject_name = subject.subject_name if subject else "Unknown Subject"
            
            # Parse start date
            if start_date_str:
                start_date = datetime.fromisoformat(start_date_str).date()
            else:
                start_date = datetime.now().date()
            
            # Check if sessions already exist to prevent duplicates
            existing_sessions_result = await db.execute(
                select(func.count(Session.session_id)).where(
                    Session.tutor_id == tutor_id,
                    Session.subject_id == subject_id
                )
            )
            existing_count = existing_sessions_result.scalar() or 0
            
            if existing_count > 0:
                logger.warning(f"⚠️  Sessions already exist for tutor {tutor_id}, subject {subject_id} ({existing_count} sessions). Skipping generation.")
                return
            
            # Find first occurrence of the scheduled day
            current_date = start_date
            day_of_week = schedule.day_of_week
            
            # Advance to the first matching day
            while current_date.weekday() != day_of_week:
                current_date += timedelta(days=1)
            
            # Generate sessions
            logger.info(f"Generating {total_sessions} sessions starting from {current_date}")
            
            for i in range(total_sessions):
                session = Session(
                    tutor_id=tutor_id,
                    subject_id=subject_id,
                    title=f"{subject_name} - Session {i+1}",
                    description=schedule.description or f"Tutoring session for {subject_name}",
                    scheduled_date=current_date,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time,
                    duration=schedule.duration,
                    location_type=schedule.location_type or 'online',
                    meeting_link=None,
                    physical_address=None,
                    max_students=max_students,
                    status='draft'
                )
                db.add(session)
                
                # Move to next week (same day)
                current_date += timedelta(weeks=1)
            
            await db.commit()
            logger.info(f"✅ Successfully generated {total_sessions} sessions for tutor {tutor_id}, subject {subject_id}")
            
        except Exception as e:
            logger.error(f"Error generating sessions from schedule: {e}")
            await db.rollback()


def register_tutor_listeners():
    """Register all tutor-related event listeners"""
    event_bus.register(EventTypes.TUTOR_REGISTERED, TutorRegistrationListener().execute)
    event_bus.register(EventTypes.TUTOR_SUBJECT_REGISTERED, TutorSubjectRegistrationListener().execute)
    event_bus.register(EventTypes.REGISTRATION_APPROVED, TutorApprovalListener().execute)
    event_bus.register(EventTypes.REGISTRATION_REJECTED, TutorApprovalListener().execute)
    logger.info("✅ Tutor event listeners registered")
