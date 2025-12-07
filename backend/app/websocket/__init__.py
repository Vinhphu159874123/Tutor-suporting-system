"""
WebSocket module for real-time communication
"""
from .manager import ConnectionManager

manager = ConnectionManager()

__all__ = ["manager", "ConnectionManager"]
