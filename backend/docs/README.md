# 📚 Backend Documentation

## 📖 Available Documentation

### 1. [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - **START HERE**
**Complete guide to backend architecture**
- Layered Architecture Pattern (Routes → Services → Repositories → Database)
- Project structure explanation
- Request flow examples
- Layer responsibilities
- Dependency Injection pattern
- Best practices

**Read this first to understand the system!**

---

### 2. [EVENT_SYSTEM.md](./EVENT_SYSTEM.md)
**Event-driven architecture for async side effects**
- EventBus implementation (fire-and-forget pattern)
- Listener pattern
- Event types and data schemas
- How to emit events from services
- How to create custom listeners
- Testing event handlers

**Read when:** Working with notifications, emails, analytics, or async operations

---

### 3. [NAMING_CONVENTIONS.md](./NAMING_CONVENTIONS.md)
**Why we use `api/` folder instead of `routes/` or `controllers/`**
- Terminology comparison (FastAPI vs Django vs Spring Boot)
- Naming best practices
- REST API conventions
- Layer naming rationale

**Read when:** Questioning folder/file naming choices

---

## 🚀 Quick Start

1. **New to the project?** → Read `ARCHITECTURE_GUIDE.md` first
2. **Adding async features?** → Check `EVENT_SYSTEM.md`
3. **Confused about naming?** → See `NAMING_CONVENTIONS.md`

---

## 📁 File Organization

```
docs/
├── README.md                  # This file
├── ARCHITECTURE_GUIDE.md      # Main architecture documentation
├── EVENT_SYSTEM.md            # Event system guide
└── NAMING_CONVENTIONS.md      # Naming rationale
```

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  ROUTES (api/)          - HTTP endpoints            │
│  ↓                                                   │
│  SERVICES (services/)   - Business logic            │
│  ↓                                                   │
│  REPOSITORIES (repos/)  - Database operations       │
│  ↓                                                   │
│  DATABASE (PostgreSQL)  - Data storage              │
│                                                      │
│  EVENTS (events/)       - Async side effects        │
└─────────────────────────────────────────────────────┘
```

**See ARCHITECTURE_GUIDE.md for detailed diagrams and examples.**

---

## 📝 Documentation Principles

✅ **Keep it simple** - Only essential docs  
✅ **Keep it updated** - Sync with code changes  
✅ **Keep it practical** - Real examples, not theory  
❌ **Avoid duplication** - One source of truth per topic  

---

## 🤝 Contributing

When adding new features:
1. Update relevant documentation
2. Add examples if introducing new patterns
3. Keep docs concise and practical

---

**Happy coding! 🚀**
