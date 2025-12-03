# HCMUT Tutor Support System - Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Docker & Docker Compose installed
- Supabase account or PostgreSQL database
- Domain name (optional, for HTTPS)

### Step 1: Environment Configuration

1. Copy the environment template:
```bash
cp .env.prod.template .env.prod
```

2. Edit `.env.prod` and fill in actual values:
```bash
# Database - Get from Supabase dashboard
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_ANON_KEY=[YOUR_ANON_KEY]

# Security - Generate a secure random key
JWT_SECRET_KEY=$(openssl rand -hex 32)

# HCMUT Services
HCMUT_SSO_URL=https://sso.hcmut.edu.vn
HCMUT_DATACORE_URL=https://datacore.hcmut.edu.vn
HCMUT_LIBRARY_URL=https://library.hcmut.edu.vn

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com  # or http://your-server-ip:8000
```

### Step 2: Database Setup

1. Run database migrations on Supabase:
```bash
# Upload supabase_migration.sql to Supabase SQL Editor
# Or connect and run:
psql $DATABASE_URL < supabase_migration.sql
```

2. Create admin account:
```bash
docker-compose -f docker-compose.prod.yml run --rm backend python create_admin.py
```

### Step 3: Build and Start Services

#### Option A: Production with Mock HCMUT Services
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start with mock services
docker-compose -f docker-compose.prod.yml --profile mock up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Option B: Production with Real HCMUT Services
```bash
# Start without mock services
docker-compose -f docker-compose.prod.yml up -d
```

### Step 4: Verify Deployment

1. Check service health:
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:80/health

# Redis health
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

2. Access the application:
- Frontend: http://localhost (or your domain)
- Backend API: http://localhost:8000/docs
- Admin login: admin@hcmut.edu.vn / admin123

### Step 5: Production Optimizations

#### Enable HTTPS with Let's Encrypt (Recommended)

1. Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Get SSL certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. Update `docker-compose.prod.yml` frontend ports:
```yaml
ports:
  - "80:80"
  - "443:443"
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

#### Configure Firewall
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend (if needed externally)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

#### Set up Monitoring (Optional)

1. View logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

2. Monitor resources:
```bash
docker stats
```

### Step 6: Backup Strategy

#### Database Backup
```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec -T backend \
  pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore database
psql $DATABASE_URL < backup_20240101.sql
```

#### Redis Backup
```bash
# Redis auto-saves to /data (mounted as volume)
# Copy backup
docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/appendonly.aof ./redis_backup.aof
```

## 🔄 Maintenance Commands

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# View logs to verify
docker-compose -f docker-compose.prod.yml logs -f
```

### Database Migrations
```bash
# Run migration script
docker-compose -f docker-compose.prod.yml exec backend python run_migration.py

# Or connect to database
docker-compose -f docker-compose.prod.yml exec backend psql $DATABASE_URL
```

### Reset Admin Password
```bash
docker-compose -f docker-compose.prod.yml exec backend python reset_admin_password.py
```

### Stop Services
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.prod.yml down -v
```

## 📊 Performance Tuning

### Backend Workers
Edit `backend/Dockerfile.prod` to adjust Gunicorn workers:
```dockerfile
# Formula: (2 x CPU cores) + 1
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     ...
```

### Nginx Caching
Edit `frontend/nginx.conf` to adjust cache settings.

### Database Connection Pool
Edit `backend/app/core/database.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_size=20,  # Adjust based on load
    max_overflow=40
)
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common issues:
# - Database connection: verify DATABASE_URL
# - Missing dependencies: rebuild image
# - Port conflict: check if 8000 is available
```

### Frontend shows API errors
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check REACT_APP_API_URL in .env.prod
# Check CORS settings in backend
```

### Database connection errors
```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python -c \
  "from app.core.database import test_connection; import asyncio; asyncio.run(test_connection())"
```

## 📱 Development Mode

To run in development mode (with hot reload):
```bash
docker-compose up -d
```

This uses the original `docker-compose.yml` with:
- Backend auto-reload on code changes
- Frontend hot reload
- Volume mounts for live coding

## 🔐 Security Checklist

- [ ] Changed default admin password
- [ ] Set strong JWT_SECRET_KEY
- [ ] Configured HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Updated ALLOWED_ORIGINS in production
- [ ] Disabled DEBUG mode
- [ ] Using environment variables (not hardcoded secrets)
- [ ] Non-root Docker users configured
- [ ] Regular security updates

## 📞 Support

For issues, check:
1. Docker logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Service health endpoints
3. Database connectivity
4. Environment variables configuration
