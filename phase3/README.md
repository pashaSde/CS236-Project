# Project Phase 3 - Interactive Web Application

**Authors:** Pankaj Sharma & Saransh Gupta  
**Course:** CS236 - Database Management System

## Folder Structure

```
CS236-Project/
│
├── backend/                      # FastAPI REST API backend
│   ├── database.py              # Database connection and session management
│   ├── main.py                  # FastAPI application and API endpoints
│   ├── models.py                # Pydantic models for request/response validation
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend setup and API documentation
│
├── frontend/                     # React TypeScript frontend
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts        # API client for backend communication
│   │   ├── components/
│   │   │   ├── DataGrid.tsx    # AG Grid data table component
│   │   │   ├── DataGrid.css    # Data grid styling
│   │   │   ├── FilterPanel.tsx # Filter controls component
│   │   │   ├── FilterPanel.css # Filter panel styling
│   │   │   ├── StatsPanel.tsx  # Statistics display component
│   │   │   └── StatsPanel.css  # Statistics panel styling
│   │   ├── types/
│   │   │   └── api.ts          # TypeScript type definitions
│   │   ├── App.tsx             # Main application component
│   │   ├── App.css             # Application styles
│   │   ├── main.tsx            # Application entry point
│   │   └── index.css            # Global styles
│   ├── package.json             # Node.js dependencies and scripts
│   ├── vite.config.ts           # Vite build configuration
│   ├── tsconfig.json            # TypeScript configuration
│   └── README.md                # Frontend setup instructions
│
└── phase3/                       # Phase 3 deliverables
    ├── phase3_report.md          # Phase 3 project report (Markdown)
    ├── phase3_report.pdf         # Phase 3 project report (PDF)
    ├── screenshots/              # Application screenshots for documentation
    │   ├── dropdown.png         # Dataset selection screenshot
    │   ├── price_range.png      # Price filter screenshot
    │   ├── bookingStatus.png     # Booking status filter screenshot
    │   ├── dateFilter.png        # Date range filter screenshot
    │   ├── marketSegmentFilter.png # Market segment filter screenshot
    │   ├── combinedFilters.png   # Combined filters screenshot
    │   ├── dataGrid.png          # Data grid with pagination screenshot
    │   └── stats.png             # Statistics panel screenshot
    └── README.md                 # This file
```

## Contents Overview

### Backend Directory (`backend/`)
FastAPI REST API that provides endpoints for querying hotel reservation data from PostgreSQL:

- **database.py**: SQLAlchemy database engine setup, connection pooling, and session management
- **main.py**: FastAPI application with endpoints for datasets, data retrieval with filtering, and statistics
- **models.py**: Pydantic models for request validation and response serialization
- **requirements.txt**: Python package dependencies (FastAPI, SQLAlchemy, psycopg2, etc.)

**Key Features:**
- RESTful API endpoints for 3 datasets
- Advanced filtering (price, dates, booking status, market segment)
- Pagination and sorting support
- Real-time statistics calculation
- Parameterized queries for SQL injection prevention
- CORS enabled for frontend integration

### Frontend Directory (`frontend/`)
React TypeScript application providing interactive UI for data exploration:

- **src/api/client.ts**: Axios-based API client with request/response interceptors
- **src/components/DataGrid.tsx**: AG Grid component for displaying paginated data with sorting
- **src/components/FilterPanel.tsx**: Collapsible filter panel with multiple filter types
- **src/components/StatsPanel.tsx**: Real-time statistics dashboard component
- **src/types/api.ts**: TypeScript interfaces for type safety
- **src/App.tsx**: Main application orchestrating components and state management

**Key Features:**
- Interactive data grid with AG Grid
- Dataset selector dropdown
- Advanced filtering panel (price, dates, booking status, market segment)
- Real-time statistics display
- Pagination controls (50-1000 records per page)
- Responsive design with modern UI
- TypeScript for type safety

### Phase 3 Deliverables (`phase3/`)
Documentation and screenshots for Phase 3:

- **phase3_report.md**: Comprehensive project report in Markdown format
- **phase3_report.pdf**: Formatted PDF version of the report
- **screenshots/**: Visual documentation of application features
  - Feature demonstrations (filters, data grid, statistics)
  - UI component screenshots
  - User interaction examples

## Quick Start

### 1. Start Backend API

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`
- API docs: http://localhost:8000/docs

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000` (or port shown in terminal)

### 3. View Documentation

- **Report**: `phase3/phase3_report.pdf`
- **Backend API**: `backend/README.md`
- **Frontend Guide**: `frontend/README.md`

## Architecture

```
┌─────────────┐         HTTP/REST          ┌─────────────┐
│   React     │ ──────────────────────────> │   FastAPI   │
│  Frontend   │ <────────────────────────── │   Backend   │
│ (Port 3000) │         JSON Response       │ (Port 8000)│
└─────────────┘                             └──────┬──────┘
                                                   │ SQL
                                                   ▼
                                            ┌─────────────┐
                                            │ PostgreSQL  │
                                            │  (AWS RDS)  │
                                            └─────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **PostgreSQL**: Database (AWS RDS)

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **AG Grid**: High-performance data grid
- **Axios**: HTTP client
- **React DatePicker**: Date selection component

## Key Features

### Dataset Selection
- Switch between 3 datasets (customer_reservations, hotel_bookings, merged_hotel_data)
- Automatic statistics loading
- Row count display

### Advanced Filtering
- **Price Range**: Min/max price filtering
- **Booking Status**: Canceled/Not Canceled filter
- **Date Range**: Month/year picker for arrival dates
- **Market Segment**: Multi-select checkbox filter
- **Combined Filters**: All filters work together with AND logic

### Data Grid
- Pagination (50-1000 records per page)
- Sortable columns
- Resizable columns
- Number formatting
- Filtered record count display

### Statistics Panel
- Total records
- Average price (min/max range)
- Cancellation rate
- Average lead time
- Average stay duration
- Unique hotels, countries, market segments

## Database Integration

The application connects to PostgreSQL database hosted on AWS RDS:
- Connection pooling for performance
- Parameterized queries for security
- Schema-aware queries (public schema)
- Support for switching between RDS and local Docker instances

## Security Features

- **SQL Injection Prevention**: All queries use parameterized statements
- **Input Validation**: Pydantic models validate all inputs
- **Type Safety**: TypeScript ensures type correctness on frontend
- **CORS Configuration**: Restricted to allowed origins

## Project Report

See `phase3_report.pdf` for:
- System architecture overview
- Feature demonstrations with screenshots
- Code implementation details
- Database integration flow
- Security considerations
- Conclusion and results


