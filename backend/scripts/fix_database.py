"""
Database Fix Script - Auto-repair detected issues
"""
import sqlite3
import json

def fix_database():
    conn = sqlite3.connect('pharma.db')
    cursor = conn.cursor()

    print("=" * 80)
    print("DATABASE AUTO-FIX SCRIPT")
    print("=" * 80)

    # Fix 1: Complete cluster_results table
    print("\n[FIX 1] Regenerating cluster_results entries...")

    # Get unique cluster_ids from doctors table
    cursor.execute("SELECT DISTINCT cluster_id FROM doctors WHERE cluster_id IS NOT NULL ORDER BY cluster_id")
    cluster_ids = [row[0] for row in cursor.fetchall()]

    print(f"  Found {len(cluster_ids)} clusters in doctors table: {cluster_ids}")

    # Delete existing cluster_results
    cursor.execute("DELETE FROM cluster_results")
    print(f"  Cleared existing cluster_results records")

    # Generate cluster_results for each cluster
    cluster_names = {
        0: "核心高价值客户 (VIP)",
        1: "潜力客户 (Potential)",
        2: "低活跃客户 (Low-Engagement)",
        3: "中等价值客户 (Medium-Value)",
        4: "休眠客户 (Dormant)"
    }

    for cluster_id in cluster_ids:
        # Calculate statistics for this cluster
        cursor.execute(f"""
            SELECT
                COUNT(*) as size,
                AVG(recency_days) as avg_recency,
                AVG(frequency) as avg_frequency,
                AVG(monetary) as avg_monetary,
                MAX(monetary) as max_monetary,
                MIN(monetary) as min_monetary
            FROM doctors
            WHERE cluster_id = {cluster_id}
        """)
        stats = cursor.fetchone()

        # Get total count for percentage
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE cluster_id IS NOT NULL")
        total = cursor.fetchone()[0]

        size = stats[0]
        size_percentage = (size / total * 100) if total > 0 else 0

        # Get top specialty
        cursor.execute(f"""
            SELECT specialty, COUNT(*) as cnt
            FROM doctors
            WHERE cluster_id = {cluster_id} AND specialty IS NOT NULL
            GROUP BY specialty
            ORDER BY cnt DESC
            LIMIT 1
        """)
        top_specialty_row = cursor.fetchone()
        top_specialty = top_specialty_row[0] if top_specialty_row else "Unknown"

        # Create KPI summary
        kpi_summary = {
            "avg_recency_days": round(stats[1], 2) if stats[1] else 0,
            "avg_frequency": round(stats[2], 2) if stats[2] else 0,
            "avg_monetary": round(stats[3], 2) if stats[3] else 0,
            "max_monetary": round(stats[4], 2) if stats[4] else 0,
            "min_monetary": round(stats[5], 2) if stats[5] else 0,
            "top_specialty": top_specialty
        }

        # Insert cluster_result
        cluster_name = cluster_names.get(cluster_id, f"Cluster {cluster_id}")

        cursor.execute("""
            INSERT INTO cluster_results
            (cluster_id, cluster_name, size_count, size_percentage, algorithm, kpi_summary, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cluster_id,
            cluster_name,
            size,
            round(size_percentage, 2),
            'k-means',
            json.dumps(kpi_summary),
            1
        ))

        print(f"  ✓ Created cluster_result for Cluster {cluster_id}: {cluster_name} ({size:,} doctors, {size_percentage:.1f}%)")

    conn.commit()

    # Fix 2: Update user roles
    print("\n[FIX 2] Updating user roles...")

    # Make Rui_3 an admin
    cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'Rui_3'")
    print("  ✓ Upgraded 'Rui_3' to admin role")

    # Make Rui an analyst
    cursor.execute("UPDATE users SET role = 'analyst' WHERE username = 'Rui'")
    print("  ✓ Upgraded 'Rui' to analyst role")

    conn.commit()

    # Fix 3: Drop unused system_logs table
    print("\n[FIX 3] Removing redundant table...")
    try:
        cursor.execute("DROP TABLE IF EXISTS system_logs")
        print("  ✓ Dropped unused 'system_logs' table")
        conn.commit()
    except Exception as e:
        print(f"  ⚠ Could not drop system_logs: {e}")

    # Fix 4: Update cluster labels in doctors table
    print("\n[FIX 4] Updating cluster labels in doctors table...")

    for cluster_id, cluster_name in cluster_names.items():
        cursor.execute("""
            UPDATE doctors
            SET cluster_label = ?
            WHERE cluster_id = ?
        """, (cluster_name, cluster_id))

        affected = cursor.rowcount
        if affected > 0:
            print(f"  ✓ Updated {affected:,} doctors in Cluster {cluster_id}")

    conn.commit()

    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    cursor.execute("SELECT COUNT(*) FROM cluster_results")
    cluster_count = cursor.fetchone()[0]
    print(f"✓ cluster_results records: {cluster_count}")

    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    roles = cursor.fetchall()
    print(f"✓ User roles:")
    for role, count in roles:
        print(f"    - {role}: {count}")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_logs'")
    system_logs_exists = cursor.fetchone()
    print(f"✓ system_logs table exists: {bool(system_logs_exists)}")

    cursor.execute("SELECT COUNT(*) FROM doctors WHERE cluster_label IS NOT NULL")
    labeled_count = cursor.fetchone()[0]
    print(f"✓ Doctors with cluster labels: {labeled_count:,}")

    conn.close()

    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_database()
