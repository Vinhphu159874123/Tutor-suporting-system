# Quick Deploy Guide - Railway + Vercel

## 📋 Tóm tắt nhanh

### 🚂 RAILWAY (Backend)

1. **Tạo Railway Project:**
   - Truy cập https://railway.app
   - New Project → Deploy from GitHub
   - Chọn repo: `Vinhphu159874123/Tutor-suporting-system`

2. **Add PostgreSQL:**
   - Click "+ New" → Database → PostgreSQL
   - Railway tự tạo `DATABASE_URL`

3. **Set Environment Variables:**
   ```env
   SUPABASE_URL=https://lrycytjxsufexhybzkkr.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   JWT_SECRET_KEY=aAlsINL4Grx1wyv6M_Ha1fzXsgbCxzMy5R0vum2igLqg2w9P80y2GUfnIqvOybhlPgSAjB9oeFghIL0kVAzusQ
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   API_V1_STR=/api/v1
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

4. **Configure Build:**
   - Root Directory: Để trống
   - Dockerfile Path: `backend/Dockerfile.prod`
   - Deploy!

5. **Copy Backend URL:** 
   - Ví dụ: `https://tutor-backend-production.up.railway.app`

### ▲ VERCEL (Frontend)

1. **Deploy Frontend:**
   - Truy cập https://vercel.com
   - New Project → Import từ GitHub
   - Chọn repo: `Vinhphu159874123/Tutor-suporting-system`

2. **Configure:**
   - Framework: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output: `build`

3. **Set Environment Variables:**
   ```env
   REACT_APP_API_URL=https://your-railway-backend.up.railway.app/api/v1
   REACT_APP_SUPABASE_URL=https://lrycytjxsufexhybzkkr.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Deploy!**

5. **Update Railway CORS:**
   - Quay lại Railway
   - Update `ALLOWED_ORIGINS` với Vercel URL
   - Redeploy backend

### ✅ Verify

- **Backend**: https://your-backend.railway.app/health
- **Frontend**: https://your-app.vercel.app
- **API Docs**: https://your-backend.railway.app/api/v1/docs

---

## 📁 Files đã tạo sẵn:

- ✅ `railway.json` - Railway config
- ✅ `backend/railway.toml` - Backend Railway settings
- ✅ `vercel.json` - Vercel config
- ✅ `RAILWAY_DEPLOY.md` - Hướng dẫn chi tiết Railway
- ✅ `VERCEL_DEPLOY.md` - Hướng dẫn chi tiết Vercel
- ✅ `backend/Dockerfile.prod` - Đã fix cho Railway PORT

## 🔄 Next Steps:

1. Push code lên GitHub
2. Deploy backend lên Railway
3. Copy Railway URL
4. Deploy frontend lên Vercel với Railway URL
5. Update CORS trên Railway
6. Test!

Chi tiết xem trong `RAILWAY_DEPLOY.md` và `VERCEL_DEPLOY.md`
