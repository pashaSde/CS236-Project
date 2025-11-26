# Phase 2 Video Script - Database Loader (2.5 minutes)

## 🎬 Timing Breakdown
- **0:00-0:20** (20s) - Introduction & Database Setup
- **0:20-0:50** (30s) - Schema Design
- **0:50-1:30** (40s) - Code Walkthrough
- **1:30-2:10** (40s) - Execution Demo
- **2:10-2:30** (20s) - Verification & Wrap-up

---

## 📝 SCRIPT

### **[0:00-0:20] INTRODUCTION & DATABASE SETUP (20 seconds)**

**[Screen: Show Docker command in terminal]**

> "Hello, I'm presenting Phase 2 of our hotel booking database project. We're loading three datasets into PostgreSQL using PySpark."

**[Type/show command]:**
```bash
docker run -d --name postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_DB=innsight \
  -p 5432:5432 postgres:latest
```

> "First, we set up PostgreSQL using Docker. This creates the 'innsight' database running on port 5432."

---

### **[0:20-0:50] SCHEMA DESIGN (30 seconds)**

**[Screen: Open phase2_ddl.sql or show schema table in report]**

> "Our schema design uses a unified 14-column structure for all three tables: customer reservations, hotel bookings, and merged data."

**[Highlight key columns on screen]:**

> "Key design decisions: We use VARCHAR for booking_id to preserve the INN prefix, BOOLEAN for is_canceled for efficiency, and nullable fields like hotel and country since not all datasets have these."

**[Show index section briefly]:**

> "We created indexes on frequently queried columns: price, cancellation status, dates, and market segments for 3 to 6x faster filtering."

---

### **[0:50-1:30] CODE WALKTHROUGH (40 seconds)**

**[Screen: Open databaseLoader.py in IDE, scroll to key functions]**

> "Let's look at the PySpark implementation. The script has several key functions:"

**[Show/highlight `normalize_booking_status` function - 10 seconds]:**

> "The normalize_booking_status function handles inconsistent data. Customer reservations use 'Canceled' and 'Not_Canceled', while hotel bookings use 'true' and 'false'. We convert all variations to proper boolean values."

**[Scroll to `load_table` function - 10 seconds]:**

> "The load_table function reads CSVs, applies transformations, and writes to PostgreSQL via JDBC. Mode overwrite allows us to re-run the script safely."

**[Scroll to `create_indexes` function - 10 seconds]:**

> "Finally, create_indexes adds performance indexes on four columns per table and runs ANALYZE to update table statistics."

---

### **[1:30-2:10] EXECUTION DEMO (40 seconds)**

**[Screen: Terminal, ready to run command]**

> "Now let's run the loader. First, I set the database password environment variable, then execute with spark-submit."

**[Type and run]:**
```bash
export POSTGRES_PWD=secret123
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py
```

**[Let it run, highlight key output lines as they appear]:**

> "The script loads each dataset... customer reservations, 36,275 rows... hotel bookings, 78,702 rows... merged data, 114,977 rows. Now creating indexes... done!"

**[Point to output]:**

> "All three tables loaded successfully with indexes created."

---

### **[2:10-2:30] VERIFICATION & WRAP-UP (20 seconds)**

**[Screen: Terminal, connect to database]**

**[Type and show]:**
```bash
docker exec -it postgres psql -U admin -d innsight
```

**[In psql]:**
```sql
\dt
SELECT COUNT(*) FROM customer_reservations;
\di
```

**[Show results briefly]:**

> "Verification shows three tables with correct row counts and 12 indexes created. Our database is now populated and optimized, ready for Phase 3 analysis and the WebUI."

> "Thank you!"

---

## 📌 TIPS FOR RECORDING

### Before Recording:
1. ✅ Run `databaseLoader.py` once to ensure it works
2. ✅ Close unnecessary windows/tabs
3. ✅ Increase terminal font size (16-18pt)
4. ✅ Have all files open in tabs: `databaseLoader.py`, `phase2_ddl.sql`, terminal
5. ✅ Clear terminal history: `clear`
6. ✅ Practice the script 2-3 times with a timer

### During Recording:
- **Speak clearly and at moderate pace**
- **Use mouse cursor to highlight what you're talking about**
- **Don't rush through output - let viewers see key numbers**
- **If you make a mistake, pause, take a breath, and continue** (you can edit later)

### Screen Layout Suggestion:
```
┌─────────────────┬─────────────────┐
│                 │                 │
│   IDE/Code      │   Terminal      │
│   (left)        │   (right)       │
│                 │                 │
└─────────────────┴─────────────────┘
```

Or use full screen and switch between views.

---

## ⏱️ PRACTICE CHECKLIST

Read through script with timer:
- [ ] First read: Check for natural flow
- [ ] Second read: Time each section
- [ ] Third read: Practice with actual screen recording
- [ ] Adjust pace if over/under 2:30

---

## 🎥 RECORDING TOOLS

**macOS:**
- QuickTime Player: File → New Screen Recording
- Built-in: Cmd+Shift+5 → Record Entire Screen

**Cross-platform:**
- OBS Studio (free)
- Zoom: Share Screen + Record

---

## 📋 QUICK COMMAND REFERENCE

```bash
# 1. Start Docker (if not running)
docker start postgres

# 2. Set password
export POSTGRES_PWD=secret123

# 3. Run loader
cd /Users/pasha/PycharmProjects/CS236-Project/phase2
spark-submit --packages org.postgresql:postgresql:42.7.3 databaseLoader.py

# 4. Verify
docker exec -it postgres psql -U admin -d innsight
\dt
SELECT COUNT(*) FROM customer_reservations;
SELECT COUNT(*) FROM hotel_bookings;
SELECT COUNT(*) FROM merged_hotel_data;
\di
\q
```

Good luck with your recording! 🎬



