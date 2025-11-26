# Quick Deployment Reference

## Railway (Backend) - Quick Steps

1. **Create Project**: [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. **Set Environment Variables**:
   ```
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=your_host
   DB_PORT=5432
   DB_NAME=postgres
   DB_SCHEMA=public
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```
3. **Deploy**: Railway auto-deploys on push
4. **Get URL**: Copy Railway URL (e.g., `https://xxx.up.railway.app`)

## Vercel (Frontend) - Quick Steps

1. **Create Project**: [vercel.com](https://vercel.com) → Add New Project → Import GitHub repo
2. **Configure**:
   - Root Directory: `frontend`
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. **Set Environment Variable**:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```
4. **Deploy**: Click Deploy
5. **Update Backend CORS**: Add Vercel URL to Railway `ALLOWED_ORIGINS`

## Environment Variables Checklist

### Railway (Backend)
- [ ] `DB_USER`
- [ ] `DB_PASSWORD`
- [ ] `DB_HOST`
- [ ] `DB_PORT`
- [ ] `DB_NAME`
- [ ] `DB_SCHEMA`
- [ ] `ALLOWED_ORIGINS` (update after frontend deploy)

### Vercel (Frontend)
- [ ] `VITE_API_URL` (Railway backend URL)

## Testing

- Backend: `https://your-backend.up.railway.app/api/health`
- Frontend: `https://your-frontend.vercel.app`
- API Docs: `https://your-backend.up.railway.app/docs`

## Common Issues

**CORS Error**: Update `ALLOWED_ORIGINS` in Railway to include Vercel URL

**Frontend can't connect**: Verify `VITE_API_URL` is set correctly in Vercel

**Database connection failed**: Check Railway environment variables match your database

