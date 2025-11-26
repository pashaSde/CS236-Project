# Deployment Guide

This guide covers deploying the Hotel Reservations application to Railway (backend) and Vercel (frontend).

## Architecture

- **Backend**: FastAPI application deployed on Railway
- **Frontend**: React/Vite application deployed on Vercel
- **Database**: PostgreSQL (AWS RDS or Railway PostgreSQL)

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **GitHub Repository**: Push your code to GitHub (required for both platforms)

## Backend Deployment (Railway)

### Step 1: Create New Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

**Important**: The project uses Python 3.12 (specified in `runtime.txt`). Railway/Nixpacks will automatically detect this. If you encounter Python version issues, ensure Railway is using Python 3.12, not 3.13.

### Step 2: Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```bash
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=postgres
DB_SCHEMA=public

# CORS Configuration (add your Vercel URL after frontend deployment)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-app.vercel.app
```

**Important**: After deploying the frontend, update `ALLOWED_ORIGINS` to include your Vercel URL.

### Step 3: Deploy

Railway will automatically:
1. Detect Python project
2. Install dependencies from `requirements.txt`
3. Run the app using the `Procfile` or `railway.json` configuration

### Step 4: Get Backend URL

After deployment, Railway will provide a URL like:
```
https://your-app.up.railway.app
```

Copy this URL - you'll need it for the frontend configuration.

### Step 5: Test Backend

Visit your Railway URL:
- Health check: `https://your-app.up.railway.app/api/health`
- API docs: `https://your-app.up.railway.app/docs`

## Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI (Optional)

```bash
npm i -g vercel
```

### Step 2: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 3: Configure Environment Variables

In Vercel dashboard → Project Settings → Environment Variables, add:

```bash
VITE_API_URL=https://your-backend.up.railway.app
```

Replace `https://your-backend.up.railway.app` with your actual Railway backend URL.

### Step 4: Deploy

Click "Deploy" and wait for the build to complete.

### Step 5: Get Frontend URL

Vercel will provide a URL like:
```
https://your-app.vercel.app
```

### Step 6: Update Backend CORS

Go back to Railway and update the `ALLOWED_ORIGINS` environment variable:

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-app.vercel.app
```

Railway will automatically redeploy with the new CORS settings.

## Alternative: Deploy via CLI

### Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Link to existing project (or create new)
railway link

# Set environment variables
railway variables set DB_USER=postgres
railway variables set DB_PASSWORD=your_password
railway variables set DB_HOST=your_host
# ... etc

# Deploy
railway up
```

### Vercel CLI

```bash
# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel

# Set environment variables
vercel env add VITE_API_URL
# Enter: https://your-backend.up.railway.app

# Deploy to production
vercel --prod
```

## Database Setup

### Option 1: Use Existing AWS RDS Database

If you already have an AWS RDS PostgreSQL database:
1. Ensure it's publicly accessible (or configure Railway IP whitelist)
2. Use the RDS endpoint in Railway environment variables

### Option 2: Use Railway PostgreSQL

1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically create a PostgreSQL database
3. Copy the connection details from the database service
4. Update your backend environment variables with Railway database credentials

### Option 3: Use External PostgreSQL

Any PostgreSQL database will work. Just configure the connection string in Railway environment variables.

## Post-Deployment Checklist

- [ ] Backend health check endpoint works: `/api/health`
- [ ] Backend API docs accessible: `/docs`
- [ ] Frontend loads without errors
- [ ] Frontend can connect to backend API
- [ ] CORS is properly configured
- [ ] Database connection is working
- [ ] All environment variables are set correctly

## Troubleshooting

### Backend Issues

**Problem**: Backend not starting
- Check Railway logs: `railway logs`
- Verify all environment variables are set
- Ensure `requirements.txt` includes all dependencies

**Problem**: Python 3.13 compatibility error (SQLAlchemy AssertionError)
- The project uses Python 3.12 (specified in `runtime.txt`)
- Railway should auto-detect Python version from `runtime.txt`
- If Railway uses Python 3.13, manually set Python version in Railway settings
- Error message: `AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'>`

**Problem**: Database connection failed
- Verify database credentials
- Check if database is accessible from Railway IPs
- Test connection locally with same credentials

**Problem**: CORS errors
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check that frontend is using correct backend URL
- Ensure no trailing slashes in URLs

### Frontend Issues

**Problem**: Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly in Vercel
- Check browser console for CORS errors
- Ensure backend URL doesn't have trailing slash

**Problem**: Build fails
- Check Vercel build logs
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

**Problem**: 404 errors on routes
- Verify `vercel.json` rewrite rules are correct
- Ensure SPA routing is configured properly

## Environment Variables Reference

### Backend (Railway)

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `your_password` |
| `DB_HOST` | Database host | `database-1.xxx.rds.amazonaws.com` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `postgres` |
| `DB_SCHEMA` | Database schema | `public` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `https://app.vercel.app` |
| `PORT` | Server port (auto-set by Railway) | `8000` |

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://backend.up.railway.app` |

## Continuous Deployment

Both Railway and Vercel support automatic deployments:

- **Railway**: Automatically deploys on push to main branch (if configured)
- **Vercel**: Automatically deploys on push to main branch

To enable:
1. Connect your GitHub repository
2. Configure branch settings in dashboard
3. Push changes to trigger automatic deployment

## Custom Domains

### Railway Custom Domain

1. Go to Railway project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` to include custom domain

### Vercel Custom Domain

1. Go to Vercel project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update backend `ALLOWED_ORIGINS` to include custom domain

## Monitoring

### Railway Logs

```bash
railway logs
```

Or view in Railway dashboard → Deployments → View Logs

### Vercel Logs

View in Vercel dashboard → Deployments → View Function Logs

## Cost Considerations

- **Railway**: Free tier includes $5/month credit
- **Vercel**: Free tier includes generous limits for personal projects
- **Database**: AWS RDS or Railway PostgreSQL pricing applies

## Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Use HTTPS**: Both platforms provide SSL certificates
3. **Limit CORS**: Only allow necessary origins
4. **Database security**: Use strong passwords, limit IP access
5. **API rate limiting**: Consider adding rate limiting for production

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Vite Docs: https://vitejs.dev

