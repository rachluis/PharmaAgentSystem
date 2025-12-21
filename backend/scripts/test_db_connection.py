"""
Test database connection and simple query.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os

DATABASE_URL = "sqlite:///./pharma.db"

print(f"Testing connection to: {DATABASE_URL}")
print(f"Current working directory: {os.getcwd()}")
print(f"Database file exists: {os.path.exists('pharma.db')}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✓ Connection successful!")
        
        # Try to query users table
        print("\nQuerying users table...")
        try:
            result = connection.execute(text("SELECT username, is_active FROM users LIMIT 5"))
            users = result.fetchall()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - {user}")
        except OperationalError as e:
            print(f"✗ Error querying users: {e}")
            
except Exception as e:
    print(f"✗ Connection failed: {e}")
