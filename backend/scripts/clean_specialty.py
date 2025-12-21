import sqlite3
import os
import sys

def clean_specialties():
    # Use absolute path to ensure we hit the right DB
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "pharma.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current state (sample)
        cursor.execute("SELECT specialty FROM doctors WHERE specialty LIKE '%|%' LIMIT 5")
        sample_before = cursor.fetchall()
        print("Sample before cleaning:", sample_before)

        # Count rows to be affected
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE specialty LIKE '%|%'")
        count = cursor.fetchone()[0]
        print(f"Found {count} rows to update.")

        if count > 0:
            # Perform Update
            # Logic: substr(specialty, instr(specialty, '|') + 1)
            # This takes everything AFTER the first '|'
            sql = """
                UPDATE doctors 
                SET specialty = substr(specialty, instr(specialty, '|') + 1) 
                WHERE instr(specialty, '|') > 0
            """
            cursor.execute(sql)
            conn.commit()
            print(f"Successfully updated {cursor.rowcount} rows.")

            # Verify
            cursor.execute("SELECT specialty FROM doctors LIMIT 5")
            sample_after = cursor.fetchall()
            print("Sample after cleaning:", sample_after)
        else:
            print("No rows required cleaning.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_specialties()
