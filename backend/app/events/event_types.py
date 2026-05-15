"""
Event Type Constants
Centralized event names — only events with active listeners are listed.
"""

class EventTypes:
    """Event type constants for type safety"""
    
    # Session Events
    SESSION_CREATED = "session.created"
    
    # Student Events
    STUDENT_ENROLLED_COURSE = "student.enrolled_course"
    
    # Tutor Events
    TUTOR_REGISTERED = "tutor.registered"
    TUTOR_SUBJECT_REGISTERED = "tutor.subject_registered"
    
    # Coordinator Events
    REGISTRATION_APPROVED = "admin.registration_approved"
    REGISTRATION_REJECTED = "admin.registration_rejected"
