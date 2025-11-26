# Load output/merged_hotel_data.csv for analysis using PySpark

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, sum,
    when, round as _round, desc
)
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import matplotlib.pyplot as plt
import pandas as pd
import os
from generate_report import generate_findings_report

# Month names for plotting
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def load_and_analyze_data(file_path="../output/merged_hotel_data.csv", output_dir="../output/phase-2"):
    
    # Create output directory structure if it doesn't exist
    plots_dir = os.path.join(output_dir, "plots")
    csvs_dir = os.path.join(output_dir, "csvs")
    report_dir = os.path.join(output_dir, "report")
    
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(csvs_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    # Initialize Spark session
    spark = SparkSession.builder.appName("HotelDataAnalysis").getOrCreate()
    
    # Load the CSV file
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    
    print("\nPrinting first 5 rows")
    df.show(5)
    
    # Perform analyses
    print("\nAnalysis on cancellation rates")
    cancellation_rates_df = cancellation_rate(df)
    cancellation_rates_df.show()
    save_cancellation_rates_plot(
        cancellation_rates_df,
        csvs_dir,
        plots_dir
    )
    
    print("\nAverages")
    averages_df = averages(df)
    averages_df.show()
    save_averages_plot(averages_df, csvs_dir, plots_dir)
    
    print("\nMonthly Bookings")
    monthly_bookings_df = monthly_bookings(df)
    monthly_bookings_df.show()
    save_bookings_plot(monthly_bookings_df, csvs_dir, plots_dir)
    
    print("\nSeasonality")
    seasonality_df = seasonality(df)
    seasonality_df.show()
    save_seasonality_plot(seasonality_df, csvs_dir, plots_dir)
    
    return df

def cancellation_rate(df):

    # Convert is_canceled to numeric (1 for true, 0 for false)
    cancellation_df = df.groupBy("arrival_month").agg(
        sum(when(col("is_canceled") == "true", 1).otherwise(0)).alias("canceled_count"),
        count("*").alias("total_bookings")
    )
    
    # Calculate cancellation rate as percentage
    cancellation_df = cancellation_df.withColumn(
        "cancellation_rate_percent",
        _round((col("canceled_count") / col("total_bookings")) * 100, 2)
    ).orderBy("arrival_month")
    
    return cancellation_df

def averages(df):
    # Calculate total nights stayed
    df_with_nights = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    )
    
    # Group by month and calculate averages
    averages_df = df_with_nights.groupBy("arrival_month").agg(
        _round(avg("avg_price_per_room"), 2).alias("avg_price_per_room"),
        _round(avg("total_nights"), 2).alias("avg_nights_stayed")
    ).orderBy("arrival_month")
    
    return averages_df

def monthly_bookings(df):

    # Group by arrival_month and market_segment_type
    bookings_df = df.groupBy("arrival_month", "market_segment_type").agg(
        count("*").alias("booking_count")
    ).orderBy("arrival_month", "market_segment_type")
    
    return bookings_df

def seasonality(df):
    # Calculate revenue for each booking
    df_with_revenue = df.withColumn(
        "total_nights",
        col("stays_in_weekend_nights") + col("stays_in_week_nights")
    ).withColumn(
        "revenue",
        col("avg_price_per_room") * col("total_nights")
    )
    
    # Group by month and sum revenue
    seasonality_df = df_with_revenue.groupBy("arrival_month").agg(
        sum("revenue").alias("total_revenue"),
        count("*").alias("total_bookings")
    ).withColumn(
        "total_revenue",
        _round(col("total_revenue"), 2)
    ).orderBy("arrival_month")
    
    return seasonality_df

