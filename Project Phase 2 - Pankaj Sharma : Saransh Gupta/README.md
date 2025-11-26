# Project Phase 2 - Deliverables

**Authors:** Pankaj Sharma & Saransh Gupta  
**Course:** CS236 - Database Management System

## Folder Structure

```
Project Phase 2 - Pankaj Sharma : Saransh Gupta/
│
├── code/
│   ├── analysis.py              # Spark analysis script
│   ├── databaseLoader.py        # Database loader script
│   └── README.md                # How to run instructions
│
├── output/
│   ├── csvs/
│   │   ├── averages.csv         # Average price and stay duration analysis
│   │   ├── cancellation_rates.csv # Monthly cancellation rate data
│   │   ├── monthly_bookings.csv  # Monthly booking counts by market segment
│   │   └── seasonality.csv       # Revenue and booking seasonality analysis
│   │
│   ├── plots/
│   │   ├── averages.png         # Visualization of average metrics
│   │   ├── cancellation_rates.png # Cancellation rate trends
│   │   ├── monthly_bookings.png  # Monthly booking patterns
│   │   └── seasonality.png       # Seasonality analysis charts
│   │
│   ├── report/
│   │   └── analysis_findings.pdf # Analysis report with plots
│   │
│   └── sql/
│       ├── phase2_database_dump.sql # Full database dump (schema + data)
│       └── phase2_ddl.sql        # DDL only (schema)
│
├── Phase 2 Report.pdf            # Main project report
└── Phase2.mp4                   # Video presentation
```

## Contents Overview

### Code Directory
Contains the main implementation scripts:
- **analysis.py**: PySpark script for data analysis and generating insights
- **databaseLoader.py**: Script to load processed data into PostgreSQL database
- **README.md**: Detailed instructions on how to run the scripts

### Output Directory
Contains all generated outputs organized by type:

#### CSV Files (`output/csvs/`)
- Processed analysis results in CSV format for further analysis
- Includes averages, cancellation rates, monthly bookings, and seasonality data

#### Plots (`output/plots/`)
- Visualizations generated from the analysis
- PNG format images showing trends and patterns

#### Report (`output/report/`)
- Comprehensive analysis findings document with embedded plots
- PDF format for easy viewing and sharing

#### SQL Files (`output/sql/`)
- **phase2_database_dump.sql**: Complete database backup including schema and data
- **phase2_ddl.sql**: Schema definition only (CREATE TABLE statements, indexes, constraints)

### Root Files
- **Phase 2 Report.pdf**: Main project documentation covering methodology, implementation, and results
- **Phase2.mp4**: Video presentation demonstrating the project

## Quick Start

1. Review the main report: `Phase 2 Report.pdf`
2. Check code instructions: `code/README.md`
3. View analysis results: `output/report/analysis_findings.pdf`
4. Watch video presentation: `Phase2.mp4`

## Database Setup

To restore the database:
```bash
# Full restore (schema + data)
psql -U postgres -d your_database < output/sql/phase2_database_dump.sql

# Schema only
psql -U postgres -d your_database < output/sql/phase2_ddl.sql
```


