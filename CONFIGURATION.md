# Configuration Guide - Railway, Vercel, and Local

This document explains how the application works in each environment.

## ✅ Current Configuration Status

The application is configured to work seamlessly across all three environments:

### 🚂 Railway (Backend)
- ✅ Uses `$PORT` environment variable (automatically set by Railway)
- ✅ Database credentials from environment variables
- ✅ CORS configured via `ALLOWED_ORIGINS` environment variable
- ✅ Minimal dependencies in `requirements.txt`

### ▲ Vercel (Frontend)
- ✅ Uses `VITE_API_URL` environment variable
- ✅ Builds static files to `dist/` directory
- ✅ SPA routing configured in `vercel.json`

### 💻 Local Development
- ✅ Backend defaults to `localhost:8000`
- ✅ Frontend defaults to `localhost:8000` for API calls
- ✅ Vite proxy configured for local development
- ✅ Database defaults to localhost (or AWS RDS if configured)

## Environment Variable Configuration

### Backend (Railway)

| Variable | Local Default | Railway Required | Description |
|----------|---------------|------------------|-------------|
| `PORT` | N/A | ✅ Auto-set | Railway automatically sets this |
| `DB_USER` | `postgres` | ✅ Yes | PostgreSQL username |
| `DB_PASSWORD` | `rootpassword` | ✅ Yes | PostgreSQL password |
| `DB_HOST` | AWS RDS default | ✅ Yes | Database host |
| `DB_PORT` | `5432` | Optional | Database port |
| `DB_NAME` | `postgres` | Optional | Database name |
| `DB_SCHEMA` | `public` | Optional | Database schema |
| `ALLOWED_ORIGINS` | localhost URLs | ✅ Yes | Comma-separated CORS origins |

### Frontend (Vercel)

| Variable | Local Default | Vercel Required | Description |
|----------|---------------|------------------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | ✅ Yes | Backend API URL |

## How It Works

### 🚂 Railway Deployment

1. **Port Configuration**: Railway sets `PORT` automatically
   - Procfile: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Railway injects `$PORT` at runtime

2. **Database**: Uses environment variables
   - No hardcoded credentials
   - Works with any PostgreSQL database

3. **CORS**: Configured via `ALLOWED_ORIGINS`
   - Set in Railway dashboard
   - Include Vercel URL after frontend deployment

### ▲ Vercel Deployment

1. **API URL**: Uses `VITE_API_URL` environment variable
   - Set in Vercel dashboard
   - Points to Railway backend URL
   - Example: `https://your-backend.up.railway.app`

2. **Build Process**:
   - Runs `npm run build`
   - Outputs to `dist/` directory
   - Serves static files

3. **Routing**: `vercel.json` handles SPA routing
   - All routes redirect to `index.html`
   - Client-side routing works correctly

### 💻 Local Development

1. **Backend**:
   ```bash
   cd backend
   python main.py
   # Runs on http://localhost:8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   # Runs on http://localhost:3000
   ```

3. **API Connection**:
   - Development: Uses Vite proxy (configured in `vite.config.ts`)
   - Production build: Uses `VITE_API_URL` environment variable

## Configuration Files

### Backend Files

- **`Procfile`**: Railway start command
- **`railway.json`**: Railway build/deploy configuration
- **`requirements.txt`**: Minimal Python dependencies
- **`main.py`**: CORS configured with environment variable support
- **`database.py`**: Database connection with environment variable defaults

### Frontend Files

- **`vercel.json`**: Vercel deployment configuration
- **`vite.config.ts`**: Local development proxy configuration
- **`src/api/client.ts`**: API client with environment variable support

## Testing Each Environment

### Test Railway Backend

```bash
# Health check
curl https://your-backend.up.railway.app/api/health

# API docs
open https://your-backend.up.railway.app/docs
```

### Test Vercel Frontend

```bash
# Open in browser
open https://your-frontend.vercel.app

# Check browser console for API calls
```

### Test Local

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Open browser
open http://localhost:3000
```

## Common Issues & Solutions

### Issue: CORS Error in Production

**Solution**: Update `ALLOWED_ORIGINS` in Railway to include Vercel URL:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-app.vercel.app
```

### Issue: Frontend Can't Connect to Backend

**Solution**: Verify `VITE_API_URL` is set correctly in Vercel:
- Should be: `https://your-backend.up.railway.app`
- No trailing slash
- Must be HTTPS (not HTTP)

### Issue: Database Connection Failed

**Solution**: Check Railway environment variables:
- All database variables must be set
- Verify database is accessible from Railway
- Check database credentials are correct

### Issue: Port Already in Use (Local)

**Solution**: Change port in `main.py` or kill existing process:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Environment-Specific Notes

### Railway
- ✅ Automatically handles HTTPS
- ✅ Provides `$PORT` environment variable
- ✅ Supports PostgreSQL addon
- ✅ Auto-deploys on git push (if configured)

### Vercel
- ✅ Automatically handles HTTPS
- ✅ Provides CDN for static assets
- ✅ Supports environment variables
- ✅ Auto-deploys on git push (if configured)

### Local
- ⚠️ Uses HTTP (not HTTPS)
- ⚠️ Requires manual database setup
- ✅ Fast development iteration
- ✅ Full debugging capabilities

## Next Steps

1. **Deploy Backend to Railway**:
   - Set environment variables
   - Get Railway URL

2. **Deploy Frontend to Vercel**:
   - Set `VITE_API_URL` to Railway URL
   - Get Vercel URL

3. **Update Backend CORS**:
   - Add Vercel URL to `ALLOWED_ORIGINS` in Railway

4. **Test Everything**:
   - Verify frontend connects to backend
   - Test API endpoints
   - Check CORS is working

