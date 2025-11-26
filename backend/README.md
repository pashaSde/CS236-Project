# Hotel Reservations API - Backend

FastAPI backend for querying hotel reservation datasets from PostgreSQL.

## Features

- REST API for 3 datasets (customer_reservations, hotel_bookings, merged_hotel_data)
- Advanced filtering (price, dates, booking status, market segment, etc.)
- Pagination and sorting
- Statistics endpoints
- Auto-generated API documentation (Swagger UI)
- CORS enabled for frontend

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env if your database credentials are different
```

### 3. Test Database Connection

```bash
python database.py
```

Expected output:
```
✓ Database connection successful

Available tables:
  - customer_reservations
    • id (character varying)
    • hotel (character varying)
    ...
  - hotel_bookings
  - merged_hotel_data
```

## Running the API

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload --port 8000
```

Or simply:

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

```bash
GET /api/health
```

### List Datasets

```bash
GET /api/datasets
```

Response:
```json
[
  {
    "name": "customer_reservations",
    "display_name": "Customer Reservations (Original)",
    "row_count": 36276,
    "column_count": 14,
    "columns": [...]
  }
]
```

### Get Data (with filters)

```bash
GET /api/data/{dataset}?page=1&page_size=100&min_price=50&max_price=200
```

Query parameters:
- `page` (default: 1)
- `page_size` (default: 100, max: 10000)
- `sort_by` (column name)
- `sort_order` (asc/desc)
- `min_price`, `max_price`
- `booking_status` (array: ["Canceled", "Not_Canceled"])
- `arrival_year`, `arrival_month`
- `market_segment` (array)
- `hotel` (array)
- `country` (array)

### Get Statistics

```bash
GET /api/stats/{dataset}
```

Response:
```json
{
  "dataset": "merged_hotel_data",
  "total_records": 114978,
  "statistics": {
    "total_records": 114978,
    "unique_hotels": 2,
    "price_statistics": {
      "average": 105.34,
      "minimum": 0.0,
      "maximum": 508.0
    },
    "cancellation_statistics": {
      "canceled": 44224,
      "not_canceled": 70754,
      "cancellation_rate": 38.46
    }
  }
}
```

## Example Requests

### Get first 50 records

```bash
curl "http://localhost:8000/api/data/merged_hotel_data?page=1&page_size=50"
```

### Filter by price range and booking status

```bash
curl "http://localhost:8000/api/data/customer_reservations?min_price=100&max_price=200&booking_status=Not_Canceled"
```

### Get 2018 bookings sorted by price

```bash
curl "http://localhost:8000/api/data/hotel_bookings?arrival_year=2018&sort_by=avg_price_per_room&sort_order=desc"
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# List datasets
curl http://localhost:8000/api/datasets

# Get statistics
curl http://localhost:8000/api/stats/merged_hotel_data
```

## Technology Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **PostgreSQL**: Database (via psycopg2)

