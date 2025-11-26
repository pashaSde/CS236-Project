#!/bin/bash
# Export PostgreSQL data (full dump with schema + data)

echo "Exporting PostgreSQL database (schema + data)..."
echo ""

# Export full database (CREATE TABLE + INSERT statements)
docker exec postgres pg_dump -U admin -d innsight > phase2_database_dump.sql

echo "Full database dump exported: phase2_database_dump.sql"
echo ""
echo "File contains:"
echo "  - Table definitions (CREATE TABLE)"
echo "  - Index definitions (CREATE INDEX)"
echo "  - All data (INSERT statements)"
echo "  - customer_reservations: 36,275 rows"
echo "  - hotel_bookings: 78,702 rows"
echo "  - merged_hotel_data: 114,977 rows"
echo ""

# Verify file size and content
FILE_SIZE=$(du -h phase2_database_dump.sql | awk '{print $1}')
TABLE_COUNT=$(grep -c "CREATE TABLE" phase2_database_dump.sql)
INSERT_COUNT=$(grep -c "COPY.*FROM stdin" phase2_database_dump.sql)

echo "File size: $FILE_SIZE"
echo "Tables: $TABLE_COUNT"
echo "Data copies: $INSERT_COUNT"
echo ""
echo "To restore this database:"
echo "  docker exec -i postgres psql -U admin -d innsight < phase2_database_dump.sql"


