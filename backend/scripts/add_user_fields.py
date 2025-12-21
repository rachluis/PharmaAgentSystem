"""
Migration script to add phone and bio fields to users table.
Run this script from the backend directory: python -m scripts.add_user_fields
"""
import sqlite3
import os

def add_user_fields():
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', 'pharma.db')
    db_path = os.path.abspath(db_path)
    
    print(f"Connecting to database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add phone column if it doesn't exist
        if 'phone' not in columns:
            print("Adding 'phone' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
            print("✓ 'phone' column added")
        else:
            print("'phone' column already exists")
        
        # Add bio column if it doesn't exist
        if 'bio' not in columns:
            print("Adding 'bio' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            print("✓ 'bio' column added")
        else:
            print("'bio' column already exists")
        
        conn.commit()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_user_fields()
