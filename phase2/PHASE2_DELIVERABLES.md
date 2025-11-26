# Phase 2 Deliverables — Complete Checklist

## 📦 What You Need to Submit

### ✅ 1. Report Documentation
**File:** `report.md`  
**Status:** ✅ COMPLETE  
**Location:** `/Users/pasha/PycharmProjects/CS236-Project/report.md`

**Contents:**
- Phase 1: Data Preparation & EDA
- Phase 2: Database Design & Population
  - Schema design decisions
  - Data type transformations
  - PySpark implementation
  - Performance optimization (indexes)
  - Error handling
  - Execution steps

---

### ✅ 2. Well-Documented Source Code
**File:** `databaseLoader.py`  
**Status:** ✅ COMPLETE  
**Location:** `/Users/pasha/PycharmProjects/CS236-Project/phase2/databaseLoader.py`

**Features:**
- Comprehensive comments explaining each function
- Environment variable support for credentials
- Error handling and data validation
- Boolean conversion logic documented
- Index creation with rationale

**How to run:**
```bash
cd /Users/pasha/PycharmProjects/CS236-Project/phase2
export POSTGRES_PWD=secret123
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
```

---

### ⏳ 3. DDL SQL File from PostgreSQL
**File:** `phase2_ddl.sql`  
**Status:** ⏳ READY TO EXPORT  
**Instructions:** See below

#### Quick Export:
```bash
cd /Users/pasha/PycharmProjects/CS236-Project
export PGPASSWORD=secret123
bash export_sql.sh
unset PGPASSWORD
```

Or manually:
```bash
export PGPASSWORD=secret123
pg_dump -h localhost -p 5432 -U admin -d innsight --schema-only -f phase2_ddl.sql
unset PGPASSWORD
```

**Expected File:**
- `phase2_ddl.sql` (~5-10 KB) — CREATE TABLE, CREATE INDEX, constraints (no data)

**What's inside:**
- 3 CREATE TABLE statements (customer_reservations, hotel_bookings, merged_hotel_data)
- 3 PRIMARY KEY constraints
- 12 CREATE INDEX statements (4 indexes per table)
- Column definitions with data types (VARCHAR, INTEGER, BOOLEAN, DOUBLE PRECISION)

**Detailed Instructions:** See `phase2/EXPORT_SQL.md`

---

### ⏳ 4. Video Presentation (5 minutes)
**Status:** ⏳ TODO (You need to create this)

**Suggested Structure:**

**Minute 1: Introduction (0:00-1:00)**
- Brief project overview
- Show the three datasets (customer reservations, hotel bookings, merged)
- Mention total record count (114,977 rows)

**Minute 2: Schema Design (1:00-2:00)**
- Open `phase2_schema.sql` or show database schema
- Explain unified 14-column schema
- Highlight key decisions:
  - Boolean type for `is_canceled`
  - VARCHAR for `booking_id` (with INN prefix)
  - Nullable fields (hotel, country, email)

**Minute 3: Data Loading Process (2:00-3:00)**
- Open `databaseLoader.py` in IDE
- Show key functions:
  - `normalize_booking_status()` — Boolean conversion
  - `create_indexes()` — Performance optimization
  - `load_table()` — JDBC write
- Mention PySpark + PostgreSQL JDBC connection

**Minute 4: Demo Execution (3:00-4:00)**
- Run the loader script:
  ```bash
  spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
  ```
- Show output:
  - "36,275 rows loaded" for customer_reservations
  - "78,702 rows loaded" for hotel_bookings
  - "114,977 rows loaded" for merged_hotel_data
  - Indexes created

**Minute 5: Verification (4:00-5:00)**
- Connect to PostgreSQL:
  ```bash
  docker exec -it postgres psql -U admin -d innsight
  ```
- Run verification queries:
  ```sql
  \dt  -- Show tables
  \d customer_reservations  -- Show schema
  SELECT COUNT(*) FROM customer_reservations;
  SELECT is_canceled, COUNT(*) FROM merged_hotel_data GROUP BY is_canceled;
  ```
