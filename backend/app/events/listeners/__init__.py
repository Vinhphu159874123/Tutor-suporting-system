"""
Event Listeners Package
Import and register all listeners
"""
from app.events.listeners.session_listener import register_session_listeners
from app.events.listeners.notification_listener import NotificationListener, EmailListener
from app.events.listeners.statistics_listener import StatisticsListener, AuditLogListener

# Auto-register listeners when imported
def register_all_listeners():
    """Register all event listeners with event bus"""
    register_session_listeners()
    # Add more listener registrations here as needed

__all__ = [
    "register_all_listeners",
    "NotificationListener",
    "EmailListener",
    "StatisticsListener",
    "AuditLogListener"
]
