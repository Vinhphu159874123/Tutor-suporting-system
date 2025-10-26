"""
Base Listener Class
Template for creating event listeners
"""
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseListener(ABC):
    """
    Base class for event listeners
    Provides common functionality and structure
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def handle(self, data: Any):
        """
        Handle event data
        Must be implemented by subclasses
        
        Args:
            data: Event data passed from event emitter
        """
        pass
    
    async def on_error(self, error: Exception, data: Any):
        """
        Handle errors in event processing
        Can be overridden by subclasses for custom error handling
        
        Args:
            error: The exception that occurred
            data: The event data that caused the error
        """
        self.logger.error(
            f"Error processing event in {self.__class__.__name__}: {error}",
            exc_info=True
        )
    
    async def before_handle(self, data: Any):
        """
        Hook called before handle()
        Can be overridden for preprocessing
        """
        pass
    
    async def after_handle(self, data: Any):
        """
        Hook called after handle()
        Can be overridden for cleanup or logging
        """
        pass
    
    async def execute(self, data: Any):
        """
        Main execution method with lifecycle hooks
        Called by event bus
        """
        try:
            await self.before_handle(data)
            await self.handle(data)
            await self.after_handle(data)
        except Exception as e:
            await self.on_error(e, data)
