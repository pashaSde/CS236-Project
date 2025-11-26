"""
Phase 2: Database Loader
Loads cleaned hotel reservation datasets into PostgreSQL using PySpark
"""

import os
import time

from py4j.java_gateway import java_import
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, lit
from pyspark.sql.types import StringType, BooleanType

# Database configuration
DB_CONFIG = {
    "user": "admin",
    "password": os.getenv("POSTGRES_PWD", ""),
    "driver": "org.postgresql.Driver"
}

DB_URL = "jdbc:postgresql://localhost:5432/innsight"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Datasets to load
DATASETS = {
    "customer_reservations": os.path.join(OUTPUT_DIR, "customer_reservations_cleaned.csv"),
    "hotel_bookings": os.path.join(OUTPUT_DIR, "hotel_bookings_cleaned.csv"),
    "merged_hotel_data": os.path.join(OUTPUT_DIR, "merged_hotel_data.csv")
}


def get_spark_session():
    """Initialize Spark session with PostgreSQL JDBC driver"""
    print("Starting Spark session...")
    
    spark = SparkSession.builder \
        .appName("Hotel Reservations DB Loader") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .config("spark.driver.host", "localhost") \
        .getOrCreate()
    
    print(f"Spark {spark.version} initialized\n")
    return spark


def get_db_connection(spark):
    """Create JDBC connection for DDL operations"""
    java_import(spark._jvm, "java.sql.DriverManager")
    return spark._jvm.DriverManager.getConnection(
        DB_URL, DB_CONFIG["user"], DB_CONFIG["password"]
    )


def create_schema(spark):
    """Using default public schema (no custom schema needed)"""
    print("Using default public schema...")
    print("\nSchema ready\n")


def normalize_booking_status(df):
    """Convert various booking status formats to boolean"""
    if "booking_status" in df.columns:
        # Convert "Canceled"/"Not_Canceled" to boolean
        df = df.withColumn("is_canceled", 
                          when(col("booking_status") == "Canceled", True).otherwise(False))
        df = df.drop("booking_status")
    
    elif "is_canceled" in df.columns:
        # First cast to string to handle all formats uniformly
        df = df.withColumn("is_canceled", col("is_canceled").cast(StringType()))
        
        # Convert string formats to boolean: "true", "false", "Canceled", "Not_Canceled"
        df = df.withColumn("is_canceled",
                          when(col("is_canceled").isin("true", "True", "1", "Canceled"), lit(True))
                          .when(col("is_canceled").isin("false", "False", "0", "Not_Canceled"), lit(False))
                          .otherwise(lit(None)).cast(BooleanType()))
    
    return df


def normalize_columns(df):
    """Ensure all datasets have the same 14 columns in the same order"""
    # Rename booking_id to id if present
    if "booking_id" in df.columns:
        df = df.withColumnRenamed("booking_id", "id")
    
    # Normalize booking status to boolean
    df = normalize_booking_status(df)
    
    # Define expected columns
    expected_cols = [
        "id", "hotel", "lead_time", "arrival_year", "arrival_month",
        "arrival_date_week_number", "arrival_date_day_of_month",
        "stays_in_weekend_nights", "stays_in_week_nights",
        "market_segment_type", "country", "avg_price_per_room",
        "email", "is_canceled"
    ]
    
    # Select columns in order, adding nulls for missing ones
    select_cols = [df[c] if c in df.columns else lit(None).alias(c) for c in expected_cols]
    return df.select(select_cols)


def load_csv(spark, file_path, dataset_name):
    """Load and normalize CSV file"""
    print(f"Loading {dataset_name}...")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found - {file_path}")
        return None
    
    # Read CSV with schema inference
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    row_count = df.count()
    
    # Normalize to common schema
    df = normalize_columns(df)
    
    print(f"Loaded {row_count:,} rows")
    return df


def load_to_postgres(df, table_name):
    """Write dataframe to PostgreSQL table"""
    print(f"Writing to {table_name}...")
    
    df.write.jdbc(
        url=DB_URL,
        table=table_name,  # Uses public schema by default
        mode="overwrite",  # Drop and recreate table
        properties=DB_CONFIG
    )
    
    print(f"{df.count():,} rows loaded\n")


def create_indexes(spark):
    """Create indexes on commonly filtered columns for better query performance"""
    print("Creating indexes for Phase 3 WebUI performance...")

    try:
        conn = get_db_connection(spark)
        stmt = conn.createStatement()
        
        tables = ["customer_reservations", "hotel_bookings", "merged_hotel_data"]
        
        for table in tables:
            print(f"Indexing {table}...")
            
            # Create indexes on filter columns
            indexes = [
                f"CREATE INDEX IF NOT EXISTS {table}_idx_price ON {table}(avg_price_per_room)",
                f"CREATE INDEX IF NOT EXISTS {table}_idx_status ON {table}(is_canceled)",
                f"CREATE INDEX IF NOT EXISTS {table}_idx_date ON {table}(arrival_year, arrival_month)",
                f"CREATE INDEX IF NOT EXISTS {table}_idx_segment ON {table}(market_segment_type)"
            ]
            
            for idx_sql in indexes:
                stmt.execute(idx_sql)
            
            # Update table statistics for query optimizer
            stmt.execute(f"ANALYZE {table}")
        
        stmt.close()
        conn.close()

    except Exception as e:
        print(f"Index creation warning: {e}\n")


def verify_data(spark):
    """Quick verification of loaded data"""
    print("Verifying loaded data...")
    
    tables = ["customer_reservations", "hotel_bookings", "merged_hotel_data"]
    
    for table in tables:
        try:
            df = spark.read.jdbc(
                url=DB_URL,
                table=table,
                properties=DB_CONFIG
            )
            
            row_count = df.count()
            col_count = len(df.columns)
            print(f"   {table}: {row_count:,} rows, {col_count} columns")
            
        except Exception as e:
            print(f"   {table}: {str(e)}")
    
    print()


def main():
    """Main execution"""
    print("HOTEL RESERVATIONS DATABASE LOADER")
    print()
    
    spark = get_spark_session()
    
    try:
        # Step 1: Create schema
        create_schema(spark)
        
        # Step 2: Load each dataset
        for table_name, file_path in DATASETS.items():
            df = load_csv(spark, file_path, table_name)
            if df:
                load_to_postgres(df, table_name)
        
        # Step 3: Create indexes for WebUI
        create_indexes(spark)
        
        # Step 4: Verify everything loaded correctly
        verify_data(spark)
        
        # Summary
        print(" DATABASE LOADING COMPLETE")
        print(f"Database: innsight")
        print(f"Schema: public (default)")
        print(f"Tables: 3 (customer_reservations, hotel_bookings, merged_hotel_data)")
        print()
        
        # Keep Spark Web UI running for inspection
        print("Spark Web UI: http://localhost:4040")
        print("Press Ctrl+C to exit...\n")
        
        try:
            for i in range(300, 0, -30):  # 5 minute timeout
                print(f"  {i}s remaining (Ctrl+C to exit now)")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n  Shutting down...")
    
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        spark.stop()
        print(" Spark session stopped\n")


if __name__ == "__main__":
    main()