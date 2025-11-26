#!/bin/bash
# Export PostgreSQL DDL (schema only) for Phase 2 deliverable

echo "Exporting PostgreSQL DDL (schema only)..."
echo ""

# Check if Docker container is running
if ! docker ps | grep -q postgres; then
    echo "Error: PostgreSQL Docker container 'postgres' is not running"
    echo "   Start it with: docker start postgres"
    exit 1
fi

# Export using Docker exec (works without PostgreSQL client on host)
docker exec postgres pg_dump -U admin -d innsight --schema-only > phase2_ddl.sql

if [ $? -eq 0 ]; then
    echo "DDL file exported: phase2_ddl.sql"
    echo ""
    echo "File contains:"
    echo "  - Table definitions (customer_reservations, hotel_bookings, merged_hotel_data)"
    echo "  - Primary key constraints"
    echo "  - Index definitions"
    echo "  - No data (no INSERT statements)"
    echo ""
    
    # Show file info
    if [ -f phase2_ddl.sql ]; then
        FILE_SIZE=$(ls -lh phase2_ddl.sql | awk '{print $5}')
        echo "File size: $FILE_SIZE"
        
        # Count tables and indexes
        TABLE_COUNT=$(grep -c "CREATE TABLE" phase2_ddl.sql || echo "0")
        INDEX_COUNT=$(grep -c "CREATE INDEX" phase2_ddl.sql || echo "0")
        
        echo "Tables: $TABLE_COUNT"
        echo "Indexes: $INDEX_COUNT"
    fi
else
    echo "Error: Failed to export DDL"
    echo "   Check if database 'innsight' exists in the container"
fi
