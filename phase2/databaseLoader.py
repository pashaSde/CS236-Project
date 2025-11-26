"""
Database Loader Script
Loads hotel reservation datasets into PostgreSQL using PySpark
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
import os
import time

# Database connection properties
DB_PROPERTIES = {
    "user": "admin",
    "password": "secret123",
    "driver": "org.postgresql.Driver",
    "currentSchema": "innsight"  # Use innsight schema
}

DB_URL = "jdbc:postgresql://localhost:5432/reservations"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Go up one level to project root
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

DATASETS = {
    "customer_reservations": os.path.join(OUTPUT_DIR, "customer_reservations_cleaned.csv"),
    "hotel_bookings": os.path.join(OUTPUT_DIR, "hotel_bookings_cleaned.csv"),
    "merged_hotel_data": os.path.join(OUTPUT_DIR, "merged_hotel_data.csv")
}


def create_spark_session():
    """
    Create and configure Spark session with PostgreSQL support
    """
    print("Creating Spark session...")
    spark = SparkSession.builder \
        .appName("Hotel Reservations DB Loader") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .config("spark.driver.extraClassPath", "org.postgresql:postgresql:42.7.3") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .getOrCreate()

    print(f"Spark version: {spark.version}")
    return spark


def define_schema():
    """
    Define the common schema for all three tables based on merged_hotel_data.csv

    Schema has 14 columns:
    - id: Unique booking identifier
    - hotel: Hotel name/type
    - lead_time: Number of days between booking and arrival
    - arrival_year: Year of arrival
    - arrival_month: Month of arrival
    - arrival_date_week_number: Week number of arrival
    - arrival_date_day_of_month: Day of month of arrival
    - stays_in_weekend_nights: Number of weekend nights
    - stays_in_week_nights: Number of weekday nights
    - market_segment_type: Type of market segment
    - country: Country code
    - avg_price_per_room: Average price per room
    - email: Customer email
    - is_canceled: Cancellation status (boolean or string)
    """
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("hotel", StringType(), True),
        StructField("lead_time", IntegerType(), True),
        StructField("arrival_year", IntegerType(), True),
        StructField("arrival_month", IntegerType(), True),
        StructField("arrival_date_week_number", IntegerType(), True),
        StructField("arrival_date_day_of_month", IntegerType(), True),
        StructField("stays_in_weekend_nights", IntegerType(), True),
        StructField("stays_in_week_nights", IntegerType(), True),
        StructField("market_segment_type", StringType(), True),
        StructField("country", StringType(), True),
        StructField("avg_price_per_room", DoubleType(), True),
        StructField("email", StringType(), True),
        StructField("is_canceled", StringType(), True)
        # Using String to handle both "true/false" and "Canceled/Not_Canceled"
    ])
    return schema


def normalize_dataframe(df, source_type):
    """
    Normalize dataframe to match the common schema
    Handles different column names across datasets
    """
    print(f"  Normalizing {source_type} data...")

    # Show original columns
    print(f"  Original columns: {df.columns}")

    # Rename columns to match standard schema
    if "booking_id" in df.columns:
        df = df.withColumnRenamed("booking_id", "id")

    if "booking_status" in df.columns:
        # Convert booking_status to is_canceled format
        from pyspark.sql.functions import when
        df = df.withColumn("is_canceled",
                           when(df.booking_status == "Canceled", "true")
                           .otherwise("false"))
        df = df.drop("booking_status")

    # Ensure all 14 columns exist in correct order
    expected_columns = [
        "id", "hotel", "lead_time", "arrival_year", "arrival_month",
        "arrival_date_week_number", "arrival_date_day_of_month",
        "stays_in_weekend_nights", "stays_in_week_nights",
        "market_segment_type", "country", "avg_price_per_room",
        "email", "is_canceled"
    ]

    # Select columns in the correct order (add missing columns as null if needed)
    from pyspark.sql.functions import lit
    select_cols = []
    for col in expected_columns:
        if col in df.columns:
            select_cols.append(df[col])
        else:
            select_cols.append(lit(None).alias(col))

    df = df.select(select_cols)

    print(f"  Normalized columns: {df.columns}")
    return df


def load_csv_to_dataframe(spark, file_path, source_type):
    """
    Load CSV file into Spark DataFrame with schema inference
    """
    print(f"\nLoading {source_type} from: {file_path}")

    if not os.path.exists(file_path):
        print(f"  ERROR: File not found - {file_path}")
        return None

    # Read CSV with header
    df = spark.read.csv(
        file_path,
        header=True,
        inferSchema=True,
        mode="PERMISSIVE"
    )

    print(f"  Rows loaded: {df.count()}")
    print(f"  Schema:")
    df.printSchema()

    # Normalize to common schema
    df = normalize_dataframe(df, source_type)

    return df


def create_schema_if_not_exists(spark):
    """
    Create the innsight schema if it doesn't exist
    """
    print("\nChecking/Creating schema...")
    try:
        # Create a temporary connection to execute DDL
        from py4j.java_gateway import java_import
        java_import(spark._jvm, "java.sql.DriverManager")
        
        conn = spark._jvm.DriverManager.getConnection(
            DB_URL,
            DB_PROPERTIES["user"],
            DB_PROPERTIES["password"]
        )
        stmt = conn.createStatement()
        stmt.execute("CREATE SCHEMA IF NOT EXISTS innsight")
        stmt.close()
        conn.close()
        
        print(" Schema 'innsight' is ready")
        
    except Exception as e:
        print(f"Note: Schema creation status: {str(e)}")
        # Continue even if there's an error - schema might already exist


def create_table_and_load_data(df, table_name, mode="overwrite"):
    """
    Create table in PostgreSQL and load data

    Args:
        df: Spark DataFrame
        table_name: Name of the table to create (will be created in innsight schema)
        mode: Write mode - 'overwrite', 'append', 'ignore', 'error'
    """
    print(f"Loading data into table: innsight.{table_name}")
    print(f"Mode: {mode}")

    try:
        # Write DataFrame to PostgreSQL with schema prefix
        # The currentSchema property in DB_PROPERTIES will handle the schema
        df.write.jdbc(
            url=DB_URL,
            table=f"innsight.{table_name}",
            mode=mode,
            properties=DB_PROPERTIES
        )

        print(f" Successfully loaded {df.count()} rows into innsight.{table_name}")

    except Exception as e:
        print(f"✗ Error loading data into innsight.{table_name}: {str(e)}")
        raise


def verify_tables(spark):
    """
    Verify that tables were created and data was loaded correctly
    """
    print("VERIFYING TABLES")

    tables = ["customer_reservations", "hotel_bookings", "merged_hotel_data"]

    for table_name in tables:
        try:
            df = spark.read.jdbc(
                url=DB_URL,
                table=f"innsight.{table_name}",
                properties=DB_PROPERTIES
            )

            row_count = df.count()
            print(f"\n Table: innsight.{table_name}")
            print(f"  Rows: {row_count}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Schema:")
            df.printSchema()

            # Show first 3 rows
            print(f"  Sample data:")
            df.show(3, truncate=True)

        except Exception as e:
            print(f"\n✗ Error reading table innsight.{table_name}: {str(e)}")


def main():
    """
    Main execution function
    """
    print("HOTEL RESERVATIONS DATABASE LOADER")

    # Create Spark session
    spark = create_spark_session()

    try:
        # Create schema in database
        create_schema_if_not_exists(spark)
        
        # Define common schema
        schema = define_schema()
        print("\n Schema defined with 14 columns")

        # Load and process each dataset
        for table_name, file_path in DATASETS.items():
            print(f"PROCESSING: {table_name}")

            # Load CSV to DataFrame
            df = load_csv_to_dataframe(spark, file_path, table_name)

            if df is None:
                print(f"Skipping {table_name} due to loading error")
                continue

            # Create table and load data
            create_table_and_load_data(df, table_name, mode="overwrite")

        # Verify all tables
        verify_tables(spark)

        print("DATABASE LOADING COMPLETED SUCCESSFULLY!")
        print("\nDatabase Connection Details:")
        print(f"  Host: localhost:5432")
        print(f"  Database: reservations")
        print(f"  Schema: innsight")
        print(f"  User: admin")
        print(f"  Tables created: innsight.customer_reservations, innsight.hotel_bookings, innsight.merged_hotel_data")
        
        # Keep Spark Web UI running for exploration
        print("\n" + "=" * 60)
        print("SPARK WEB UI is available at: http://localhost:4040")
        print("=" * 60)
        print("\nPress Ctrl+C to stop Spark and exit...")
        print("(Keeping Web UI active for 5 minutes...)\n")
        
        # Keep alive with periodic updates
        try:
            for remaining in range(300, 0, -30):  # 5 minutes, update every 30 seconds
                print(f"Web UI still active... ({remaining} seconds remaining, press Ctrl+C to exit now)")
                time.sleep(30)
            print("\nTimeout reached after 5 minutes.")
        except KeyboardInterrupt:
            print("\n\nCtrl+C received. Shutting down...")

    except Exception as e:
        print(f"\n✗ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # Stop Spark session
        spark.stop()
        print("\n Spark session stopped")


if __name__ == "__main__":
    main()