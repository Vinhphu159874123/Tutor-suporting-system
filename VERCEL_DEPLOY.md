# Deploy Frontend to Vercel

## ▲ Bước 1: Prepare Frontend

Tạo file cấu hình Vercel:

**File đã tạo sẵn:** `vercel.json` ở root của project

## 🚀 Bước 2: Deploy to Vercel

### Option A: Deploy qua Vercel Dashboard (Khuyến nghị)

1. Truy cập https://vercel.com
2. Sign in với GitHub
3. Click **"Add New..."** → **"Project"**
4. Import repository: `Vinhphu159874123/Tutor-suporting-system`
5. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

### Option B: Deploy qua Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy từ thư mục frontend
cd frontend
vercel --prod
```

## 🔧 Bước 3: Configure Environment Variables

Trong Vercel Project Settings → **"Environment Variables"**, thêm:

```env
# Backend API URL (từ Railway)
REACT_APP_API_URL=https://your-backend.railway.app/api/v1

# Supabase (nếu dùng)
REACT_APP_SUPABASE_URL=https://lrycytjxsufexhybzkkr.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxyeWN5dGp4c3VmZXhoeWJ6a2tyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0OTA0MDEsImV4cCI6MjA3NzA2NjQwMX0.he9yKDhS8XS1a_hMAGF0My6wur0X82-VQtPMw5vUzN0
```

**Lưu ý:** Thay `https://your-backend.railway.app` bằng URL thật từ Railway

## 🔄 Bước 4: Update Backend CORS

Quay lại Railway, update `ALLOWED_ORIGINS`:

```env
ALLOWED_ORIGINS=https://your-app.vercel.app,https://tutor-system.vercel.app
```

Redeploy backend trên Railway để apply changes.

## ✅ Bước 5: Verify Deployment

1. Truy cập Vercel URL: `https://your-app.vercel.app`
2. Test login với mock account
3. Kiểm tra API calls trong Browser DevTools → Network tab
4. Verify không có CORS errors

## 🔗 Bước 6: Setup Custom Domain (Optional)

1. Vào Vercel Project → **"Settings"** → **"Domains"**
2. Add domain: `tutor.yourdomain.com`
3. Update DNS records theo hướng dẫn Vercel
4. Update Railway `ALLOWED_ORIGINS` với domain mới

---

## 📝 Notes

- Vercel free tier: Unlimited deployments, bandwidth limits
- Auto deploy khi push code lên GitHub
- Preview deployments cho mỗi PR
- Nếu build lâu, check logs trong Vercel Dashboard
- Environment variables chỉ apply sau khi redeploy

## 🐛 Troubleshooting

### Build fails với "Cannot find module"
```bash
# Chạy local để test
cd frontend
npm install
npm run build
```

### API calls fail (404/CORS)
- Check `REACT_APP_API_URL` có đúng không
- Verify Railway backend đang chạy
- Check `ALLOWED_ORIGINS` trên Railway có domain Vercel

### Blank page sau deploy
- Open Browser Console → Check errors
- Verify `REACT_APP_API_URL` có `/api/v1` ở cuối
- Check Vercel build logs
