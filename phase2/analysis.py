"""
Phase 2: Hotel Data Analysis using PySpark
Analyzes merged hotel booking data and generates visualizations
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum, when, round as spark_round, desc
import matplotlib.pyplot as plt
import pandas as pd
import os

# Initialize Spark
spark = SparkSession.builder.appName("HotelDataAnalysis").getOrCreate()

# File paths
DATA_FILE = "../output/merged_hotel_data.csv"
OUTPUT_BASE = "output"
PLOTS_DIR = os.path.join(OUTPUT_BASE, "plots")
CSVS_DIR = os.path.join(OUTPUT_BASE, "csvs")
REPORT_DIR = os.path.join(OUTPUT_BASE, "report")

# Create output directories
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(CSVS_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def load_data():
    """Load the merged hotel data CSV"""
    print("Loading data from:", DATA_FILE)
    df = spark.read.csv(DATA_FILE, header=True, inferSchema=True)
    print(f"Loaded {df.count()} rows\n")
    df.show(5)
    return df


def analyze_cancellations(df):
    """Calculate cancellation rates by month"""
    print("\nAnalyzing Cancellation Rates")
    
    # Group by month and calculate cancellation rate
    result = df.groupBy("arrival_month").agg(
        sum(when(col("is_canceled") == "true", 1).otherwise(0)).alias("canceled_count"),
        count("*").alias("total_bookings")
    )
    
    # Calculate percentage
    result = result.withColumn(
        "cancellation_rate_percent",
        spark_round((col("canceled_count") / col("total_bookings")) * 100, 2)
    ).orderBy("arrival_month")
    
    result.show()
    
    # Save to CSV
    pdf = result.toPandas()
    pdf.to_csv(os.path.join(CSVS_DIR, "cancellation_rates.csv"), index=False)
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.bar(pdf['arrival_month'], pdf['cancellation_rate_percent'], color='steelblue', edgecolor='black')
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Cancellation Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Cancellation Rates by Month', fontsize=14, fontweight='bold')
    plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "cancellation_rates.png"), dpi=300)
    plt.close()
    
    print(f"✓ Saved: cancellation_rates.csv and plot")
    return result


def analyze_averages(df):
    """Calculate average price and nights stayed per month"""
    print("\nAnalyzing Averages")
    
    # Add total nights column
    df_nights = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    )
    
    # Group by month and calculate averages
    result = df_nights.groupBy("arrival_month").agg(
        spark_round(avg("avg_price_per_room"), 2).alias("avg_price_per_room"),
        spark_round(avg("total_nights"), 2).alias("avg_nights_stayed")
    ).orderBy("arrival_month")
    
    result.show()
    
    # Save to CSV
    pdf = result.toPandas()
    pdf.to_csv(os.path.join(CSVS_DIR, "averages.csv"), index=False)
    
    # Plot with dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Price line
    ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Price per Room ($)', color='tab:blue', fontsize=12, fontweight='bold')
    ax1.plot(pdf['arrival_month'], pdf['avg_price_per_room'], 
             color='tab:blue', marker='o', linewidth=2, markersize=8)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(axis='y', alpha=0.3)
    
    # Nights line on second axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Average Nights Stayed', color='tab:orange', fontsize=12, fontweight='bold')
    ax2.plot(pdf['arrival_month'], pdf['avg_nights_stayed'], 
             color='tab:orange', marker='s', linewidth=2, markersize=8)
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    plt.title('Average Price and Nights Stayed by Month', fontsize=14, fontweight='bold')
    fig.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "averages.png"), dpi=300)
    plt.close()
    
    print(f"✓ Saved: averages.csv and plot")
    return result


def analyze_bookings_by_segment(df):
    """Count bookings by month and market segment"""
    print("\nAnalyzing Monthly Bookings by Market Segment")
    
    # Group by month and segment
    result = df.groupBy("arrival_month", "market_segment_type").agg(
        count("*").alias("booking_count")
    ).orderBy("arrival_month", "market_segment_type")
    
    result.show()
    
    # Save to CSV
    pdf = result.toPandas()
    pdf.to_csv(os.path.join(CSVS_DIR, "monthly_bookings.csv"), index=False)
    
    # Create stacked bar chart
    pivot_df = pdf.pivot(index='arrival_month', 
                          columns='market_segment_type', 
                          values='booking_count').fillna(0)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    pivot_df.plot(kind='bar', stacked=True, ax=ax, colormap='tab10', edgecolor='black')
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Bookings', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Bookings by Market Segment', fontsize=14, fontweight='bold')
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=0)
    ax.legend(title='Market Segment', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "monthly_bookings.png"), dpi=300)
    plt.close()
    
    print(f"✓ Saved: monthly_bookings.csv and plot")
    return result


def analyze_seasonality(df):
    """Identify revenue patterns by month"""
    print("\nAnalyzing Seasonality (Revenue by Month)")
    
    # Calculate revenue per booking
    df_revenue = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    ).withColumn(
        "revenue",
        col("avg_price_per_room") * col("total_nights")
    )
    
    # Group by month
    result = df_revenue.groupBy("arrival_month").agg(
        sum("revenue").alias("total_revenue"),
        count("*").alias("total_bookings")
    ).withColumn(
        "total_revenue",
        spark_round(col("total_revenue"), 2)
    ).orderBy(desc("total_revenue"))
    
    result.show()
    
    # Save to CSV
    pdf = result.toPandas().sort_values('arrival_month')
    pdf.to_csv(os.path.join(CSVS_DIR, "seasonality.csv"), index=False)
    
    # Plot revenue and bookings
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Revenue bars
    ax1.bar(pdf['arrival_month'], pdf['total_revenue'], 
            color='steelblue', edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Revenue ($)', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Bookings line on second axis
    ax2 = ax1.twinx()
    ax2.plot(pdf['arrival_month'], pdf['total_bookings'], 
             color='darkred', marker='o', linewidth=2, markersize=8)
    ax2.set_ylabel('Total Bookings', color='darkred', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='darkred')
    
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    plt.title('Seasonality: Revenue and Bookings by Month', fontsize=14, fontweight='bold')
    fig.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "seasonality.png"), dpi=300)
    plt.close()
    
    print(f"✓ Saved: seasonality.csv and plot")
    return result


def main():
    """Run all analyses"""
    print("HOTEL BOOKING DATA ANALYSIS")

    # Load data
    df = load_data()
    
    # Run all analyses
    analyze_cancellations(df)
    analyze_averages(df)
    analyze_bookings_by_segment(df)
    analyze_seasonality(df)
    
    # Summary
    print("ANALYSIS COMPLETE")
    print(f"Results saved to:")
    print(f"  - CSV files: {CSVS_DIR}/")
    print(f"  - Plots: {PLOTS_DIR}/")
    print(f"\nTo generate findings report, run:")
    print(f"  python generate_report.py --output-dir {OUTPUT_BASE}")
    print()


if __name__ == "__main__":
    main()