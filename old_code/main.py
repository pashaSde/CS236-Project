#!/usr/bin/env python3
"""
Hotel Booking Data Analysis Pipeline
Main entry point for EDA and data merging workflow.

This script orchestrates:
1. Exploratory Data Analysis (EDA) on raw datasets
2. Data cleaning, transformation, and merging

Usage:
    python main.py
"""

import sys
from pyspark.sql import SparkSession
from datetime import datetime

# Import custom modules
import eda
import merge


def create_spark_session():
    """
    Create and configure Spark session.
    
    Returns:
        SparkSession: Configured Spark session
    """
    spark = SparkSession.builder \
        .appName("HotelBookingAnalysis") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    return spark


def main():
    """
    Main execution function.
    Runs EDA followed by data merge operations.
    """
    print("\n" + "="*80)
    print("HOTEL BOOKING DATA ANALYSIS PIPELINE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Phase 1: Exploratory Data Analysis
        print("\n" + "="*80)
        print("PHASE 1: EXPLORATORY DATA ANALYSIS")
        print("="*80)
        
        customer_df, hotel_df = eda.run_eda(spark)
        
        # Phase 2: Data Integration and Merging
        print("\n" + "="*80)
        print("PHASE 2: DATA INTEGRATION AND MERGING")
        print("="*80)
        
        merged_df = merge.run_merge(customer_df, hotel_df)
        
        # Final summary
        print("\n" + "="*80)
        print("PIPELINE EXECUTION COMPLETED")
        print("="*80)
        print(f"\nTotal records in merged dataset: {merged_df.count():,}")
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nGenerated outputs:")
        print("   • EDA correlation plots: output/eda_*_correlation.png")
        print("   • Cleaned datasets: output/*_cleaned.csv")
        print("   • Merged dataset: output/merged_hotel_data.csv")
        print("\nFor details on merge decisions, see: DATA_MERGE_DECISIONS.md")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up Spark session
        spark.stop()
        print("\n Spark session stopped.")


if __name__ == "__main__":
    main()