def save_cancellation_rates_plot(df, csv_dir, plots_dir):
    # Convert to pandas
    pdf = df.toPandas()
    
    # Save to CSV
    csv_path = os.path.join(csv_dir, "cancellation_rates.csv")
    pdf.to_csv(csv_path, index=False)
    
    # Create plot
    plt.figure(figsize=(12, 6))
    plt.bar(pdf['arrival_month'], pdf['cancellation_rate_percent'], color='steelblue', edgecolor='black')
    plt.xlabel("Month", fontsize=12, fontweight='bold')
    plt.ylabel("Cancellation Rate (%)", fontsize=12, fontweight='bold')
    plt.title("Cancellation Rates by Month", fontsize=14, fontweight='bold')
    plt.xticks(range(1, 13), MONTH_NAMES)
    plt.grid(axis='y', alpha=0.3)
    
    # Save plot
    plot_path = os.path.join(plots_dir, "cancellation_rates.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def save_averages_plot(df, csv_dir, plots_dir):
    # Convert to pandas
    pdf = df.toPandas()
    
    # Save to CSV
    csv_path = os.path.join(csv_dir, "averages.csv")
    pdf.to_csv(csv_path, index=False)
    
    # Create plot with dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot average price
    color = 'tab:blue'
    ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Price per Room ($)', color=color, fontsize=12, fontweight='bold')
    ax1.plot(pdf['arrival_month'], pdf['avg_price_per_room'], 
             color=color, marker='o', linewidth=2, markersize=8, label='Avg Price')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(axis='y', alpha=0.3)
    
    # Create second y-axis for nights
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Average Nights Stayed', color=color, fontsize=12, fontweight='bold')
    ax2.plot(pdf['arrival_month'], pdf['avg_nights_stayed'], 
             color=color, marker='s', linewidth=2, markersize=8, label='Avg Nights')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Set x-axis labels
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(MONTH_NAMES)
    
    plt.title('Average Price and Nights Stayed by Month', fontsize=14, fontweight='bold')
    
    # Save plot
    plot_path = os.path.join(plots_dir, "averages.png")
    fig.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def save_bookings_plot(df, csv_dir, plots_dir):
    # Convert to pandas
    pdf = df.toPandas()
    
    # Save to CSV
    csv_path = os.path.join(csv_dir, "monthly_bookings.csv")
    pdf.to_csv(csv_path, index=False)
    
    # Pivot data for stacked bar chart
    pivot_df = pdf.pivot(index='arrival_month', 
                          columns='market_segment_type', 
                          values='booking_count').fillna(0)
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(14, 7))
    pivot_df.plot(kind='bar', stacked=True, ax=ax, colormap='tab10', edgecolor='black')
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Bookings', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Bookings by Market Segment', fontsize=14, fontweight='bold')
    ax.set_xticklabels(MONTH_NAMES, rotation=0)
    ax.legend(title='Market Segment', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    # Save plot
    plot_path = os.path.join(plots_dir, "monthly_bookings.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()


def save_seasonality_plot(df, csv_dir, plots_dir):
    # Convert to pandas
    pdf = df.toPandas().sort_values('arrival_month')
    
    # Save to CSV
    csv_path = os.path.join(csv_dir, "seasonality.csv")
    pdf.to_csv(csv_path, index=False)
    
    # Create plot
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Left axis: Revenue (Bar chart)
    ax1 = plt.gca()
    ax1.bar(pdf["arrival_month"], pdf["total_revenue"], color="steelblue", alpha=0.7, label="Total Revenue")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Total Revenue ($)")
    ax1.grid(axis="y", alpha=0.3)

    # Right axis: Bookings (Line chart)
    ax2 = ax1.twinx()
    ax2.plot(pdf["arrival_month"], pdf["total_bookings"], color="darkred", marker="o", label="Total Bookings")
    ax2.set_ylabel("Total Bookings", color="darkred")

    # Set x-axis month labels
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(MONTH_NAMES)

    plt.title("Seasonality: Revenue and Bookings by Month")

    # Combine both legends
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # Save the figure
    plot_path = os.path.join(plots_dir, "seasonality.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    # Load and analyze the data
    dataframe = load_and_analyze_data()