"""
Event Bus - Simple Event Dispatcher
Manages event emission and listener registration
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class EventBus:
    """
    Simple in-memory event bus for async event handling
    Events are processed asynchronously without blocking the main flow
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._enabled = True  # Can disable for testing
    
    def on(self, event_name: str):
        """
        Decorator to register event listener
        
        Usage:
            @event_bus.on("session.created")
            async def handle_session_created(data: dict):
                # Handle event
                pass
        """
        def decorator(func: Callable):
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(func)
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def register(self, event_name: str, handler: Callable):
        """
        Programmatically register event listener
        
        Args:
            event_name: Name of the event (e.g., "session.created")
            handler: Async function to handle the event
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)
        logger.info(f"Registered listener for event: {event_name}")
    
    async def emit(self, event_name: str, data: Any = None):
        """
        Emit event asynchronously (fire-and-forget)
        
        Args:
            event_name: Name of the event
            data: Event data to pass to listeners
        
        Note: This method returns immediately without waiting for listeners
        """
        if not self._enabled:
            return
        
        if event_name not in self._listeners:
            logger.debug(f"No listeners registered for event: {event_name}")
            return
        
        # Create background task for each listener (non-blocking)
        for listener in self._listeners[event_name]:
            asyncio.create_task(self._execute_listener(listener, event_name, data))
    
    async def _execute_listener(self, listener: Callable, event_name: str, data: Any):
        """
        Execute listener with error handling
        Errors in listeners don't affect main flow
        """
        try:
            # Check if listener is a class instance with handle method
            if hasattr(listener, 'handle'):
                await listener.handle(data)
                listener_name = listener.__class__.__name__
            else:
                # Direct callable function
                await listener(data)
                listener_name = getattr(listener, '__name__', str(listener))
            
            logger.debug(f"Event '{event_name}' processed by {listener_name}")
        except Exception as e:
            listener_name = getattr(listener, '__class__', {}).get('__name__', str(listener))
            logger.error(
                f"Error in listener {listener_name} for event '{event_name}': {e}",
                exc_info=True
            )
    
    def disable(self):
        """Disable event bus (useful for testing)"""
        self._enabled = False
    
    def enable(self):
        """Enable event bus"""
        self._enabled = True
    
    def clear_listeners(self, event_name: str = None):
        """
        Clear listeners for specific event or all events
        Useful for testing
        """
        if event_name:
            self._listeners.pop(event_name, None)
        else:
            self._listeners.clear()
    
    def get_listeners(self, event_name: str) -> List[Callable]:
        """Get all listeners for specific event"""
        return self._listeners.get(event_name, [])


# Global event bus instance
event_bus = EventBus()
