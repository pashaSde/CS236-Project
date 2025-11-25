"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class FilterParams(BaseModel):
    """
    Filter parameters for querying data
    """
    # Price filters
    min_price: Optional[float] = Field(None, description="Minimum price per room")
    max_price: Optional[float] = Field(None, description="Maximum price per room")
    
    # Booking status filter
    booking_status: Optional[List[str]] = Field(None, description="Booking status (Canceled/Not_Canceled or true/false)")
    
    # Date filters
    arrival_year: Optional[int] = Field(None, description="Arrival year")
    arrival_month: Optional[int] = Field(None, ge=1, le=12, description="Arrival month (1-12)")
    arrival_date_from: Optional[str] = Field(None, description="Arrival date from (YYYY-MM format)")
    arrival_date_to: Optional[str] = Field(None, description="Arrival date to (YYYY-MM format)")
    
    # Stay filters
    min_weekend_nights: Optional[int] = Field(None, ge=0, description="Minimum weekend nights")
    max_weekend_nights: Optional[int] = Field(None, ge=0, description="Maximum weekend nights")
    min_week_nights: Optional[int] = Field(None, ge=0, description="Minimum week nights")
    max_week_nights: Optional[int] = Field(None, ge=0, description="Maximum week nights")
    
    # Market segment filter
    market_segment: Optional[List[str]] = Field(None, description="Market segment type")
    
    # Hotel filter
    hotel: Optional[List[str]] = Field(None, description="Hotel name/type")
    
    # Country filter
    country: Optional[List[str]] = Field(None, description="Country code")
    
    # Lead time filters
    min_lead_time: Optional[int] = Field(None, ge=0, description="Minimum lead time in days")
    max_lead_time: Optional[int] = Field(None, ge=0, description="Maximum lead time in days")


class PaginationParams(BaseModel):
    """
    Pagination parameters
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(100, ge=1, le=10000, description="Number of records per page")


class SortParams(BaseModel):
    """
    Sorting parameters
    """
    sort_by: Optional[str] = Field(None, description="Column to sort by")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order (asc/desc)")


class DatasetInfo(BaseModel):
    """
    Dataset information response
    """
    name: str
    display_name: str
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]


class DataResponse(BaseModel):
    """
    Data response with pagination
    """
    dataset: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]


class StatsResponse(BaseModel):
    """
    Statistics response for a dataset
    """
    dataset: str
    total_records: int
    statistics: Dict[str, Any]


class HealthResponse(BaseModel):
    """
    Health check response
    """
    status: str
    database_connected: bool
    available_datasets: List[str]
    timestamp: datetime


class ErrorResponse(BaseModel):
    """
    Error response
    """
    error: str
    detail: Optional[str] = None

