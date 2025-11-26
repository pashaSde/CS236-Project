from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import matplotlib.pyplot as plt
import sys
import seaborn as sns
import os
import shutil
import glob

def save_single_csv(df, output_path):
    """
    Save a Spark DataFrame as a single CSV file with a specific name.
    Handles Spark's partitioned output by extracting the CSV and renaming it.
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create temporary directory for Spark output
    temp_dir = output_path + "_temp"
    
    # Remove temp directory if it exists
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    # Write to temporary directory
    df.coalesce(1).write.mode('overwrite').option('header', 'true').csv(temp_dir)
    
    # Find the CSV file in the temp directory (ignoring _SUCCESS file)
    csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
    if csv_files:
        csv_file = csv_files[0]
        
        # Remove existing output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Move and rename the CSV file
        shutil.move(os.path.join(temp_dir, csv_file), output_path)
    
    # Remove the temporary directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def perform_eda(df, data_name="dataset"):
    print("\nSchema:")
    df.printSchema()

    print("\nRow Count:")
    print(df.count())

    print("\nColumn Count:")
    print(len(df.columns))

    print("\nColumns:")
    print(df.columns)

    print("\nData Sample:")
    df.show(5)

    print("\nSummary Statistics:")
    df.describe().show()

    print("\nMissing Values Count:")
    missing_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    missing_counts.show()

    print("\nDistinct Values Count:")
    distinct_counts = df.agg(*[countDistinct(c).alias(c) for c in df.columns])
    distinct_counts.show()

    numeric_cols = [f.name for f in df.schema.fields if isinstance(f.dataType, (IntegerType, DoubleType, FloatType, LongType))]
    if len(numeric_cols) > 1:
        pdf = df.select(numeric_cols).toPandas()
        corr = pdf.corr()
        plt.figure(figsize=(8,6))
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title(f'Correlation Matrix for {data_name}')
        plt.tight_layout()
        plt.savefig(f'eda_{data_name}_correlation.png')
        plt.close()

def merge_datasets(customer_df, hotel_df):
    """
    Merge customer reservations and hotel bookings datasets using PySpark.
    This function handles schema alignment and combines both datasets into a unified format.
    """
    print("\n" + "="*80)
    print("DATA MERGING PROCESS")
    print("="*80)
    
    # Analyze column differences
    print("\n" + "-"*80)
    print("COLUMN ANALYSIS")
    print("-"*80)
    customer_cols = set(customer_df.columns)
    hotel_cols = set(hotel_df.columns)
    
    # Identify common columns (accounting for naming differences)
    common_cols = customer_cols.intersection(hotel_cols)
    customer_only = customer_cols - hotel_cols - {'Booking_ID', 'arrival_date'}  # These get renamed
    hotel_only = hotel_cols - customer_cols - {'booking_status', 'arrival_date_day_of_month'}  # These have equivalents
    
    print(f"\nCommon columns ({len(common_cols)}): {sorted(common_cols)}")
    print(f"\nSemantic equivalents (different names, same meaning):")
    print(f"   • Booking_ID (customer) ↔ booking_id (hotel) - will be unified")
    print(f"   • arrival_date (customer) ↔ arrival_date_day_of_month (hotel) - same field")
    print(f"   • booking_status: text (customer) ↔ 0/1 (hotel) - will be standardized")
    print(f"\nCustomer-only columns ({len(customer_only)}): {sorted(customer_only)}")
    print(f"\nHotel-only columns ({len(hotel_only)}): {sorted(hotel_only)}")
    print(f"\nCustomer records: {customer_df.count():,}")
    print(f"Hotel records: {hotel_df.count():,}")
    
    # Step 1: Standardize customer dataset
    print("\n" + "-"*80)
    print("STEP 1: STANDARDIZING CUSTOMER DATA")
    print("-"*80)
    
    # Rename columns for consistency
    customer_clean = customer_df \
        .withColumnRenamed('Booking_ID', 'booking_id') \
        .withColumnRenamed('arrival_date', 'arrival_date_day_of_month')
    
    # Add missing columns with default values
    customer_clean = customer_clean \
        .withColumn('hotel', lit('Unknown')) \
        .withColumn('country', lit('Unknown')) \
        .withColumn('email', lit('Unknown')) \
        .withColumn('arrival_date_week_number', lit(0))
    
    print(" Customer dataset standardized")
    
    # Step 2: Standardize hotel dataset
    print("\n" + "-"*80)
    print("STEP 2: STANDARDIZING HOTEL DATA")
    print("-"*80)
    
    # Standardize booking_status (0/1 to Not_Canceled/Canceled)
    hotel_clean = hotel_df.withColumn(
        'booking_status',
        when(col('booking_status') == 0, 'Not_Canceled').otherwise('Canceled')
    )
    
    # Convert arrival_month from text to numeric
    hotel_clean = hotel_clean.withColumn(
        'arrival_month',
        when(col('arrival_month') == 'January', 1)
        .when(col('arrival_month') == 'February', 2)
        .when(col('arrival_month') == 'March', 3)
        .when(col('arrival_month') == 'April', 4)
        .when(col('arrival_month') == 'May', 5)
        .when(col('arrival_month') == 'June', 6)
        .when(col('arrival_month') == 'July', 7)
        .when(col('arrival_month') == 'August', 8)
        .when(col('arrival_month') == 'September', 9)
        .when(col('arrival_month') == 'October', 10)
        .when(col('arrival_month') == 'November', 11)
        .when(col('arrival_month') == 'December', 12)
        .otherwise(0)
    )
    
    # Generate booking IDs for hotel data
    hotel_clean = hotel_clean.withColumn(
        'booking_id',
        concat(lit('HTL'), lpad(monotonically_increasing_id().cast('string'), 6, '0'))
    )
    
    print(" Hotel dataset standardized")
    
    # Step 2.5: Save cleaned individual datasets
    print("\n" + "-"*80)
    print("SAVING CLEANED INDIVIDUAL DATASETS")
    print("-"*80)
    
    save_single_csv(customer_clean, 'output/customer_reservations_cleaned.csv')
    print(" Saved cleaned customer dataset to: output/customer_reservations_cleaned.csv")
    
    save_single_csv(hotel_clean, 'output/hotel_bookings_cleaned.csv')
    print(" Saved cleaned hotel dataset to: output/hotel_bookings_cleaned.csv")
    
    # Step 3: Select common columns in same order and add source identifier
    print("\n" + "-"*80)
    print("STEP 3: ALIGNING SCHEMAS FOR MERGE")
    print("-"*80)
    
    # Add source identifier for tracking in merged dataset
    customer_for_merge = customer_clean.withColumn('data_source', lit('customer_reservations'))
    hotel_for_merge = hotel_clean.withColumn('data_source', lit('hotel_bookings'))
    
    # Define unified column list (includes data_source for merged dataset)
    unified_columns = [
        'booking_id', 'hotel', 'booking_status', 'lead_time', 
        'arrival_year', 'arrival_month', 'arrival_date_week_number',
        'arrival_date_day_of_month', 'stays_in_weekend_nights', 
        'stays_in_week_nights', 'market_segment_type', 
        'country', 'avg_price_per_room', 'email', 'data_source'
    ]
    
    customer_aligned = customer_for_merge.select(*unified_columns)
    hotel_aligned = hotel_for_merge.select(*unified_columns)
    
    print(f" Aligned both datasets to {len(unified_columns)} common columns")
    
    # Step 4: Union datasets
    print("\n" + "-"*80)
    print("STEP 4: MERGING DATASETS")
    print("-"*80)
    
    merged_df = customer_aligned.union(hotel_aligned)
    
    print(f" Successfully merged datasets!")
    print(f"  - Total merged records: {merged_df.count():,}")
    
    # Step 5: Create derived features
    print("\n" + "-"*80)
    print("STEP 5: FEATURE ENGINEERING")
    print("-"*80)
    
    merged_df = merged_df \
        .withColumn('total_nights', col('stays_in_weekend_nights') + col('stays_in_week_nights')) \
        .withColumn('total_revenue', col('avg_price_per_room') * 
                    (col('stays_in_weekend_nights') + col('stays_in_week_nights')))
    
    print(" Created derived features: total_nights, total_revenue")
    
    # Step 6: Data quality summary
    print("\n" + "-"*80)
    print("MERGED DATA SUMMARY")
    print("-"*80)
    
    print("\nMerged Schema:")
    merged_df.printSchema()
    
    print("\nSample of merged data:")
    merged_df.show(5, truncate=False)
    
    print("\nRecords by source:")
    merged_df.groupBy('data_source').count().show()
    
    print("\nBooking status distribution:")
    merged_df.groupBy('booking_status').count().show()
    
    print("\nBasic statistics:")
    merged_df.select('lead_time', 'total_nights', 'avg_price_per_room', 'total_revenue').describe().show()
    
    # Step 7: Save merged dataset
    print("\n" + "-"*80)
    print("SAVING MERGED DATA")
    print("-"*80)
    
    output_path = 'output/merged_hotel_data.csv'
    save_single_csv(merged_df, output_path)
    print(f" Merged dataset saved to: {output_path}")
    
    print("\n" + "="*80)
    print("DATA MERGE COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\n📁 OUTPUT FILES CREATED:")
    print("   1. output/customer_reservations_cleaned.csv (cleaned customer data)")
    print("   2. output/hotel_bookings_cleaned.csv (cleaned hotel data)")
    print("   3. output/merged_hotel_data.csv (unified merged data)")
    
    return merged_df

def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("HotelBooking") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    # Load Data Sets
    customer_reservartions = spark.read.csv("data/customer-reservations.csv", header=True, inferSchema=True)
    hotel_bookings = spark.read.csv("data/hotel-booking.csv", header=True, inferSchema=True)

    if customer_reservartions is None or hotel_bookings is None:
        print("Datasets not loaded properly")   
        sys.exit(1)

    # EDA on customer_reservartions
    print("\nEDA on Customer Reservartions Data:")
    perform_eda(customer_reservartions, "customer_reservartions")

    # EDA on hotel_bookings
    print("\nEDA on Hotel Bookings Data:")
    perform_eda(hotel_bookings, "hotel_bookings")

    # Merge datasets
    print("\n" + "="*80)
    print("PHASE 2: DATA INTEGRATION")
    print("="*80)
    merged_data = merge_datasets(customer_reservartions, hotel_bookings)
    
    print(f"\n Analysis complete! Merged dataset has {merged_data.count():,} total records.")

    spark.stop()

if __name__ == "__main__":
    main()