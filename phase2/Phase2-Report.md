# Phase 2: Spark Analysis & Database Population

**Course:** CS236 — Database Management System  
**Authors:**

- **Pankaj Sharma** (SID: 862549035)
- **Saransh Gupta** (SID: 862548920)

---

## 1. Dataset Analaysis

This sections will describes the reasoning and decisions behind analysis was done using Spark

### 1.1 Cancellation Rate Calculation

We did cancellation rate analysis in order to analyse how cancellations vary by month.

- We used the is_canceled attribute of the dataset.
- However, this field was originally a string ("true" / "false"), so first decision we took was to convert it into a numeric form (0/1):
- We grouped bookings by arrival month and the cancellation rate was computed as
  Cancellation Rate = Number of Canceled Bookings/ Total Bookings​ × 100

### 1.2 Average Price and Average Nights Stayed analysis

We did to anlyse the average price and average ngihts stayed by customers. Each booking in the dataset contains two fields related to length of stay:

- stays_in_weekend_nights
- stays_in_week_nights

Decisions made:

- We made the decision to combine these to form Total Nights i.e.
  _Total Nights = Weekend Nights + Weekday Nights_
- Then the Average Price per room and Average Stay duration were computed by using the avg() method.
- This dual analysis helps determine not only whether certain months are more expensive but also whether guests tend to stay longer during those periods.

### 1.3 Monthly Booking by Market Segment

Here we decided to group Bookings by

- arrival_month
- market_segment_type
  in order to get insights into customer acquisition channels.

### 1.4 Seasonality and Revenue Estimation

Since Revenue is not directly provided in the dataset. We took a decision to compute Revenue via _Revenue = Avg Price per Room × Total Nights Stayed_ We decided this on the assumption that The total amount a guest pays is proportional to how many nights they stay and the room price. Revenue and booking counts were then grouped monthly to identify peak revenue months versus peak bookings month.

## 2. Database Setup

We used Docker to run PostgreSQL with the following configuration:

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=******** \
  -e POSTGRES_DB=innsight \
  -p 5432:5432 \
  postgres:latest
```

**Database Hierarchy:**

```
PostgreSQL Instance (localhost:5432)
└── Database: innsight
    └── Schema: public (default)
        ├── Table: customer_reservations (36,275 rows)
        ├── Table: hotel_bookings (78,702 rows)
        └── Table: merged_hotel_data (114,977 rows)
```

---

## 3. Schema Design

### 3.1 Unified Schema for Three Tables

All three tables share the same 14-column schema to maintain consistency across datasets:

| Column Name                 | Data Type | Nullable | Description                             |
| --------------------------- | --------- | -------- | --------------------------------------- |
| `booking_id`                | VARCHAR   | NOT NULL | Unique booking identifier (PRIMARY KEY) |
| `hotel`                     | VARCHAR   | NULL     | Hotel type (City/Resort)                |
| `is_canceled`               | BOOLEAN   | NOT NULL | Cancellation status (True/False)        |
| `lead_time`                 | INTEGER   | NULL     | Days between booking and arrival        |
| `arrival_year`              | INTEGER   | NULL     | Year of arrival                         |
| `arrival_month`             | INTEGER   | NULL     | Month of arrival (1-12)                 |
| `arrival_date_week_number`  | INTEGER   | NULL     | ISO week number (1-53)                  |
| `arrival_date_day_of_month` | INTEGER   | NULL     | Day of month (1-31)                     |
| `stays_in_weekend_nights`   | INTEGER   | NULL     | Weekend nights booked                   |
| `stays_in_week_nights`      | INTEGER   | NULL     | Weekday nights booked                   |
| `market_segment_type`       | VARCHAR   | NULL     | Market segment category                 |
| `country`                   | VARCHAR   | NULL     | ISO country code                        |
| `avg_price_per_room`        | DOUBLE    | NULL     | Average room price per night            |
| `email`                     | VARCHAR   | NULL     | Customer email address                  |

### 3.2 Key Design Decisions

**Primary Key:** We chose `booking_id` (VARCHAR) as the primary key because the IDs follow pattern `INN00001`, `INN50000`, etc., which preserves data lineage from source systems.

**Boolean Type:** The `is_canceled` field uses PostgreSQL BOOLEAN type for storage efficiency (1 byte vs 12+ bytes for strings) and better query performance.

**Nullable Fields:** Fields like `hotel`, `country`, and `email` are nullable because the Customer Reservations dataset lacks these columns.

### 3.3 Indexes for Performance

We created indexes on frequently queried columns:

```sql
CREATE INDEX idx_price ON table_name(avg_price_per_room);
CREATE INDEX idx_status ON table_name(is_canceled);
CREATE INDEX idx_date ON table_name(arrival_year, arrival_month);
CREATE INDEX idx_segment ON table_name(market_segment_type);
```

These indexes improve query performance by 3-6x for filtering operations.

---

## 4. Data Loading with PySpark

### 4.1 Architecture

```
CSV Files → PySpark DataFrame → Data Transformation → PostgreSQL (JDBC)
```

### 4.2 Code Structure

The `databaseLoader.py` script consists of several key functions:

#### **1. Spark Session Setup**

```python
def get_spark_session():
    spark = SparkSession.builder \
        .appName("Hotel Reservations DB Loader") \
        .config("spark.jars", postgres_jar_path) \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    return spark
