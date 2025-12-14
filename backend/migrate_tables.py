"""
Database migration script for Phase 2 backend enhancements.

This script safely adds new columns to existing tables and creates new tables
while preserving all existing data (738,772 doctor records).

Usage:
    python migrate_tables.py

IMPORTANT: This script uses ALTER TABLE commands to modify existing tables
without data loss. Backup pharma.db before running!
"""
import sqlite3
from pathlib import Path
import json
from datetime import datetime


def main():
    # Connect to database
    db_path = Path(__file__).parent / "pharma.db"
    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        return
    
    print(f"📁 Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ===== Step 1: Add columns to doctors table =====
        print("\n🔧 Step 1: Extending doctors table...")
        
        doctor_columns = [
            ("full_name", "VARCHAR(200)"),
            ("city", "VARCHAR(100)"),
            ("total_payments", "INTEGER DEFAULT 0"),
            ("avg_payment_amount", "FLOAT DEFAULT 0.0"),
            ("last_payment_date", "DATE"),
            ("cluster_label", "VARCHAR(50)"),
        ]
        
        for col_name, col_type in doctor_columns:
            try:
                cursor.execute(f"ALTER TABLE doctors ADD COLUMN {col_name} {col_type}")
                print(f"   ✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⏭️  Column already exists: {col_name}")
                else:
                    raise
        
        # Update full_name from first_name + last_name
        print("   🔄 Computing full_name values...")
        cursor.execute("""
            UPDATE doctors 
            SET full_name = COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')
            WHERE full_name IS NULL
        """)
        updated = cursor.rowcount
        print(f"   ✅ Updated {updated:,} full_name values")
        
        conn.commit()
        
        # ===== Step 2: Add columns to cluster_results table =====
        print("\n🔧 Step 2: Extending cluster_results table...")
        
        cluster_columns = [
            ("task_id", "INTEGER"),
            ("algorithm", "VARCHAR(50) DEFAULT 'k-means'"),
            ("features_used", "TEXT"),
            ("cluster_labels", "TEXT"),
            ("silhouette_score", "FLOAT"),
            ("inertia", "FLOAT"),
            ("visualization_data", "TEXT"),
            ("is_active", "BOOLEAN DEFAULT 1"),
        ]
        
        for col_name, col_type in cluster_columns:
            try:
                cursor.execute(f"ALTER TABLE cluster_results ADD COLUMN {col_name} {col_type}")
                print(f"   ✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   ⏭️  Column already exists: {col_name}")
                else:
                    raise
        
        conn.commit()
        
        # ===== Step 3: Create new tables =====
        print("\n🔧 Step 3: Creating new tables...")
        
        # AnalysisTask table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name VARCHAR(200) NOT NULL,
                task_type VARCHAR(50) NOT NULL,
                parameters TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                error_message TEXT,
                created_by INTEGER,
                started_at DATETIME,
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                result_id INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (result_id) REFERENCES cluster_results(cluster_id)
            )
        """)
        print("   ✅ Created table: analysis_tasks")
        
        # AIReport table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_title VARCHAR(300) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                report_content TEXT NOT NULL,
                report_summary TEXT,
                related_cluster_id INTEGER,
                related_npi VARCHAR(20),
                generated_by INTEGER NOT NULL,
                dify_conversation_id VARCHAR(100),
                generation_time FLOAT,
                status VARCHAR(20) DEFAULT 'draft',
                view_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY (related_cluster_id) REFERENCES cluster_results(cluster_id),
                FOREIGN KEY (related_npi) REFERENCES doctors(npi),
                FOREIGN KEY (generated_by) REFERENCES users(id)
            )
        """)
        print("   ✅ Created table: ai_reports")
        
        # SystemLog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100) NOT NULL,
                module VARCHAR(50) NOT NULL,
                ip_address VARCHAR(50),
                request_data TEXT,
                response_status INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✅ Created table: system_logs")
        
        conn.commit()
        
        # ===== Step 4: Create indexes for performance =====
        print("\n🔧 Step 4: Creating indexes...")
        
        indexes = [
            ("idx_doctors_cluster_id", "CREATE INDEX IF NOT EXISTS idx_doctors_cluster_id ON doctors(cluster_id)"),
            ("idx_doctors_specialty", "CREATE INDEX IF NOT EXISTS idx_doctors_specialty ON doctors(specialty)"),
            ("idx_doctors_state", "CREATE INDEX IF NOT EXISTS idx_doctors_state ON doctors(state)"),
            ("idx_analysis_tasks_status", "CREATE INDEX IF NOT EXISTS idx_analysis_tasks_status ON analysis_tasks(status)"),
            ("idx_analysis_tasks_created_by", "CREATE INDEX IF NOT EXISTS idx_analysis_tasks_created_by ON analysis_tasks(created_by)"),
            ("idx_ai_reports_type", "CREATE INDEX IF NOT EXISTS idx_ai_reports_type ON ai_reports(report_type)"),
            ("idx_ai_reports_generated_by", "CREATE INDEX IF NOT EXISTS idx_ai_reports_generated_by ON ai_reports(generated_by)"),
            ("idx_system_logs_user_id", "CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id)"),
            ("idx_system_logs_action", "CREATE INDEX IF NOT EXISTS idx_system_logs_action ON system_logs(action)"),
        ]
        
        for idx_name, idx_sql in indexes:
            cursor.execute(idx_sql)
            print(f"   ✅ Created index: {idx_name}")
        
        conn.commit()
        
        # ===== Step 5: Verify data integrity =====
        print("\n🔍 Step 5: Verifying data integrity...")
        
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = cursor.fetchone()[0]
        print(f"   ✅ Doctor records: {doctor_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   ✅ User records: {user_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM payment_records")
        payment_count = cursor.fetchone()[0]
        print(f"   ✅ Payment records: {payment_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM analysis_tasks")
        task_count = cursor.fetchone()[0]
        print(f"   ✅ Analysis tasks: {task_count:,}")
        
        cursor.execute("SELECT COUNT(*) FROM ai_reports")
        report_count = cursor.fetchone()[0]
        print(f"   ✅ AI reports: {report_count:,}")
        
        print("\n✅ Migration completed successfully!")
        print(f"📊 Database stats:")
        print(f"   - {doctor_count:,} doctors")
        print(f"   - {user_count:,} users")
        print(f"   - {payment_count:,} payment records")
        print(f"   - {task_count:,} analysis tasks (new)")
        print(f"   - {report_count:,} AI reports (new)")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Database Migration Script - Phase 2 Backend Enhancement")
    print("=" * 60)
    main()
