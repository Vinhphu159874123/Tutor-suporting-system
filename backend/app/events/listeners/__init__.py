"""
Event Listeners Package
Import and register all listeners
"""
from app.events.listeners.session_listener import register_session_listeners
from app.events.listeners.notification_listener import NotificationListener, EmailListener
from app.events.listeners.tutor_listener import register_tutor_listeners
from app.events.listeners.enrollment_listener import register_enrollment_listeners

# Auto-register listeners when imported
def register_all_listeners():
    """Register all event listeners with event bus"""
    register_session_listeners()
    register_tutor_listeners()
    register_enrollment_listeners()
    # Add more listener registrations here as needed

__all__ = [
    "register_all_listeners",
    "NotificationListener",
    "EmailListener"
]
