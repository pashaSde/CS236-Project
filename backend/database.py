from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_HOST = os.getenv("DB_HOST", "database-1.cgd0sswa4bi6.us-east-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"options": f"-csearch_path={DB_SCHEMA}"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database session dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Tests database connectivity by executing a simple query."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False


def get_available_tables():
    """Returns list of available table names in the public schema."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            return [row[0] for row in result]
    except Exception as e:
        print(f"Error getting tables: {str(e)}")
        return []


def get_table_info(table_name: str):
    """Returns column metadata (name, type, nullable) for a given table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """))
            return [
                {
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2] == "YES"
                }
                for row in result
            ]
    except Exception as e:
        print(f"Error getting table info: {str(e)}")
        return []


if __name__ == "__main__":
    test_connection()
    tables = get_available_tables()
    for table in tables:
        print(f"{table}")
        for col in get_table_info(table):
            print(f"  {col['name']} ({col['type']})")

