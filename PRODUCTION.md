# Production Deployment - Quick Reference

## 🚀 Quick Deploy

```bash
# 1. Configure environment
cp .env.prod.template .env.prod
nano .env.prod  # Fill in your values

# 2. Deploy
./deploy.sh

# Select option:
# 1 = Production (real HCMUT services)
# 2 = Production with mock services
```

## 📋 What Was Created

### Production Files
- **docker-compose.prod.yml** - Production orchestration
- **backend/Dockerfile.prod** - Multi-stage backend build
- **frontend/Dockerfile.prod** - Multi-stage frontend with Nginx
- **frontend/nginx.conf** - Nginx reverse proxy config
- **.env.prod.template** - Environment variables template
- **DEPLOYMENT.md** - Full deployment documentation
- **deploy.sh** - Automated deployment script

### Optimizations Applied
✅ **Multi-stage builds** - Smaller production images
✅ **Non-root users** - Security hardening
✅ **Gunicorn workers** - Production WSGI server
✅ **Nginx static serving** - Fast frontend delivery
✅ **Health checks** - Service monitoring
✅ **Restart policies** - Auto-recovery
✅ **.dockerignore files** - Faster builds
✅ **Environment variables** - No hardcoded secrets
✅ **Gzip compression** - Reduced bandwidth
✅ **Static asset caching** - Better performance

## 🔍 Key Differences: Dev vs Prod

| Feature | Development | Production |
|---------|-------------|------------|
| **Backend Server** | Uvicorn with --reload | Gunicorn + Uvicorn workers |
| **Frontend Server** | npm start (webpack dev) | Nginx serving static build |
| **Image Size** | ~1.5GB (with dev deps) | ~400MB (optimized) |
| **Hot Reload** | ✅ Enabled | ❌ Disabled |
| **Source Code** | Mounted volumes | Copied into image |
| **Security** | Permissive CORS | Configured origins |
| **Logging** | Verbose debug | Structured production |
| **Database Pool** | Small pool | Optimized pool size |

## ⚡ Quick Commands

```bash
# Start production
docker-compose -f docker-compose.prod.yml up -d

# Start with mock services
docker-compose -f docker-compose.prod.yml --profile mock up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop everything
docker-compose -f docker-compose.prod.yml down

# Rebuild after code changes
docker-compose -f docker-compose.prod.yml up -d --build

# Check service health
curl http://localhost:8000/health  # Backend
curl http://localhost:80/health    # Frontend

# Database backup
docker-compose -f docker-compose.prod.yml exec -T backend \
  pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## 🔐 Security Checklist

Before deploying to production:

- [ ] Copy `.env.prod.template` to `.env.prod`
- [ ] Set strong `JWT_SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Update `DATABASE_URL` with your Supabase credentials
- [ ] Configure `ALLOWED_ORIGINS` with your domain
- [ ] Change default admin password after first login
- [ ] Set `ENVIRONMENT=production` in `.env.prod`
- [ ] Review and update HCMUT service URLs
- [ ] Enable HTTPS with SSL certificate (see DEPLOYMENT.md)
- [ ] Set up firewall rules
- [ ] Configure regular database backups

## 🌐 Deployment Scenarios

### Local Testing (Mock Services)
```bash
./deploy.sh
# Choose option 2
# Access: http://localhost
```

### Production (Real HCMUT Services)
```bash
# Configure .env.prod with real service URLs
./deploy.sh
# Choose option 1
```

### Cloud Deployment (AWS/GCP/Azure)
1. Provision a VM with Docker
2. Clone repository
3. Configure `.env.prod` with cloud database
4. Run `./deploy.sh`
5. Set up SSL with Let's Encrypt
6. Configure domain DNS

## 📊 Resource Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB
- **Network**: 10Mbps

### Recommended (Production)
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 50GB SSD
- **Network**: 100Mbps
- **Database**: Managed service (Supabase)

## 🐛 Common Issues

### Backend won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Common fixes:
# 1. Verify DATABASE_URL in .env.prod
# 2. Check Gunicorn worker count (reduce if low RAM)
# 3. Ensure port 8000 is free
```

### Frontend shows blank page
```bash
# Check if REACT_APP_API_URL is set correctly
# Rebuild frontend
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

### Database connection timeout
```bash
# Test database from backend container
docker-compose -f docker-compose.prod.yml exec backend \
  python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); print(engine.connect())"
```

## 📚 Documentation

- **Full Guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
- **API Docs**: http://localhost:8000/docs (after deployment)
- **Architecture**: See [backend/docs/ARCHITECTURE_GUIDE.md](./backend/docs/ARCHITECTURE_GUIDE.md)

## 🎯 Next Steps

After successful deployment:

1. **Verify Services**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:80/health
   ```

2. **Login as Admin**
   - URL: http://localhost
   - Email: admin@hcmut.edu.vn
   - Password: admin123
   - **⚠️ Change this immediately!**

3. **Create Test Accounts** (optional)
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python create_test_accounts.py
   ```

4. **Set up Monitoring**
   - Configure log aggregation
   - Set up uptime monitoring
   - Enable database backups

5. **Configure Domain & SSL** (for production)
   - Point domain to your server
   - Install SSL certificate
   - Update ALLOWED_ORIGINS

## 💡 Tips

- Use `--build` flag when code changes
- Monitor logs regularly: `docker-compose -f docker-compose.prod.yml logs -f`
- Keep backups before major updates
- Test in staging environment first
- Use `docker system prune` to clean up old images

---

**Need help?** Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.
