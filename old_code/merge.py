"""
Data Merge Module
Handles cleaning, standardization, and merging of hotel booking datasets.
"""

from pyspark.sql.functions import *
import os
import shutil


def save_single_csv(df, output_path):
    """
    Save a Spark DataFrame as a single CSV file with a specific name.
    Handles Spark's partitioned output by extracting the CSV and renaming it.
    
    Args:
        df: Spark DataFrame to save
        output_path: Desired output path (e.g., 'output/file.csv')
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


def analyze_column_overlap(customer_df, hotel_df):
    """
    Analyze column overlap and differences between datasets.
    
    Args:
        customer_df: Customer reservations DataFrame
        hotel_df: Hotel bookings DataFrame
    """
    print("\n" + "-"*80)
    print("COLUMN OVERLAP ANALYSIS")
    print("-"*80)
    
    customer_cols = set(customer_df.columns)
    hotel_cols = set(hotel_df.columns)
    
    # Identify common columns (accounting for naming differences)
    common_cols = customer_cols.intersection(hotel_cols)
    customer_only = customer_cols - hotel_cols - {'Booking_ID', 'arrival_date'}
    hotel_only = hotel_cols - customer_cols - {'booking_status', 'arrival_date_day_of_month'}
    
    print(f"\nCommon columns ({len(common_cols)}): {sorted(common_cols)}")
    print(f"\nSemantic equivalents (different names, same meaning):")
    print(f"   • Booking_ID (customer) ↔ booking_id (hotel) - will be unified")
    print(f"   • arrival_date (customer) ↔ arrival_date_day_of_month (hotel) - same field")
    print(f"   • booking_status: text (customer) ↔ 0/1 (hotel) - will be standardized")
    print(f"\nCustomer-only columns ({len(customer_only)}): {sorted(customer_only)}")
    print(f"\nHotel-only columns ({len(hotel_only)}): {sorted(hotel_only)}")
    print(f"\nRecord counts:")
    print(f"   • Customer: {customer_df.count():,}")
    print(f"   • Hotel: {hotel_df.count():,}")


def clean_customer_data(customer_df):
    """
    Clean and standardize customer reservations dataset.
    
    Args:
        customer_df: Raw customer reservations DataFrame
        
    Returns:
        Cleaned customer DataFrame
    """
    print("\n" + "-"*80)
    print("STEP 1: CLEANING CUSTOMER DATA")
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
    
    print(" Customer dataset cleaned:")
    print("  - Renamed columns: Booking_ID → booking_id, arrival_date → arrival_date_day_of_month")
    print("  - Added missing columns: hotel, country, email, arrival_date_week_number")
    
    return customer_clean


def clean_hotel_data(hotel_df):
    """
    Clean and standardize hotel bookings dataset.
    
    Args:
        hotel_df: Raw hotel bookings DataFrame
        
    Returns:
        Cleaned hotel DataFrame
    """
    print("\n" + "-"*80)
    print("STEP 2: CLEANING HOTEL DATA")
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
    
    print(" Hotel dataset cleaned:")
    print("  - Standardized booking_status: 0/1 → Not_Canceled/Canceled")
    print("  - Converted arrival_month: text → numeric (1-12)")
    print("  - Generated unique booking_id with HTL prefix")
    
    return hotel_clean


def save_cleaned_datasets(customer_clean, hotel_clean):
    """
    Save cleaned individual datasets to CSV files.
    
    Args:
        customer_clean: Cleaned customer DataFrame
        hotel_clean: Cleaned hotel DataFrame
    """
    print("\n" + "-"*80)
    print("STEP 3: SAVING CLEANED DATASETS")
    print("-"*80)
    
    save_single_csv(customer_clean, 'output/customer_reservations_cleaned.csv')
    print(" Saved: output/customer_reservations_cleaned.csv")
    
    save_single_csv(hotel_clean, 'output/hotel_bookings_cleaned.csv')
    print(" Saved: output/hotel_bookings_cleaned.csv")


def align_schemas(customer_clean, hotel_clean):
    """
    Align schemas of both datasets for merging.
    
    Args:
        customer_clean: Cleaned customer DataFrame
        hotel_clean: Cleaned hotel DataFrame
        
    Returns:
        tuple: (customer_aligned, hotel_aligned) with unified schema
    """
    print("\n" + "-"*80)
    print("STEP 4: ALIGNING SCHEMAS")
    print("-"*80)
    
    # Add source identifier for tracking in merged dataset
    customer_for_merge = customer_clean.withColumn('data_source', lit('customer_reservations'))
    hotel_for_merge = hotel_clean.withColumn('data_source', lit('hotel_bookings'))
    
    # Define unified column list
    unified_columns = [
        'booking_id', 'hotel', 'booking_status', 'lead_time', 
        'arrival_year', 'arrival_month', 'arrival_date_week_number',
        'arrival_date_day_of_month', 'stays_in_weekend_nights', 
        'stays_in_week_nights', 'market_segment_type', 
        'country', 'avg_price_per_room', 'email', 'data_source'
    ]
    
    customer_aligned = customer_for_merge.select(*unified_columns)
    hotel_aligned = hotel_for_merge.select(*unified_columns)
    
    print(f" Schemas aligned with {len(unified_columns)} common columns")
    print(f"  Columns: {unified_columns[:5]}... (and {len(unified_columns)-5} more)")
    
    return customer_aligned, hotel_aligned


def merge_datasets(customer_aligned, hotel_aligned):
    """
    Merge aligned datasets using union operation.
    
    Args:
        customer_aligned: Customer DataFrame with aligned schema
        hotel_aligned: Hotel DataFrame with aligned schema
        
    Returns:
        Merged DataFrame
    """
    print("\n" + "-"*80)
    print("STEP 5: MERGING DATASETS")
    print("-"*80)
    
    merged_df = customer_aligned.union(hotel_aligned)
    
    print(f" Datasets merged successfully!")
    print(f"   • Customer records: {customer_aligned.count():,}")
    print(f"   • Hotel records: {hotel_aligned.count():,}")
    print(f"   • Total records: {merged_df.count():,}")
    
    return merged_df


def add_derived_features(merged_df):
    """
    Add derived features to the merged dataset.
    
    Args:
        merged_df: Merged DataFrame
        
    Returns:
        DataFrame with derived features
    """
    print("\n" + "-"*80)
    print("STEP 6: FEATURE ENGINEERING")
    print("-"*80)
    
    merged_df = merged_df \
        .withColumn('total_nights', col('stays_in_weekend_nights') + col('stays_in_week_nights')) \
        .withColumn('total_revenue', col('avg_price_per_room') * 
                    (col('stays_in_weekend_nights') + col('stays_in_week_nights')))
    
    print(" Added derived features:")
    print("   • total_nights = stays_in_weekend_nights + stays_in_week_nights")
    print("   • total_revenue = avg_price_per_room × total_nights")
    
    # Convert booking_status to boolean for database-friendly format
    merged_df = merged_df \
        .withColumn('is_canceled', when(col('booking_status') == 'Canceled', True).otherwise(False)) \
        .drop('booking_status')
    
    print(" Converted booking_status to is_canceled (boolean: True/False)")
    
    return merged_df


def show_merge_summary(merged_df):
    """
    Display summary statistics and information about the merged dataset.
    
    Args:
        merged_df: Merged DataFrame
    """
    print("\n" + "-"*80)
    print("MERGED DATA SUMMARY")
    print("-"*80)
    
    print("\nMerged Schema:")
    merged_df.printSchema()
    
    print("\nSample of merged data:")
    merged_df.show(5, truncate=False)
    
    print("\nRecords by source:")
    merged_df.groupBy('data_source').count().show()
    
    print("\nCancellation distribution:")
    merged_df.groupBy('is_canceled').count().show()
    
    print("\nBasic statistics for key metrics:")
    merged_df.select('lead_time', 'total_nights', 'avg_price_per_room', 'total_revenue').describe().show()


def save_merged_dataset(merged_df):
    """
    Save the merged dataset to CSV file.
    
    Args:
        merged_df: Merged DataFrame
    """
    print("\n" + "-"*80)
    print("STEP 7: SAVING MERGED DATASET")
    print("-"*80)
    
    output_path = 'output/merged_hotel_data.csv'
    save_single_csv(merged_df, output_path)
    print(f" Saved: {output_path}")


def run_merge(customer_df, hotel_df):
    """
    Main merge workflow - orchestrates all merge steps.
    
    Args:
        customer_df: Raw customer reservations DataFrame
        hotel_df: Raw hotel bookings DataFrame
        
    Returns:
        Merged DataFrame with all transformations applied
    """
    print("\n" + "="*80)
    print("DATA MERGE AND INTEGRATION PROCESS")
    print("="*80)
    
    # Analyze column overlap
    analyze_column_overlap(customer_df, hotel_df)
    
    # Step 1: Clean customer data
    customer_clean = clean_customer_data(customer_df)
    
    # Step 2: Clean hotel data
    hotel_clean = clean_hotel_data(hotel_df)
    
    # Step 3: Save cleaned datasets
    save_cleaned_datasets(customer_clean, hotel_clean)
    
    # Step 4: Align schemas
    customer_aligned, hotel_aligned = align_schemas(customer_clean, hotel_clean)
    
    # Step 5: Merge datasets
    merged_df = merge_datasets(customer_aligned, hotel_aligned)
    
    # Step 6: Add derived features
    merged_df = add_derived_features(merged_df)
    
    # Show summary
    show_merge_summary(merged_df)
    
    # Step 7: Save merged dataset
    save_merged_dataset(merged_df)
    
    print("\n" + "="*80)
    print("MERGE PROCESS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\n📁 OUTPUT FILES CREATED:")
    print("   1. output/customer_reservations_cleaned.csv")
    print("   2. output/hotel_bookings_cleaned.csv")
    print("   3. output/merged_hotel_data.csv")
    
    return merged_df