- Show indexes:
  ```sql
  \di  -- List indexes
  ```
- Wrap up with key achievements

**Recording Tips:**
- Use screen recording tool (QuickTime, OBS, Zoom)
- Show terminal + IDE side-by-side
- Speak clearly and explain each step
- Practice once before final recording
- Keep it under 5 minutes (aim for 4:30)

---

## 🚀 Pre-Submission Checklist

### Step 1: Verify Database is Loaded
```bash
docker exec -it postgres psql -U admin -d innsight -c "\dt"
```
Expected output: 3 tables (customer_reservations, hotel_bookings, merged_hotel_data)

### Step 2: Export DDL File
```bash
cd /Users/pasha/PycharmProjects/CS236-Project
export PGPASSWORD=secret123
bash export_sql.sh
unset PGPASSWORD
```

### Step 3: Verify Files Exist
```bash
ls -lh phase2_ddl.sql report.md phase2/databaseLoader.py
```

Expected output:
```
-rw-r--r--  phase2_ddl.sql (~5-10 KB)
-rw-r--r--  report.md (~50+ KB)
-rw-r--r--  phase2/databaseLoader.py (~8+ KB)
```

### Step 4: Create Video (5 minutes)
Follow structure above, record, and save as `phase2_demo.mp4`

### Step 5: Package for Submission
```bash
zip -r Phase2_Submission.zip \
  report.md \
  phase2/databaseLoader.py \
  phase2_ddl.sql \
  phase2_demo.mp4
```

---

## 📊 What Your Report Contains

Your `report.md` now includes:

### Phase 1 (Existing)
- Installation process
- Exploratory Data Analysis
- Data merge & integration

### Phase 2 (NEW — Just Added)
1. **Database Setup** — Docker, database hierarchy
2. **Schema Design** — Unified schema, design decisions
3. **Data Type Transformations** — Boolean conversion, column standardization
4. **PySpark Implementation** — Architecture, components, JDBC
5. **Performance Optimization** — Indexes, table statistics
6. **Data Validation** — Row counts, integrity checks
7. **Error Handling** — Type mismatch resolution, security
8. **Execution Steps** — Prerequisites, running the loader
9. **Deliverables Summary** — Checklist of what was completed
10. **Key Achievements** — Major accomplishments

**Total:** ~480 lines added to report.md

---

## 🎯 Quick Commands Summary

```bash
# 1. Run the database loader
cd /Users/pasha/PycharmProjects/CS236-Project/phase2
export POSTGRES_PWD=secret123
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py

# 2. Export DDL file
cd /Users/pasha/PycharmProjects/CS236-Project
export PGPASSWORD=secret123
bash export_sql.sh
unset PGPASSWORD

# 3. Verify everything
ls -lh phase2_ddl.sql report.md phase2/databaseLoader.py

# 4. Connect to database (for demo)
docker exec -it postgres psql -U admin -d innsight
```

---

## 📝 Submission Checklist

- [ ] `report.md` — Complete documentation (Phase 1 + Phase 2)
- [ ] `phase2/databaseLoader.py` — Well-commented source code
- [ ] `phase2_ddl.sql` — Database DDL (CREATE TABLE, CREATE INDEX)
- [ ] `phase2_demo.mp4` — 5-minute video presentation
- [ ] Everything zipped in `Phase2_Submission.zip`

---

## 🆘 Need Help?

**Export SQL files not working?**
- See detailed instructions in `phase2/EXPORT_SQL.md`

**Video recording tips?**
- Use QuickTime (macOS): File → New Screen Recording
- Use OBS Studio (free, cross-platform)
- Use Zoom: Share screen → Record

**Report formatting?**
- Your `report.md` follows same style as Phase 1
- Uses markdown tables, code blocks, and clear sections
- Includes "Why?" explanations for all decisions

---

Good luck with your submission! 🎉

