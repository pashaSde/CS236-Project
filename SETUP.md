# Hotel Reservations System - Complete Setup Guide

This guide will help you set up and run the complete Hotel Reservations Data Viewer system.

## 📋 Prerequisites

- Python 3.9+ (with PySpark)
- Node.js 18+ and npm
- PostgreSQL (via Docker)
- Git

## 🏗️ Project Structure

```
CS236-Project/
├── backend/              # FastAPI REST API
├── frontend/             # React + AG Grid UI
├── phase2/               # PySpark data loader
├── output/               # CSV datasets
└── SETUP.md             # This file
```

## 🚀 Step-by-Step Setup

### 1. Database Setup

#### Start PostgreSQL with Docker

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secret123 \
  -e POSTGRES_DB=reservations \
  -p 5432:5432 \
  postgres:latest
```

#### Verify Database is Running

```bash
docker ps | grep postgres
```

### 2. Load Data into PostgreSQL

#### Navigate to phase2 directory

```bash
cd phase2
```

#### Run PySpark Data Loader

```bash
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
```

**Expected Output:**
```
✓ Schema 'innsight' is ready
✓ Successfully loaded 36276 rows into innsight.customer_reservations
✓ Successfully loaded 78700 rows into innsight.hotel_bookings
✓ Successfully loaded 114978 rows into innsight.merged_hotel_data
```

**Note:** The script will pause with Spark Web UI available at http://localhost:4040. Press Ctrl+C when done exploring.

### 3. Backend Setup (FastAPI)

#### Navigate to backend directory

```bash
cd ../backend
```

#### Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Test database connection

```bash
python database.py
```

**Expected Output:**
```
✓ Database connection successful

Available tables:
  - customer_reservations
  - hotel_bookings
  - merged_hotel_data
```

#### Start FastAPI server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

**API will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

### 4. Frontend Setup (React)

#### Open a new terminal and navigate to frontend

```bash
cd ../frontend
```

#### Install Node.js dependencies

```bash
npm install
```

#### Start React development server

```bash
npm run dev
```

**Frontend will be available at:**
- http://localhost:3000

## 🎯 Usage

### Accessing the Application

1. **Open browser:** Navigate to http://localhost:3000
2. **Select dataset:** Choose from 3 available datasets
3. **View statistics:** See real-time stats at the top
4. **Apply filters:** Expand filter panel and set criteria
5. **Browse data:** Use AG Grid to sort, filter, and paginate

### Available Datasets

1. **Customer Reservations** - 36,276 rows
2. **Hotel Bookings** - 78,700 rows  
3. **Merged Hotel Data** - 114,978 rows (unified)

### Filter Options

- **Price Range:** Min/Max price per room
- **Booking Status:** Canceled or Not Canceled
- **Arrival Date:** Year and month
- **Market Segment:** Customer segment type
- **Hotel:** Hotel name/type
- **Country:** Country code

## 🧪 Testing

### Test Backend API

```bash
# Health check
curl http://localhost:8000/api/health

# List datasets
curl http://localhost:8000/api/datasets

# Get data with filters
curl "http://localhost:8000/api/data/merged_hotel_data?page=1&page_size=10&min_price=100"

# Get statistics
curl http://localhost:8000/api/stats/customer_reservations
```

### Test Frontend
- Open http://localhost:3000
- Try switching datasets
- Apply various filters
- Test pagination

## 🛠️ Troubleshooting

### Database Connection Failed

**Issue:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check if Docker container is running
docker ps

# Restart container if needed
docker restart postgres

# Check logs
docker logs postgres
```

### PySpark Data Loader Failed

**Issue:** "File not found" errors

**Solution:**
- Ensure you're running from the correct directory
- Verify CSV files exist in `../output/` directory

**Issue:** "Database does not exist"

**Solution:**
- Verify database name is `reservations` not `InnSight`
- Recreate Docker container with correct DB name

### Backend Won't Start

**Issue:** Port 8000 already in use

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in main.py
uvicorn main:app --reload --port 8001
```

**Issue:** Module not found

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Issue:** Cannot connect to backend

**Solution:**
- Ensure backend is running on port 8000
- Check CORS settings in backend/main.py
- Verify API_BASE_URL in frontend/src/api/client.js

**Issue:** AG Grid not displaying

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📦 Production Deployment

### Backend

```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or any static server
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:
```
DB_USER=admin
DB_PASSWORD=secret123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reservations
DB_SCHEMA=innsight
```

### Frontend Environment Variables

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│  Browser (localhost:3000)                   │
│  React + AG Grid + Axios                    │
└──────────────┬──────────────────────────────┘
               │ HTTP REST API
               ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend (localhost:8000)           │
│  Python + SQLAlchemy + Pydantic             │
└──────────────┬──────────────────────────────┘
               │ SQL Queries
               ▼
┌─────────────────────────────────────────────┐
│  PostgreSQL (localhost:5432)                │
│  Database: reservations                     │
│  Schema: innsight                           │
│  - customer_reservations (36K rows)         │
│  - hotel_bookings (79K rows)                │
│  - merged_hotel_data (115K rows)            │
└─────────────────────────────────────────────┘
```

## 🎓 For CS236 Project

This system demonstrates:
- ✅ Big Data Processing (PySpark)
- ✅ Database Design (PostgreSQL with schema)
- ✅ REST API Development (FastAPI)
- ✅ Frontend Development (React + AG Grid)
- ✅ Data Filtering and Pagination
- ✅ Real-time Statistics
- ✅ Interactive Data Visualization

## 📝 Key Features

1. **Three Dataset Support:** Original datasets + unified dataset
2. **Advanced Filtering:** Multiple filter criteria with AND logic
3. **Performance:** Server-side pagination, handles 100K+ rows
4. **Statistics:** Real-time aggregated statistics
5. **Modern UI:** Responsive design with gradients and animations
6. **Developer Friendly:** API documentation at /docs

## 🆘 Need Help?

- Backend API Docs: http://localhost:8000/docs
- Backend README: `backend/README.md`
- Frontend README: `frontend/README.md`
- Data Loader: `phase2/databaseLoader.py`

## ✅ Verification Checklist

- [ ] PostgreSQL Docker container running
- [ ] Data loaded into database (3 tables)
- [ ] Backend API running on port 8000
- [ ] Backend /api/health returns healthy status
- [ ] Frontend running on port 3000
- [ ] Can view all 3 datasets
- [ ] Filters work correctly
- [ ] Statistics display properly
- [ ] Pagination works
- [ ] AG Grid displays data

---

**Built with:** React • AG Grid • FastAPI • PostgreSQL • PySpark

**Author:** CS236 Project Team

**Date:** November 2025

