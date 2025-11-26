#!/usr/bin/env python3
"""
PySpark Data Transformation and Merging Script - Fixed Version
Merges hotel booking and customer reservation datasets into a unified dataset.

This script performs:
- Schema analysis and alignment
- Data cleaning and transformation
- Feature engineering for merging
- Dataset merging with consistent schema
- Saving cleaned and merged datasets as CSV files
"""

import os
# Set Java home for OpenJDK 17
os.environ['JAVA_HOME'] = '/opt/homebrew/opt/openjdk@17'

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, concat, format_string, monotonically_increasing_id, count, avg, min, max, sum, desc
from pyspark.sql.types import *
from datetime import datetime

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("HotelDataMerge") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

# Set log level to reduce verbosity
spark.sparkContext.setLogLevel("WARN")

print("=" * 80)
print("PYSPARK DATA TRANSFORMATION AND MERGING")
print("=" * 80)
print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    # Load original datasets
    print("\n" + "=" * 80)
    print("LOADING ORIGINAL DATASETS")
    print("=" * 80)
    
    print("Loading hotel booking data...")
    hotel_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv("CS236_Project_Fall2025_Datasets/hotel-booking.csv")
    
    print("Loading customer reservation data...")
    customer_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv("CS236_Project_Fall2025_Datasets/customer-reservations.csv")
    
    print("✅ Original datasets loaded successfully!")
    
    # Schema analysis
    print("\n" + "=" * 80)
    print("SCHEMA ANALYSIS")
    print("=" * 80)
    
    print("\n HOTEL BOOKING DATASET SCHEMA:")
    print("-" * 50)
    hotel_df.printSchema()
    print(f"Columns: {hotel_df.columns}")
    print(f"Row count: {hotel_df.count():,}")
    
    print("\n CUSTOMER RESERVATION DATASET SCHEMA:")
    print("-" * 50)
    customer_df.printSchema()
    print(f"Columns: {customer_df.columns}")
    print(f"Row count: {customer_df.count():,}")
    
    # Identify overlapping and unique columns
    hotel_cols = set(hotel_df.columns)
    customer_cols = set(customer_df.columns)
    
    overlapping_cols = hotel_cols.intersection(customer_cols)
    hotel_unique = hotel_cols - customer_cols
    customer_unique = customer_cols - hotel_cols
    
    print(f"\n COLUMN ANALYSIS:")
    print(f"   • Overlapping columns: {sorted(overlapping_cols)}")
    print(f"   • Hotel unique columns: {sorted(hotel_unique)}")
    print(f"   • Customer unique columns: {sorted(customer_unique)}")
    
    # Data type analysis for overlapping columns
    print(f"\n DATA TYPE ANALYSIS FOR OVERLAPPING COLUMNS:")
    for col_name in overlapping_cols:
        hotel_type = dict(hotel_df.dtypes)[col_name]
        customer_type = dict(customer_df.dtypes)[col_name]
        print(f"   • {col_name}: Hotel={hotel_type}, Customer={customer_type}")
    
    # Data cleaning and transformation
    print("\n" + "=" * 80)
    print("DATA CLEANING AND TRANSFORMATION")
    print("=" * 80)
    
    # Clean Hotel Dataset
    print("\n🧹 CLEANING HOTEL DATASET:")
    print("-" * 40)
    
    # Handle null values in country column
    hotel_cleaned = hotel_df.fillna({"country": "Unknown"})
    
    # Standardize booking_status (0/1 to Not_Canceled/Canceled)
    hotel_cleaned = hotel_cleaned.withColumn(
        "booking_status_standardized",
        when(col("booking_status") == 0, "Not_Canceled")
        .otherwise("Canceled")
    )
    
    # Standardize market_segment_type
    hotel_cleaned = hotel_cleaned.withColumn(
        "market_segment_standardized",
        when(col("market_segment_type") == "Online TA", "Online")
        .when(col("market_segment_type") == "Offline TA/TO", "Offline")
        .otherwise(col("market_segment_type"))
    )
    
    # Convert arrival_month to numeric for consistency
    hotel_cleaned = hotel_cleaned.withColumn(
        "arrival_month_numeric",
        when(col("arrival_month") == "January", 1)
        .when(col("arrival_month") == "February", 2)
        .when(col("arrival_month") == "March", 3)
        .when(col("arrival_month") == "April", 4)
        .when(col("arrival_month") == "May", 5)
        .when(col("arrival_month") == "June", 6)
        .when(col("arrival_month") == "July", 7)
        .when(col("arrival_month") == "August", 8)
        .when(col("arrival_month") == "September", 9)
        .when(col("arrival_month") == "October", 10)
        .when(col("arrival_month") == "November", 11)
        .when(col("arrival_month") == "December", 12)
        .otherwise(0)
    )
    
    # Create derived features
    hotel_cleaned = hotel_cleaned.withColumn(
        "total_stay_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    )
    
    # Add dataset identifier
    hotel_cleaned = hotel_cleaned.withColumn("dataset_source", lit("hotel_booking"))
    
    # Generate unique booking ID for hotel data
    hotel_cleaned = hotel_cleaned.withColumn(
        "booking_id",
        concat(lit("HTL"), format_string("%06d", monotonically_increasing_id()))
    )
    
    print("✅ Hotel dataset cleaned and transformed!")
    
    # Clean Customer Dataset
    print("\n🧹 CLEANING CUSTOMER DATASET:")
    print("-" * 40)
    
    # Standardize market_segment_type
    customer_cleaned = customer_df.withColumn(
        "market_segment_standardized",
        col("market_segment_type")
    )
    
    # Standardize booking_status
    customer_cleaned = customer_cleaned.withColumn(
        "booking_status_standardized",
        col("booking_status")
    )
    
    # Create derived features
    customer_cleaned = customer_cleaned.withColumn(
        "total_stay_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    )
    
    # Add dataset identifier
    customer_cleaned = customer_cleaned.withColumn("dataset_source", lit("customer_reservation"))
    
    # Add missing columns with default values
    customer_cleaned = customer_cleaned.withColumn("hotel", lit("Unknown"))
    customer_cleaned = customer_cleaned.withColumn("country", lit("Unknown"))
    customer_cleaned = customer_cleaned.withColumn("email", lit("Unknown"))
    customer_cleaned = customer_cleaned.withColumn("arrival_date_week_number", lit(0))
    
    print("✅ Customer dataset cleaned and transformed!")
    
    # Schema alignment for merging
    print("\n" + "=" * 80)
    print("SCHEMA ALIGNMENT FOR MERGING")
    print("=" * 80)
    
    # Select and rename columns for hotel dataset
    hotel_unified = hotel_cleaned.select(
        col("booking_id").alias("booking_id"),
        col("hotel").alias("hotel"),
        col("booking_status_standardized").alias("booking_status_standardized"),
        col("lead_time").alias("lead_time"),
        col("arrival_year").alias("arrival_year"),
        col("arrival_month_numeric").alias("arrival_month_numeric"),
        col("arrival_date_week_number").alias("arrival_date_week_number"),
        col("arrival_date_day_of_month").alias("arrival_date_day_of_month"),
        col("stays_in_weekend_nights").alias("stays_in_weekend_nights"),
        col("stays_in_week_nights").alias("stays_in_week_nights"),
        col("total_stay_nights").alias("total_stay_nights"),
        col("market_segment_standardized").alias("market_segment_standardized"),
        col("country").alias("country"),
        col("avg_price_per_room").alias("avg_price_per_room"),
        col("email").alias("email"),
        col("dataset_source").alias("dataset_source")
    )
    
    # Select and rename columns for customer dataset
    customer_unified = customer_cleaned.select(
        col("Booking_ID").alias("booking_id"),
        col("hotel").alias("hotel"),
        col("booking_status_standardized").alias("booking_status_standardized"),
        col("lead_time").alias("lead_time"),
        col("arrival_year").alias("arrival_year"),
        col("arrival_month").alias("arrival_month_numeric"),
        col("arrival_date_week_number").alias("arrival_date_week_number"),
        col("arrival_date").alias("arrival_date_day_of_month"),
        col("stays_in_weekend_nights").alias("stays_in_weekend_nights"),
        col("stays_in_week_nights").alias("stays_in_week_nights"),
        col("total_stay_nights").alias("total_stay_nights"),
        col("market_segment_standardized").alias("market_segment_standardized"),
        col("country").alias("country"),
        col("avg_price_per_room").alias("avg_price_per_room"),
        col("email").alias("email"),
        col("dataset_source").alias("dataset_source")
    )
    
    print("✅ Schema alignment completed!")
    
    # Merge datasets
    print("\n" + "=" * 80)
    print("MERGING DATASETS")
    print("=" * 80)
    
    # Union the datasets
    merged_df = hotel_unified.union(customer_unified)
    
    print(f"✅ Datasets merged successfully!")
    print(f"   • Hotel records: {hotel_unified.count():,}")
    print(f"   • Customer records: {customer_unified.count():,}")
    print(f"   • Total merged records: {merged_df.count():,}")
    
    # Final data quality check
    print("\n" + "=" * 80)
    print("FINAL DATA QUALITY CHECK")
    print("=" * 80)
    
    print("\n MERGED DATASET SCHEMA:")
    merged_df.printSchema()
    
    print("\n NULL VALUE CHECK:")
    null_counts = merged_df.select([count(when(col(c).isNull(), c)).alias(c) for c in merged_df.columns])
    null_counts.show(vertical=True)
    
    print("\n SAMPLE DATA:")
    merged_df.show(5, truncate=False)
    
    # Save cleaned and merged datasets
    print("\n" + "=" * 80)
    print("SAVING DATASETS")
    print("=" * 80)
    
    # Create output directory
    output_dir = "cleaned_datasets"
    
    print(f"\n SAVING CLEANED HOTEL DATASET:")
    hotel_output_path = f"{output_dir}/hotel_booking_cleaned.csv"
    hotel_unified.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(hotel_output_path)
    print(f"   ✅ Saved to: {hotel_output_path}")
    
    print(f"\n SAVING CLEANED CUSTOMER DATASET:")
    customer_output_path = f"{output_dir}/customer_reservation_cleaned.csv"
    customer_unified.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(customer_output_path)
    print(f"   ✅ Saved to: {customer_output_path}")
    
    print(f"\n SAVING MERGED DATASET:")
    merged_output_path = f"{output_dir}/unified_hotel_data.csv"
    merged_df.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(merged_output_path)
    print(f"   ✅ Saved to: {merged_output_path}")
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("TRANSFORMATION SUMMARY REPORT")
    print("=" * 80)
    
    print(f"\n📋 TRANSFORMATION DECISIONS:")
    print("   1. Schema Alignment:")
    print("      • Standardized booking_status: 0/1 → Not_Canceled/Canceled")
    print("      • Standardized market_segment: Online TA → Online, Offline TA/TO → Offline")
    print("      • Converted arrival_month to numeric for consistency")
    print("      • Added missing columns with default values")
    
    print("\n   2. Data Cleaning:")
    print("      • Filled null values in country column with 'Unknown'")
    print("      • Generated unique booking IDs for hotel data")
    print("      • Added dataset source identifier")
    
    print("\n   3. Feature Engineering:")
    print("      • Created total_stay_nights = weekend_nights + week_nights")
    print("      • Added dataset_source column for traceability")
    
    print("\n   4. Schema Unification:")
    print("      • Aligned all columns to consistent naming and types")
    print("      • Ensured all datasets have same column structure")
    
    print(f"\n FINAL DATASET STATISTICS:")
    print(f"   • Hotel cleaned records: {hotel_unified.count():,}")
    print(f"   • Customer cleaned records: {customer_unified.count():,}")
    print(f"   • Total unified records: {merged_df.count():,}")
    print(f"   • Unified columns: {len(merged_df.columns)}")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   1. {hotel_output_path}/")
    print(f"   2. {customer_output_path}/")
    print(f"   3. {merged_output_path}/")
    
    print(f"\n✅ Data transformation and merging completed successfully!")
    print(f"   Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
except Exception as e:
    print(f"❌ Error during transformation: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    # Clean up Spark session
    spark.stop()
    print("\n Spark session stopped.")
