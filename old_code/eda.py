"""
Exploratory Data Analysis (EDA) Module
Performs comprehensive analysis on hotel booking and customer reservation datasets.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import matplotlib.pyplot as plt
import seaborn as sns


def load_datasets(spark):
    """
    Load customer reservations and hotel bookings datasets.
    
    Args:
        spark: Active SparkSession
        
    Returns:
        tuple: (customer_df, hotel_df)
    """
    print("\n" + "="*80)
    print("LOADING DATASETS")
    print("="*80)
    
    customer_df = spark.read.csv("data/customer-reservations.csv", header=True, inferSchema=True)
    print(" Loaded customer reservations")
    
    hotel_df = spark.read.csv("data/hotel-booking.csv", header=True, inferSchema=True)
    print(" Loaded hotel bookings")
    
    return customer_df, hotel_df


def analyze_schema(df, dataset_name):
    """
    Analyze and display schema information for a dataset.
    
    Args:
        df: Spark DataFrame
        dataset_name: Name of the dataset for display
    """
    print("\n" + "-"*80)
    print(f"SCHEMA ANALYSIS: {dataset_name}")
    print("-"*80)
    
    print("\nSchema:")
    df.printSchema()
    
    print(f"\nDataset dimensions:")
    print(f"  • Rows: {df.count():,}")
    print(f"  • Columns: {len(df.columns)}")
    
    print(f"\nColumn names:")
    print(f"  {df.columns}")


def analyze_data_quality(df):
    """
    Analyze data quality: missing values, distinct counts.
    
    Args:
        df: Spark DataFrame
    """
    print("\n" + "-"*40)
    print("DATA QUALITY ANALYSIS")
    print("-"*40)
    
    print("\nMissing Values Count:")
    missing_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns])
    missing_counts.show()
    
    print("\nDistinct Values Count:")
    distinct_counts = df.agg(*[countDistinct(c).alias(c) for c in df.columns])
    distinct_counts.show()


def analyze_statistics(df):
    """
    Display descriptive statistics for the dataset.
    
    Args:
        df: Spark DataFrame
    """
    print("\n" + "-"*40)
    print("DESCRIPTIVE STATISTICS")
    print("-"*40)
    
    print("\nSample Data (first 5 rows):")
    df.show(5)
    
    print("\nSummary Statistics:")
    df.describe().show()


def generate_correlation_matrix(df, dataset_name):
    """
    Generate and save correlation matrix heatmap for numeric columns.
    
    Args:
        df: Spark DataFrame
        dataset_name: Name for the output file
    """
    numeric_cols = [f.name for f in df.schema.fields 
                   if isinstance(f.dataType, (IntegerType, DoubleType, FloatType, LongType))]
    
    if len(numeric_cols) > 1:
        print(f"\nGenerating correlation matrix for {len(numeric_cols)} numeric columns...")
        pdf = df.select(numeric_cols).toPandas()
        corr = pdf.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', 
                   square=True, linewidths=0.5)
        plt.title(f'Correlation Matrix - {dataset_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_file = f'output/eda_{dataset_name}_correlation.png'
        plt.savefig(output_file, dpi=150)
        plt.close()
        print(f" Correlation matrix saved to: {output_file}")


def perform_eda(df, dataset_name):
    """
    Perform complete exploratory data analysis on a dataset.
    
    Args:
        df: Spark DataFrame
        dataset_name: Name of the dataset for display and file naming
    """
    print("\n" + "="*80)
    print(f"EXPLORATORY DATA ANALYSIS: {dataset_name.upper()}")
    print("="*80)
    
    # Schema analysis
    analyze_schema(df, dataset_name)
    
    # Data quality
    analyze_data_quality(df)
    
    # Statistics
    analyze_statistics(df)
    
    # Correlation matrix
    generate_correlation_matrix(df, dataset_name)
    
    print(f"\n EDA completed for {dataset_name}")


def run_eda(spark):
    """
    Main EDA workflow - loads data and performs analysis on both datasets.
    
    Args:
        spark: Active SparkSession
        
    Returns:
        tuple: (customer_df, hotel_df)
    """
    # Load datasets
    customer_df, hotel_df = load_datasets(spark)
    
    # Perform EDA on customer reservations
    perform_eda(customer_df, "customer_reservations")
    
    # Perform EDA on hotel bookings
    perform_eda(hotel_df, "hotel_bookings")
    
    # Return the loaded DataFrames for further processing
    return customer_df, hotel_df