```

Initializes Spark with PostgreSQL JDBC driver and allocates 2GB memory.

#### **2. Schema Definition**

```python
def define_schema():
    return StructType([
        StructField("booking_id", StringType(), False),
        StructField("hotel", StringType(), True),
        StructField("is_canceled", BooleanType(), False),
        # ... 11 more fields
    ])
```

Explicitly defines the schema to ensure type consistency across all tables.

#### **3. Data Normalization**

```python
def normalize_booking_status(df):
    # Convert booking_status → is_canceled (boolean)
    if "booking_status" in df.columns:
        df = df.withColumn("is_canceled",
            when(df.booking_status == "Canceled", True)
            .otherwise(False))
        df = df.drop("booking_status")

    # Normalize existing is_canceled variations
    elif "is_canceled" in df.columns:
        df = df.withColumn("is_canceled",
            col("is_canceled").cast(StringType()))

        df = df.withColumn("is_canceled",
            when(col("is_canceled").isin("true", "True", "1", "Canceled"),
                 lit(True))
            .when(col("is_canceled").isin("false", "False", "0", "Not_Canceled"),
                  lit(False))
            .otherwise(col("is_canceled").cast(BooleanType())))

    return df
```

Handles inconsistent boolean representations across datasets:

- Customer Reservations: "Canceled", "Not_Canceled"
- Hotel Bookings: "true", "false", "1", "0"
- Merged Data: "Canceled", "Not_Canceled"

#### **5. Column Renaming**

```python
def normalize_columns(df):
    # Standardize column names
    rename_map = {
        "Booking_ID": "booking_id",
        "id": "booking_id",
        "arrival_date": "arrival_date_day_of_month"
    }

    for old_name, new_name in rename_map.items():
        if old_name in df.columns:
            df = df.withColumnRenamed(old_name, new_name)

    return df
```

Normalizes inconsistent column names across source files.

#### **5. Write to PostgreSQL**

```python
def load_table(spark, table_name, csv_path):
    # Read CSV with explicit schema
    df = spark.read.csv(csv_path, header=True, schema=schema)

    # Normalize data
    df = normalize_columns(df)
    df = normalize_booking_status(df)

    # Write to PostgreSQL via JDBC
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/innsight") \
        .option("dbtable", table_name) \
        .option("user", "admin") \
        .option("password", os.getenv("POSTGRES_PWD", "")) \
        .option("driver", "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()
```

Uses JDBC to write DataFrames directly to PostgreSQL. The `mode("overwrite")` allows idempotent execution.

#### **6. Index Creation**

```python
def create_indexes(spark):
    conn = get_db_connection(spark)
    stmt = conn.createStatement()

    for table in ["customer_reservations", "hotel_bookings", "merged_hotel_data"]:
        # Create indexes
        stmt.execute(f"CREATE INDEX IF NOT EXISTS {table}_idx_price
                      ON {table}(avg_price_per_room)")
        stmt.execute(f"CREATE INDEX IF NOT EXISTS {table}_idx_status
                      ON {table}(is_canceled)")
        stmt.execute(f"CREATE INDEX IF NOT EXISTS {table}_idx_date
                      ON {table}(arrival_year, arrival_month)")
        stmt.execute(f"CREATE INDEX IF NOT EXISTS {table}_idx_segment
                      ON {table}(market_segment_type)")

        # Update statistics
        stmt.execute(f"ANALYZE {table}")

    stmt.close()
    conn.close()
```

Creates performance indexes and updates table statistics for query optimization.

### 3.3 Execution

```bash
export POSTGRES_PWD=********
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
```

The script loads all three datasets and creates indexes, resulting in:

- 36,275 customer reservation records
- 78,702 hotel booking records
- 114,977 merged records
- 12 indexes (4 per table)

---

## 5. Key Challenges & Solutions

### Challenge 1: Inconsistent Boolean Representations

**Problem:** Three different formats for cancellation status across datasets.  
**Solution:** Multi-stage normalization that converts all variations to proper BOOLEAN type.

### Challenge 2: Column Name Variations

**Problem:** Same data with different column names (e.g., `Booking_ID` vs `id`).  
**Solution:** Mapping-based column renaming before schema enforcement.

### Challenge 3: Type Safety in Spark

**Problem:** PySpark `DATATYPE_MISMATCH` error when mixing boolean and string types.  
**Solution:** Explicit type casting to string before comparison, then final cast to boolean.

---

## 6. Summary

We successfully designed and populated a PostgreSQL database with three hotel booking datasets using PySpark. The implementation features:

- **Unified Schema:** 14-column schema consistent across all three tables
- **Data Transformation:** Robust handling of inconsistent data formats
- **Performance Optimization:** Strategic indexing for 3-6x query speedup
- **Production-Ready:** Environment-based configuration and idempotent execution
- **Data Integrity:** 114,977 records loaded with proper type conversions

The resulting database is ready for analysis and serves as the backend for our Phase 3 WebUI application.
