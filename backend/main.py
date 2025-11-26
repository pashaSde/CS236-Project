import logging
from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db, test_connection, get_available_tables, get_table_info, DB_SCHEMA
from models import FilterParams, DatasetInfo, DataResponse, StatsResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hotel Reservations API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASETS = {
    "customer_reservations": "Customer Reservations (Original)",
    "hotel_bookings": "Hotel Bookings (Original)",
    "merged_hotel_data": "Merged Hotel Data (Unified)"
}


def validate_dataset(dataset: str):
    """Validates that the requested dataset exists in available datasets."""
    if dataset not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' not found")


def build_filter_query(base_query: str, filters: FilterParams) -> tuple:
    """
    Builds a SQL WHERE clause from filter parameters.
    
    Handles complex filtering including price ranges, booking status (with boolean conversion),
    date ranges (year/month or date range), stay duration, and categorical filters.
    
    Returns:
        tuple: (query_string, params_dict) for parameterized query execution
    """
    where_clauses = []
    params = {}
    
    if filters.min_price is not None:
        where_clauses.append("avg_price_per_room >= :min_price")
        params["min_price"] = filters.min_price
    
    if filters.max_price is not None:
        where_clauses.append("avg_price_per_room <= :max_price")
        params["max_price"] = filters.max_price
    
    if filters.booking_status:
        # Convert string status values to boolean for database query
        bool_values = []
        for status in filters.booking_status:
            if status in ('Canceled', 'true', 'True', '1'):
                bool_values.append(True)
            elif status in ('Not_Canceled', 'false', 'False', '0'):
                bool_values.append(False)
        
        if bool_values:
            unique_bool_values = list(dict.fromkeys(bool_values))
            if len(unique_bool_values) == 1:
                bool_literal = 'TRUE' if unique_bool_values[0] else 'FALSE'
                where_clauses.append(f"is_canceled = {bool_literal}")
            else:
                or_conditions = [f"is_canceled = {'TRUE' if v else 'FALSE'}" for v in unique_bool_values]
                where_clauses.append(f"({' OR '.join(or_conditions)})")
    
    if filters.arrival_date_from or filters.arrival_date_to:
        # Handle date range filtering (format: YYYY-MM)
        date_conditions = []
        if filters.arrival_date_from:
            from_year, from_month = map(int, filters.arrival_date_from.split('-'))
            date_conditions.append(f"((arrival_year > :from_year) OR (arrival_year = :from_year AND arrival_month >= :from_month))")
            params["from_year"] = from_year
            params["from_month"] = from_month
        if filters.arrival_date_to:
            to_year, to_month = map(int, filters.arrival_date_to.split('-'))
            date_conditions.append(f"((arrival_year < :to_year) OR (arrival_year = :to_year AND arrival_month <= :to_month))")
            params["to_year"] = to_year
            params["to_month"] = to_month
        if date_conditions:
            where_clauses.append(f"({' AND '.join(date_conditions)})")
    else:
        if filters.arrival_year is not None:
            where_clauses.append("arrival_year = :arrival_year")
            params["arrival_year"] = filters.arrival_year
        if filters.arrival_month is not None:
            where_clauses.append("arrival_month = :arrival_month")
            params["arrival_month"] = filters.arrival_month
    
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
    
    if filters.market_segment:
        where_clauses.append("market_segment_type = ANY(:market_segment)")
        params["market_segment"] = filters.market_segment
    if filters.hotel:
        where_clauses.append("hotel = ANY(:hotel)")
        params["hotel"] = filters.hotel
    if filters.country:
        where_clauses.append("country = ANY(:country)")
        params["country"] = filters.country
    if filters.min_lead_time is not None:
        where_clauses.append("lead_time >= :min_lead_time")
        params["min_lead_time"] = filters.min_lead_time
    if filters.max_lead_time is not None:
        where_clauses.append("lead_time <= :max_lead_time")
        params["max_lead_time"] = filters.max_lead_time
    
    if where_clauses:
        query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
    else:
        query = base_query
    
    return query, params


@app.get("/")
async def root():
    return {
        "message": "Hotel Reservations API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    db_connected = test_connection()
    available_datasets = get_available_tables() if db_connected else []
    
    return HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        database_connected=db_connected,
        available_datasets=available_datasets,
        timestamp=datetime.now()
    )


@app.get("/api/datasets", response_model=List[DatasetInfo])
async def list_datasets(db: Session = Depends(get_db)):
    result = []
    for table_name, display_name in DATASETS.items():
        count_query = text(f"SELECT COUNT(*) FROM {DB_SCHEMA}.{table_name}")
        row_count = db.execute(count_query).scalar()
        columns = get_table_info(table_name)
        
        result.append(DatasetInfo(
            name=table_name,
            display_name=display_name,
            row_count=row_count,
            column_count=len(columns),
            columns=columns
        ))
    
    return result


@app.get("/api/data/{dataset}", response_model=DataResponse)
async def get_data(
    dataset: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=10000),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    booking_status: Optional[List[str]] = Query(None),
    arrival_year: Optional[int] = Query(None),
    arrival_month: Optional[int] = Query(None, ge=1, le=12),
    arrival_date_from: Optional[str] = Query(None),
    arrival_date_to: Optional[str] = Query(None),
    market_segment: Optional[List[str]] = Query(None),
    hotel: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    validate_dataset(dataset)
    
    filters = FilterParams(
        min_price=min_price,
        max_price=max_price,
        booking_status=booking_status,
        arrival_year=arrival_year,
        arrival_month=arrival_month,
        arrival_date_from=arrival_date_from,
        arrival_date_to=arrival_date_to,
        market_segment=market_segment,
        hotel=hotel,
        country=country
    )
    
    base_query = f"SELECT * FROM {DB_SCHEMA}.{dataset}"
    query, params = build_filter_query(base_query, filters)
    
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total_records = db.execute(text(count_query), params).scalar()
    
    if sort_by:
        query += f" ORDER BY {sort_by} {sort_order.upper()}"
    else:
        query += " ORDER BY id"
    
    offset = (page - 1) * page_size
    query += f" LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = db.execute(text(query), params)
    columns = result.keys()
    data = [dict(zip(columns, row)) for row in result]
    
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


@app.get("/api/stats/{dataset}", response_model=StatsResponse)
async def get_statistics(dataset: str, db: Session = Depends(get_db)):
    """Returns aggregated statistics for the specified dataset."""
    validate_dataset(dataset)
    
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
            COUNT(CASE WHEN is_canceled IS TRUE OR lower(is_canceled::text) IN ('true', 'Canceled') THEN 1 END) as canceled_count,
            COUNT(CASE WHEN is_canceled IS FALSE OR lower(is_canceled::text) IN ('false', 'Not_Canceled') THEN 1 END) as not_canceled_count
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

