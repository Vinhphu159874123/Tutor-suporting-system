"""
Tutor Event Listener
Handle tutor-related events
"""
import logging
from typing import Dict, Any

from app.events.base_listener import BaseListener
from app.events import event_bus, EventTypes
from app.core.database import AsyncSessionLocal
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.websocket import manager

logger = logging.getLogger(__name__)


class TutorRegistrationListener(BaseListener):
    """Handle tutor registration events"""

    async def handle(self, data: Dict[str, Any]):
        """
        Gửi notification cho tất cả admin + coordinator khi tutor tạo profile.

        - Dùng UserRepository để lấy user_ids theo role
        - Dùng NotificationRepository để bulk insert
        - WebSocket push realtime cho users đang online
        """
        try:
            full_name = data.get('full_name', 'Unknown')
            tutor_id  = data.get('tutor_id')
            user_id   = data.get('user_id')
            logger.info(f"New tutor registration: {full_name} (ID: {tutor_id})")

            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                notif_repo = NotificationRepository(db)

                # Get admin + coordinator user IDs via repository
                recipient_ids = await user_repo.get_user_ids_by_roles(['admin', 'coordinator'])

                if not recipient_ids:
                    logger.warning("No admin/coordinator found to notify")
                    return

                # Bulk INSERT via repository
                message = f"{full_name} đã đăng ký làm Tutor. Vui lòng xem xét và phê duyệt."
                await notif_repo.bulk_create([
                    {
                        "user_id": uid,
                        "type":    "tutor_registration",
                        "title":   "Đơn đăng ký Tutor mới",
                        "message": message,
                        "data":    {"tutor_id": tutor_id, "user_id": user_id, "status": "pending"},
                        "is_read": False
                    }
                    for uid in recipient_ids
                ])
                await notif_repo.commit()
                logger.info(f"Bulk inserted notifications for {len(recipient_ids)} recipient(s)")

                # WebSocket push for online users
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

        - Dùng UserRepository để lấy coordinator IDs
        - Dùng NotificationRepository để bulk insert
        - WebSocket push realtime
        """
        try:
            subject_name  = data.get('subject_name', '')
            subject_code  = data.get('subject_code', '')
            full_name     = data.get('full_name', 'Unknown')
            tutor_user_id = data.get('user_id')
            logger.info(f"New subject registration: {full_name} for {subject_code} - {subject_name}")

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
                user_repo = UserRepository(db)
                notif_repo = NotificationRepository(db)

                # Get coordinator IDs via repository
                coordinator_ids = await user_repo.get_user_ids_by_roles(['coordinator'])

                if coordinator_ids:
                    # Bulk INSERT for coordinators via repository
                    await notif_repo.bulk_create([
                        {
                            "user_id": uid,
                            "type":    "subject_registration",
                            "title":   "Đơn đăng ký dạy môn mới",
                            "message": coord_message,
                            "data":    notification_meta,
                            "is_read": False
                        }
                        for uid in coordinator_ids
                    ])
                    logger.info(f"Bulk inserted notifications for {len(coordinator_ids)} coordinator(s)")

                # Confirmation notification for tutor via repository
                await notif_repo.create(
                    user_id=tutor_user_id,
                    type="subject_registration_submitted",
                    title="Đơn đăng ký đã được gửi",
                    message=tutor_message,
                    data=notification_meta,
                )
                await notif_repo.commit()

                # WebSocket push for online coordinators
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

                # WebSocket confirmation for tutor
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
        
        Expected data:
            - user_id: int
            - registration_id: int
            - tutor_id: int
            - subject_id: int
            - subject_name: str
            - status: str ('approved' or 'rejected')
            - reason: str (optional, for rejection)
        """
        try:
            user_id = data.get('user_id')
            subject_name = data.get('subject_name', 'môn học')
            approval_status = data.get('status', 'approved')
            
            logger.info(f"Registration {approval_status}: user_id={user_id}, subject={subject_name}")
            
            async with AsyncSessionLocal() as db:
                notif_repo = NotificationRepository(db)

                if approval_status == 'approved':
                    await notif_repo.create(
                        user_id=user_id,
                        type='registration_approved',
                        title='Đơn đăng ký môn học được phê duyệt',
                        message=f'Chúc mừng! Đơn đăng ký dạy môn {subject_name} của bạn đã được phê duyệt.',
                        data={
                            "registration_id": data.get('registration_id'),
                            "subject_name": subject_name,
                            "status": "approved"
                        },
                    )
                    logger.info("Registration approved. Tutor can now generate sessions manually.")
                    
                else:  # rejected
                    reason = data.get('reason', 'Không đáp ứng yêu cầu')
                    await notif_repo.create(
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
                    )

                await notif_repo.commit()
                logger.info(f"Created {approval_status} notification for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error creating approval/rejection notification: {e}")


def register_tutor_listeners():
    """Register all tutor-related event listeners"""
    event_bus.register(EventTypes.TUTOR_REGISTERED, TutorRegistrationListener().execute)
    event_bus.register(EventTypes.TUTOR_SUBJECT_REGISTERED, TutorSubjectRegistrationListener().execute)
    event_bus.register(EventTypes.REGISTRATION_APPROVED, TutorApprovalListener().execute)
    event_bus.register(EventTypes.REGISTRATION_REJECTED, TutorApprovalListener().execute)
    logger.info("Tutor event listeners registered")
