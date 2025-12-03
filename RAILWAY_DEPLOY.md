# Deploy Backend to Railway

## 🚂 Bước 1: Tạo Railway Project

1. Truy cập https://railway.app
2. Sign in với GitHub
3. Click **"New Project"**
4. Chọn **"Deploy from GitHub repo"**
5. Chọn repository: `Vinhphu159874123/Tutor-suporting-system`

## 📊 Bước 2: Add PostgreSQL Database

1. Trong Railway project, click **"+ New"**
2. Chọn **"Database"** → **"PostgreSQL"**
3. Railway sẽ tự tạo database và generate `DATABASE_URL`

## 🔧 Bước 3: Configure Environment Variables

Vào **"Variables"** tab và thêm:

```env
# Railway sẽ tự set PORT, không cần thêm
# DATABASE_URL sẽ tự động từ PostgreSQL service

# Supabase (hoặc dùng Railway PostgreSQL)
SUPABASE_URL=https://lrycytjxsufexhybzkkr.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxyeWN5dGp4c3VmZXhoeWJ6a2tyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0OTA0MDEsImV4cCI6MjA3NzA2NjQwMX0.he9yKDhS8XS1a_hMAGF0My6wur0X82-VQtPMw5vUzN0

# JWT Configuration
JWT_SECRET_KEY=aAlsINL4Grx1wyv6M_Ha1fzXsgbCxzMy5R0vum2igLqg2w9P80y2GUfnIqvOybhlPgSAjB9oeFghIL0kVAzusQ
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# HCMUT Services - Mock
HCMUT_SSO_URL=http://localhost:3001
HCMUT_DATACORE_URL=http://localhost:3002
HCMUT_LIBRARY_URL=http://localhost:3003

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
API_V1_STR=/api/v1
PROJECT_NAME=HCMUT Tutor Support System

# CORS - Thêm Vercel domain sau khi deploy
ALLOWED_ORIGINS=https://tutor-system.vercel.app,http://localhost:3000
CORS_ALLOW_CREDENTIALS=true
```

## 🏗️ Bước 4: Configure Build Settings

1. Vào **"Settings"** → **"Build"**
2. **Root Directory**: Để trống (hoặc `/`)
3. **Dockerfile Path**: `backend/Dockerfile.prod`
4. **Start Command**: 
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

## 🗄️ Bước 5: Run Database Migration

Sau khi deploy thành công:

1. Vào **"Settings"** → **"Networking"**
2. Copy **Public Domain** (ví dụ: `tutor-backend.railway.app`)
3. Connect vào PostgreSQL từ Railway Dashboard
4. Run SQL migration:
   ```sql
   -- Copy nội dung từ supabase_migration.sql
   ```

Hoặc dùng Railway CLI:
```bash
railway login
railway link
railway run psql $DATABASE_URL < supabase_migration.sql
```

## ✅ Bước 6: Verify Deployment

1. Truy cập: `https://your-backend.railway.app/health`
2. Xem API docs: `https://your-backend.railway.app/api/v1/docs`
3. Check logs: Railway Dashboard → **"Logs"** tab

## 🔗 Bước 7: Get Backend URL

Copy Public Domain từ Railway (ví dụ: `https://tutor-backend-production.up.railway.app`)

Bạn sẽ cần URL này để configure Vercel frontend.

---

## 📝 Notes

- Railway free tier: 500 hours/month, $5 credit
- Database sẽ sleep sau 30 phút không hoạt động (free tier)
- Nếu dùng Supabase thay vì Railway PostgreSQL, update `DATABASE_URL` trong Variables
- Mock services (SSO, DataCore, Library) sẽ không hoạt động trên Railway - cần deploy riêng hoặc bỏ
