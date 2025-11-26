# Hotel Booking Data Analysis Project

CS236 Fall 2025 - Big Data Analysis using PySpark

## Project Team

CS236 Graduate Students - Fall 2025
-   Pankaj Sharma - 862549035
-   Saransh Gupta - 862548920

## Project Overview

This project performs comprehensive exploratory data analysis (EDA) and data integration on hotel booking datasets. It combines customer reservation data with hotel booking data to create a unified dataset for analysis.

## Project Structure

```
CS236-Project/
├── data/                           # Raw input datasets
│   ├── customer-reservations.csv   # Customer reservation data
│   └── hotel-booking.csv           # Hotel booking data
├── output/                         # Generated outputs
│   ├── eda_*_correlation.png       # EDA correlation matrices
│   ├── customer_reservations_cleaned.csv
│   ├── hotel_bookings_cleaned.csv
│   └── merged_hotel_data.csv       # Final merged dataset
├── phase1.py                   # Main analysis script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── report.md                       # Complete project report with EDA and merge documentation
```

## Requirements

- Python 3.8+
- Apache Spark 3.x
- Java 11 or 17 (required for Spark)

### Python Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required packages:
- pyspark
- matplotlib
- seaborn
- pandas (for visualization only)

## Quick Start

### 1. Verify Data Files

Ensure the following files exist in the `data/` directory:
- `customer-reservations.csv`
- `hotel-booking.csv`

### 2. Run the Analysis Pipeline

Execute the analysis script:

```bash
python phase1.py
```

### 3. View Results

After execution, check the `output/` directory for:
- **EDA visualizations**: Correlation matrix heatmaps
- **Cleaned datasets**: Individual cleaned CSV files
- **Merged dataset**: Unified data file with all records

## What the Script Does

### Exploratory Data Analysis (EDA)

For each dataset (customer reservations and hotel bookings):

1. Data Loading with schema inference
2. Schema and dimension analysis
3. Missing value and distinct count checks
4. Descriptive statistics
5. Correlation matrix generation (saved as PNG)

### Data Merge and Integration

1. Column overlap analysis
2. Data cleaning and standardization
3. Schema alignment
4. Dataset union operation
5. Boolean conversion (is_canceled)
6. Data quality validation

### Outputs

- `customer_reservations_cleaned.csv`: Cleaned customer data
- `hotel_bookings_cleaned.csv`: Cleaned hotel data
- `merged_hotel_data.csv`: Unified dataset with 115,000+ records
- Correlation plots: EDA visualizations

## Key Features

### Data Cleaning & Standardization

- Unified column naming conventions
- Standardized booking status formats
- Converted text months to numeric values
- Generated unique booking IDs with INN prefix

### Changes in Merged Dataset

- `booking_id` renamed to `id`
- `booking_status` converted to `is_canceled` (boolean: True/False)

## Complete Project Report

For comprehensive documentation including EDA findings, data cleaning, processing, and merge decisions, see:
**[report.md](report.md)**

This complete report includes:
- Installation and setup instructions
- Dataset overview and characteristics
- Exploratory data analysis (EDA) with visualizations
- Schema alignment strategies
- Data type standardizations
- Handling of missing values
- Column mapping decisions
- Feature engineering rationale
- Final merged dataset specifications

## Output Specifications

### Cleaned Datasets

Both cleaned datasets contain 14 common columns:
- `booking_id`, `hotel`, `booking_status`, `lead_time`
- `arrival_year`, `arrival_month`, `arrival_date_week_number`, `arrival_date_day_of_month`
- `stays_in_weekend_nights`, `stays_in_week_nights`
- `market_segment_type`, `country`, `avg_price_per_room`, `email`

### Merged Dataset

The merged dataset includes 14 columns:
- `id`: Unique booking identifier (renamed from booking_id)
- `is_canceled` (boolean): Cancellation status (replaces booking_status text field)
- 12 other common columns from both datasets

## Troubleshooting

### Common Issues

1. **Java not found**
   - Install Java 11 or 17
   - Set `JAVA_HOME` environment variable

2. **Module not found errors**
   - Install dependencies: `pip install -r requirements.txt`

3. **Memory errors**
   - Increase Spark driver memory: Configure in `main.py`

4. **File permission errors**
   - Ensure write permissions in the `output/` directory

## License

Academic Use Only - UCR CS236 Course Project

---

For questions or issues, please contact the project team or course instructor.
