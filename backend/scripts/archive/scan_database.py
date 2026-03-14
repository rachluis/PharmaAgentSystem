"""
Database Structure Scanner
Scans pharma.db and outputs detailed structure and data samples
"""
import sqlite3
import json
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

def scan_database():
    conn = sqlite3.connect('pharma.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("DATABASE STRUCTURE SCAN REPORT")
    print("=" * 80)

    # 1. Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"\n[1] TABLES ({len(tables)} total):")
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")

    # 2. Scan each table
    for table_name in tables:
        print(f"\n{'=' * 80}")
        print(f"TABLE: {table_name}")
        print("=" * 80)

        # Get schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print("\n[SCHEMA]")
        print(f"{'Column':<30} {'Type':<15} {'Nullable':<10} {'PK'}")
        print("-" * 80)
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else "NULL"
            pk = "PK" if col[5] else ""
            print(f"{col_name:<30} {col_type:<15} {not_null:<10} {pk}")

        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n[ROW COUNT]: {count:,}")

        # Get sample data (first 3 rows)
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()

            print(f"\n[SAMPLE DATA] (showing {min(3, count)} rows)")
            for idx, row in enumerate(rows, 1):
                print(f"\nRow {idx}:")
                row_dict = dict(row)
                for key, value in row_dict.items():
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"  {key}: {value}")

    # 3. Check indexes
    print(f"\n{'=' * 80}")
    print("INDEXES")
    print("=" * 80)
    cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY tbl_name;")
    indexes = cursor.fetchall()

    current_table = None
    for idx in indexes:
        if idx[1] != current_table:
            current_table = idx[1]
            print(f"\nTable: {current_table}")
        print(f"  - {idx[0]}")
        print(f"    SQL: {idx[2]}")

    # 4. Data quality checks
    print(f"\n{'=' * 80}")
    print("DATA QUALITY ANALYSIS")
    print("=" * 80)

    if 'doctors' in tables:
        print("\n[DOCTORS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM doctors")
        total = cursor.fetchone()[0]
        print(f"  Total doctors: {total:,}")

        cursor.execute("SELECT COUNT(*) FROM doctors WHERE cluster_id IS NOT NULL")
        clustered = cursor.fetchone()[0]
        print(f"  Clustered doctors: {clustered:,} ({100*clustered/total if total > 0 else 0:.1f}%)")

        cursor.execute("SELECT COUNT(DISTINCT cluster_id) FROM doctors WHERE cluster_id IS NOT NULL")
        num_clusters = cursor.fetchone()[0]
        print(f"  Number of clusters: {num_clusters}")

        cursor.execute("SELECT MIN(monetary), MAX(monetary), AVG(monetary) FROM doctors WHERE monetary IS NOT NULL")
        stats = cursor.fetchone()
        if stats[0] is not None:
            print(f"  Monetary: min=${stats[0]:.2f}, max=${stats[1]:,.2f}, avg=${stats[2]:,.2f}")

        cursor.execute("SELECT MIN(frequency), MAX(frequency), AVG(frequency) FROM doctors WHERE frequency IS NOT NULL")
        stats = cursor.fetchone()
        if stats[0] is not None:
            print(f"  Frequency: min={stats[0]}, max={stats[1]}, avg={stats[2]:.2f}")

        cursor.execute("SELECT COUNT(DISTINCT specialty) FROM doctors WHERE specialty IS NOT NULL")
        num_specialties = cursor.fetchone()[0]
        print(f"  Unique specialties: {num_specialties}")

        cursor.execute("SELECT COUNT(DISTINCT state) FROM doctors WHERE state IS NOT NULL")
        num_states = cursor.fetchone()[0]
        print(f"  Unique states: {num_states}")

    if 'users' in tables:
        print("\n[USERS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"  Total users: {total_users}")

        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        roles = cursor.fetchall()
        print("  Role distribution:")
        for role, count in roles:
            print(f"    - {role}: {count}")

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active = cursor.fetchone()[0]
        print(f"  Active users: {active}/{total_users}")

    if 'cluster_results' in tables:
        print("\n[CLUSTER_RESULTS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM cluster_results")
        total_clusters = cursor.fetchone()[0]
        print(f"  Total cluster records: {total_clusters}")

        if total_clusters > 0:
            cursor.execute("SELECT cluster_id, cluster_name, size_count FROM cluster_results ORDER BY cluster_id")
            clusters = cursor.fetchall()
            print("  Cluster details:")
            for cluster in clusters:
                print(f"    - Cluster {cluster[0]}: {cluster[1]} ({cluster[2]:,} doctors)")

    if 'analysis_tasks' in tables:
        print("\n[ANALYSIS_TASKS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM analysis_tasks")
        total_tasks = cursor.fetchone()[0]
        print(f"  Total tasks: {total_tasks}")

        if total_tasks > 0:
            cursor.execute("SELECT status, COUNT(*) FROM analysis_tasks GROUP BY status")
            statuses = cursor.fetchall()
            print("  Task status distribution:")
            for status, count in statuses:
                print(f"    - {status}: {count}")

    if 'ai_reports' in tables:
        print("\n[AI_REPORTS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM ai_reports")
        total_reports = cursor.fetchone()[0]
        print(f"  Total AI reports: {total_reports}")

    if 'sys_login_logs' in tables:
        print("\n[SYS_LOGIN_LOGS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM sys_login_logs")
        total_logs = cursor.fetchone()[0]
        print(f"  Total login logs: {total_logs:,}")

        if total_logs > 0:
            cursor.execute("SELECT status, COUNT(*) FROM sys_login_logs GROUP BY status")
            statuses = cursor.fetchall()
            print("  Login status:")
            for status, count in statuses:
                status_label = "Success" if status == 1 else "Failed"
                print(f"    - {status_label}: {count:,}")

    if 'sys_op_logs' in tables:
        print("\n[SYS_OP_LOGS TABLE]")
        cursor.execute("SELECT COUNT(*) FROM sys_op_logs")
        total_logs = cursor.fetchone()[0]
        print(f"  Total operation logs: {total_logs:,}")

    conn.close()
    print(f"\n{'=' * 80}")
    print("SCAN COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    scan_database()
