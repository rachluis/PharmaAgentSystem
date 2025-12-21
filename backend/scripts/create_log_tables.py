import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, inspect
from app.models import Base
from app.config import get_settings

settings = get_settings()

def create_tables():
    print(f"Connecting to database: {settings.database_url}")
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    
    # Check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Existing tables: {existing_tables}")
    
    # Create new tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    # Verify new tables
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print(f"Tables after creation: {new_tables}")
    
    if "sys_login_logs" in new_tables and "sys_op_logs" in new_tables:
        print("SUCCESS: sys_login_logs and sys_op_logs created.")
    else:
        print("ERROR: Failed to create new log tables.")

if __name__ == "__main__":
    create_tables()
