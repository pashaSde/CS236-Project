# How to Export DDL from PostgreSQL

## Quick Export (Recommended)

Run this command to export just the DDL (schema):

```bash
cd /Users/pasha/PycharmProjects/CS236-Project
export PGPASSWORD=secret123
bash export_sql.sh
```

This creates `phase2_ddl.sql` with CREATE TABLE and CREATE INDEX statements only (no data).

---

## Manual Export (Alternative Method)

If you prefer to run the command directly:

```bash
export PGPASSWORD=secret123
pg_dump -h localhost -p 5432 -U admin -d innsight --schema-only -f phase2_ddl.sql
unset PGPASSWORD
```

---

## What's Included in phase2_ddl.sql

**DDL (Data Definition Language) statements:**
- ✅ CREATE TABLE statements (3 tables)
- ✅ Column definitions with data types
- ✅ PRIMARY KEY constraints
- ✅ CREATE INDEX statements (performance indexes)
- ❌ No INSERT statements (no data)
- ❌ No SELECT queries

**Example output:**
```sql
CREATE TABLE customer_reservations (
    booking_id character varying NOT NULL,
    hotel character varying,
    is_canceled boolean NOT NULL,
    lead_time integer,
    arrival_year integer,
    arrival_month integer,
    arrival_date_week_number integer,
    arrival_date_day_of_month integer,
    stays_in_weekend_nights integer,
    stays_in_week_nights integer,
    market_segment_type character varying,
    country character varying,
    avg_price_per_room double precision,
    email character varying
);

ALTER TABLE ONLY customer_reservations
    ADD CONSTRAINT customer_reservations_pkey PRIMARY KEY (booking_id);

CREATE INDEX customer_reservations_idx_date ON customer_reservations USING btree (arrival_year, arrival_month);
CREATE INDEX customer_reservations_idx_price ON customer_reservations USING btree (avg_price_per_room);
CREATE INDEX customer_reservations_idx_segment ON customer_reservations USING btree (market_segment_type);
CREATE INDEX customer_reservations_idx_status ON customer_reservations USING btree (is_canceled);
```

---

## Expected File Size

| File | Approximate Size | Contains |
|------|------------------|----------|
| `phase2_ddl.sql` | ~5-10 KB | Table definitions, indexes, constraints only |

---

## Verify Export Success

```bash
# Check if file was created
ls -lh phase2_ddl.sql

# Preview the DDL file
head -30 phase2_ddl.sql

# Count tables (should be 3)
grep -c "CREATE TABLE" phase2_ddl.sql

# Count indexes (should be 12 total: 4 per table)
grep -c "CREATE INDEX" phase2_ddl.sql
```

---

## How to Restore Schema (If Needed)

To recreate the tables on another PostgreSQL instance:

```bash
psql -h localhost -p 5432 -U admin -d innsight < phase2_ddl.sql
```

**Note:** This only creates the tables and indexes, not the data.

---

## Troubleshooting

### Error: "pg_dump: command not found"

**Solution:** Install PostgreSQL client tools:
```bash
# macOS
brew install postgresql@14

# Add to PATH
export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"
```

### Error: "password authentication failed"

**Solution:** Check your password or use Docker exec:
```bash
docker exec -it postgres pg_dump -U admin -d innsight --schema-only > phase2_schema.sql
```

### Error: "database does not exist"

**Solution:** Verify database name:
```bash
docker exec -it postgres psql -U admin -c "\l"
```

---

## Phase 2 Deliverable Checklist

✅ **1. Report Documentation**
   - File: `report.md` (Phase 2 section added)
   - Contains: Schema design, decisions, transformations

✅ **2. Source Code**
   - File: `phase2/databaseLoader.py`
   - Well-commented with explanations

⏳ **3. DDL SQL File** (run export commands above)
   - `phase2_ddl.sql` — CREATE TABLE, CREATE INDEX (no data)

⏳ **4. Video Presentation**
   - 5-minute demo of your work
   - Show database schema, data loading, verification

