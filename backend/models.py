from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class FilterParams(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    booking_status: Optional[List[str]] = None
    arrival_year: Optional[int] = None
    arrival_month: Optional[int] = Field(None, ge=1, le=12)
    arrival_date_from: Optional[str] = None
    arrival_date_to: Optional[str] = None
    min_weekend_nights: Optional[int] = Field(None, ge=0)
    max_weekend_nights: Optional[int] = Field(None, ge=0)
    min_week_nights: Optional[int] = Field(None, ge=0)
    max_week_nights: Optional[int] = Field(None, ge=0)
    market_segment: Optional[List[str]] = None
    hotel: Optional[List[str]] = None
    country: Optional[List[str]] = None
    min_lead_time: Optional[int] = Field(None, ge=0)
    max_lead_time: Optional[int] = Field(None, ge=0)


class DatasetInfo(BaseModel):
    name: str
    display_name: str
    row_count: int
    column_count: int
    columns: List[Dict[str, Any]]


class DataResponse(BaseModel):
    dataset: str
    total_records: int
    page: int
    page_size: int
    total_pages: int
    data: List[Dict[str, Any]]
    filters_applied: Dict[str, Any]


class StatsResponse(BaseModel):
    dataset: str
    total_records: int
    statistics: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    available_datasets: List[str]
    timestamp: datetime

