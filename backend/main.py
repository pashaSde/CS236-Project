"""
FastAPI Backend for Hotel Reservations Data Viewer
"""

import logging
from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db, test_connection, get_available_tables, get_table_info, DB_SCHEMA
from models import (
    FilterParams, DatasetInfo,
    DataResponse, StatsResponse, HealthResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hotel Reservations API",
    description="REST API for querying hotel reservation datasets",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available datasets
DATASETS = {
    "customer_reservations": "Customer Reservations (Original)",
    "hotel_bookings": "Hotel Bookings (Original)",
    "merged_hotel_data": "Merged Hotel Data (Unified)"
}


def validate_dataset(dataset: str):
    """Validate dataset name"""
    if dataset not in DATASETS:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{dataset}' not found. Available: {list(DATASETS.keys())}"
        )


def build_filter_query(base_query: str, filters: FilterParams) -> tuple:
    """
    Build SQL query with filters
    Returns: (query_string, params_dict)
    """
    where_clauses = []
    params = {}
    
    # Price filters
    if filters.min_price is not None:
        where_clauses.append("avg_price_per_room >= :min_price")
        params["min_price"] = filters.min_price
    
    if filters.max_price is not None:
        where_clauses.append("avg_price_per_room <= :max_price")
        params["max_price"] = filters.max_price
    
    # Booking status filter
    if filters.booking_status:
        where_clauses.append("is_canceled = ANY(:booking_status)")
        params["booking_status"] = filters.booking_status
    
    # Date filters
    if filters.arrival_year is not None:
        where_clauses.append("arrival_year = :arrival_year")
        params["arrival_year"] = filters.arrival_year
    
    if filters.arrival_month is not None:
        where_clauses.append("arrival_month = :arrival_month")
        params["arrival_month"] = filters.arrival_month
    
    # Stay filters
    if filters.min_weekend_nights is not None:
        where_clauses.append("stays_in_weekend_nights >= :min_weekend_nights")
        params["min_weekend_nights"] = filters.min_weekend_nights
    
    if filters.max_weekend_nights is not None:
        where_clauses.append("stays_in_weekend_nights <= :max_weekend_nights")
        params["max_weekend_nights"] = filters.max_weekend_nights
    
    if filters.min_week_nights is not None:
        where_clauses.append("stays_in_week_nights >= :min_week_nights")
        params["min_week_nights"] = filters.min_week_nights
    
    if filters.max_week_nights is not None:
        where_clauses.append("stays_in_week_nights <= :max_week_nights")
        params["max_week_nights"] = filters.max_week_nights
    
    # Market segment filter
    if filters.market_segment:
        where_clauses.append("market_segment_type = ANY(:market_segment)")
        params["market_segment"] = filters.market_segment
    
    # Hotel filter
    if filters.hotel:
        where_clauses.append("hotel = ANY(:hotel)")
        params["hotel"] = filters.hotel
    
    # Country filter
    if filters.country:
        where_clauses.append("country = ANY(:country)")
        params["country"] = filters.country
    
    # Lead time filters
    if filters.min_lead_time is not None:
        where_clauses.append("lead_time >= :min_lead_time")
        params["min_lead_time"] = filters.min_lead_time
    
    if filters.max_lead_time is not None:
        where_clauses.append("lead_time <= :max_lead_time")
        params["max_lead_time"] = filters.max_lead_time
    
    # Build final query
    if where_clauses:
        query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
    else:
        query = base_query
    
    return query, params


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Hotel Reservations API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db_connected = test_connection()
        available_datasets = get_available_tables() if db_connected else []
        
        return HealthResponse(
            status="healthy" if db_connected else "unhealthy",
            database_connected=db_connected,
            available_datasets=available_datasets,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datasets", response_model=List[DatasetInfo], tags=["Datasets"])
async def list_datasets(db: Session = Depends(get_db)):
    """List available datasets with metadata"""
    try:
        result = []
        for table_name, display_name in DATASETS.items():
            # Get row count
            count_query = text(f"SELECT COUNT(*) FROM {DB_SCHEMA}.{table_name}")
            row_count = db.execute(count_query).scalar()
            
            # Get column info
            columns = get_table_info(table_name)
            
            result.append(DatasetInfo(
                name=table_name,
                display_name=display_name,
                row_count=row_count,
                column_count=len(columns),
                columns=columns
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/{dataset}", response_model=DataResponse, tags=["Data"])
async def get_data(
    dataset: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=10000, description="Records per page"),
    sort_by: Optional[str] = Query(None, description="Column to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    booking_status: Optional[List[str]] = Query(None, description="Booking status"),
    arrival_year: Optional[int] = Query(None, description="Arrival year"),
    arrival_month: Optional[int] = Query(None, ge=1, le=12, description="Arrival month"),
    market_segment: Optional[List[str]] = Query(None, description="Market segment"),
    hotel: Optional[List[str]] = Query(None, description="Hotel"),
    country: Optional[List[str]] = Query(None, description="Country"),
    db: Session = Depends(get_db)
):
    """
    Get paginated data from a dataset with optional filters and sorting
    """
    validate_dataset(dataset)
    
    try:
        # Build filters
        filters = FilterParams(
            min_price=min_price,
            max_price=max_price,
            booking_status=booking_status,
            arrival_year=arrival_year,
            arrival_month=arrival_month,
            market_segment=market_segment,
            hotel=hotel,
            country=country
        )
        
        # Base query
        base_query = f"SELECT * FROM {DB_SCHEMA}.{dataset}"
        
        # Build query with filters
        query, params = build_filter_query(base_query, filters)
        
        # Get total count with filters
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total_records = db.execute(text(count_query), params).scalar()
        
        # Add sorting
        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order.upper()}"
        else:
            query += " ORDER BY id"
        
        # Add pagination
        offset = (page - 1) * page_size
        query += f" LIMIT :limit OFFSET :offset"
        params["limit"] = page_size
        params["offset"] = offset
        
        # Execute query
        result = db.execute(text(query), params)
        
        # Convert to list of dicts
        columns = result.keys()
        data = [dict(zip(columns, row)) for row in result]
        
        # Calculate total pages
        total_pages = (total_records + page_size - 1) // page_size
        
        return DataResponse(
            dataset=dataset,
            total_records=total_records,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=data,
            filters_applied=filters.dict(exclude_none=True)
        )
        
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/{dataset}", response_model=StatsResponse, tags=["Statistics"])
async def get_statistics(
    dataset: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a dataset
    """
    validate_dataset(dataset)
    
    try:
        # Get basic stats
        stats_query = text(f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT hotel) as unique_hotels,
                COUNT(DISTINCT country) as unique_countries,
                COUNT(DISTINCT market_segment_type) as unique_segments,
                AVG(avg_price_per_room) as avg_price,
                MIN(avg_price_per_room) as min_price,
                MAX(avg_price_per_room) as max_price,
                AVG(lead_time) as avg_lead_time,
                AVG(stays_in_weekend_nights) as avg_weekend_nights,
                AVG(stays_in_week_nights) as avg_week_nights,
                COUNT(CASE WHEN is_canceled IN ('true', 'Canceled') THEN 1 END) as canceled_count,
                COUNT(CASE WHEN is_canceled IN ('false', 'Not_Canceled') THEN 1 END) as not_canceled_count
            FROM {DB_SCHEMA}.{dataset}
        """)
        
        result = db.execute(stats_query).fetchone()
        
        statistics = {
            "total_records": result[0],
            "unique_hotels": result[1],
            "unique_countries": result[2],
            "unique_market_segments": result[3],
            "price_statistics": {
                "average": float(result[4]) if result[4] else None,
                "minimum": float(result[5]) if result[5] else None,
                "maximum": float(result[6]) if result[6] else None
            },
            "booking_statistics": {
                "avg_lead_time": float(result[7]) if result[7] else None,
                "avg_weekend_nights": float(result[8]) if result[8] else None,
                "avg_week_nights": float(result[9]) if result[9] else None
            },
            "cancellation_statistics": {
                "canceled": result[10],
                "not_canceled": result[11],
                "cancellation_rate": (result[10] / result[0] * 100) if result[0] > 0 else 0
            }
        }
        
        return StatsResponse(
            dataset=dataset,
            total_records=result[0],
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting Hotel Reservations API...")
    print("Docs available at: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

