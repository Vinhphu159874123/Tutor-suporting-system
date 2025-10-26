# Event System Documentation

## 📦 Overview

Event-driven architecture cho Tutor Support System. Services emit events, listeners xử lý side effects asynchronously.

## 🏗️ Architecture

```
Routes → Services (emit events) → Repositories → Database
                ↓
          Event Bus (async)
                ↓
          Listeners (side effects)
            - Notifications
            - Emails
            - Statistics
            - Audit logs
```

## 📂 Structure

```
app/events/
├── __init__.py                 # Package exports
├── event_bus.py                # Event dispatcher
├── event_types.py              # Event constants
├── base_listener.py            # Base listener class
└── listeners/
    ├── __init__.py
    ├── session_listener.py     # Session events
    ├── notification_listener.py # Notifications & emails
    └── statistics_listener.py   # Stats & audit logs
```

## 🎯 Event Types

### Session Events
- `SESSION_CREATED` - New session created
- `SESSION_COMPLETED` - Session marked complete
- `SESSION_CANCELLED` - Session cancelled

### Student Events
- `STUDENT_REGISTERED` - New student registered
- `TUTOR_REQUESTED` - Student requests tutor
- `FEEDBACK_SUBMITTED` - Student submits feedback

### Tutor Events
- `TUTOR_REGISTERED` - New tutor registered
- `TUTOR_AVAILABILITY_SET` - Tutor updates availability

## 💻 Usage Examples

### Emitting Events in Services

```python
from app.events import event_bus, EventTypes

async def create_session(self, session_data: SessionCreate):
    # 1. Execute core business logic
    session = await self.session_repo.create(data)
    
    # 2. Emit event (fire-and-forget, non-blocking)
    await event_bus.emit(EventTypes.SESSION_CREATED, {
        "session_id": session.id,
        "tutor_id": session.tutor_id,
        "student_id": session.student_id
    })
    
    # 3. Return immediately
    return SessionResponse.model_validate(session)
```

### Creating Custom Listeners

```python
from app.events.base_listener import BaseListener
from app.events import event_bus, EventTypes

class MyCustomListener(BaseListener):
    async def handle(self, data: dict):
        # Your async logic here
        user_id = data.get("user_id")
        await send_email(user_id)
        await update_stats(user_id)

# Register listener
listener = MyCustomListener()
event_bus.register(EventTypes.SESSION_CREATED, listener.execute)
```

### Using Decorator Style

```python
from app.events import event_bus, EventTypes

@event_bus.on(EventTypes.SESSION_CREATED)
async def handle_session_created(data: dict):
    # Handle event
    print(f"Session created: {data['session_id']}")
```

## ⚡ Current Status

### ✅ Implemented
- Event bus system (async, fire-and-forget)
- Base listener class with lifecycle hooks
- Event type constants
- Listener registration
- Services emit events

### ⚠️ PLACEHOLDER (Not Implemented)
All listeners are placeholders - they log but don't execute:
- Email sending
- Push notifications
- Statistics updates
- Audit logging

## 🔧 Implementation Guide

### To Implement a Listener:

1. **Open listener file** (e.g., `session_listener.py`)

2. **Replace placeholder with real logic:**
```python
async def handle(self, data: Dict[str, Any]):
    # BEFORE (Placeholder)
    logger.info(f"[PLACEHOLDER] Session created")
    
    # AFTER (Real implementation)
    session_id = data["session_id"]
    student_id = data["student_id"]
    
    # Send email
    await email_service.send_notification(
        to=student_id,
        subject="Session Confirmed",
        template="session_created"
    )
```

3. **No need to change services** - events already emitted!

## 🧪 Testing

### Disable Events in Tests
```python
from app.events import event_bus

# In test setup
event_bus.disable()

# Run tests
...

# In test teardown
event_bus.enable()
```

### Test Listener Independently
```python
from app.events.listeners.session_listener import SessionCreatedListener

async def test_session_listener():
    listener = SessionCreatedListener()
    await listener.handle({
        "session_id": 123,
        "tutor_id": 1,
        "student_id": 2
    })
```

## 🚀 Benefits

✅ **Non-blocking** - API responses fast (~200ms)  
✅ **Decoupled** - Services don't know about notifications/emails  
✅ **Scalable** - Easy to add new listeners  
✅ **Testable** - Test services and listeners separately  
✅ **Extensible** - Add features without changing core logic  

## 📊 Performance

- **Event emission**: < 1ms (async create_task)
- **API response**: Not affected (fire-and-forget)
- **Listener execution**: Runs in background
- **Error handling**: Listener failures don't affect main flow

## 🔮 Future Enhancements

- [ ] Redis event bus for distributed systems
- [ ] Event replay for debugging
- [ ] Event persistence for audit
- [ ] Retry mechanism for failed listeners
- [ ] Event versioning
- [ ] Dead letter queue for failed events

## 📝 Event Data Schemas

### SESSION_CREATED
```python
{
    "session_id": int,
    "tutor_id": int,
    "student_id": int,
    "subject": str,
    "start_time": str (ISO format)
}
```

### STUDENT_REGISTERED
```python
{
    "student_id": int,
    "user_id": int,
    "email": str,
    "full_name": str
}
```

### TUTOR_REGISTERED
```python
{
    "tutor_id": int,
    "user_id": int,
    "email": str,
    "full_name": str,
    "subjects": List[str]
}
```

---

**Created**: 2025-10-27  
**Status**: Structure implemented, listeners are placeholders  
**Next Step**: Implement real notification/email logic when needed
