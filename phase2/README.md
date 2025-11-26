# Phase 2: Spark Analysis & Database Population

**Course:** CS236 — Database Management System  
**Authors:** Pankaj Sharma (862549035), Saransh Gupta (862548920)

---

## How to Run

### Step 1: Run Analysis

```bash
cd phase2
spark-submit analysis.py
```

This will:
- Analyze the CSV files in `output/` directory
- Generate visualizations in `output/plots/`
- Save analysis results as CSV files

---

### Step 2: Start PostgreSQL Database

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=******** \
  -e POSTGRES_DB=innsight \
  -p 5432:5432 \
  postgres:latest
```

---

### Step 3: Load Data into Database

```bash
cd phase2
export POSTGRES_PWD=********
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
```

This will:
- Load 3 CSV files into PostgreSQL
- Create 3 tables with 114,977 total records
- Create indexes for query performance

---