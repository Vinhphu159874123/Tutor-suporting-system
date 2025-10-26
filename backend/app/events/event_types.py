"""
Event Type Constants
Centralized event names to avoid typos
"""

class EventTypes:
    """Event type constants for type safety"""
    
    # Session Events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    SESSION_COMPLETED = "session.completed"
    SESSION_CANCELLED = "session.cancelled"
    
    # Student Events
    STUDENT_REGISTERED = "student.registered"
    STUDENT_UPDATED = "student.updated"
    TUTOR_REQUESTED = "student.tutor_requested"
    FEEDBACK_SUBMITTED = "student.feedback_submitted"
    
    # Tutor Events
    TUTOR_REGISTERED = "tutor.registered"
    TUTOR_UPDATED = "tutor.updated"
    TUTOR_AVAILABILITY_SET = "tutor.availability_set"
    
    # Admin Events
    USER_ROLE_CHANGED = "admin.user_role_changed"
    REGISTRATION_APPROVED = "admin.registration_approved"
    REGISTRATION_REJECTED = "admin.registration_rejected"
    
    # Forum Events
    POST_CREATED = "forum.post_created"
    COMMENT_CREATED = "forum.comment_created"
    POST_VOTED = "forum.post_voted"
    
    # System Events
    NOTIFICATION_SENT = "system.notification_sent"
    EMAIL_SENT = "system.email_sent"
    STATISTICS_UPDATED = "system.statistics_updated"
