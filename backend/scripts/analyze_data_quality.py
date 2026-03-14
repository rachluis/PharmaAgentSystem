"""
Advanced Data Quality Analysis and Clustering Optimization
数据质量深度分析与聚类优化方案
"""
import sqlite3
import numpy as np
import json
from datetime import datetime

def analyze_data_quality():
    conn = sqlite3.connect('pharma.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print("DATA QUALITY DEEP ANALYSIS")
    print("=" * 80)

    # 1. RFM Data Quality Analysis
    print("\n[1] RFM DATA QUALITY")
    print("-" * 80)

    # Get RFM statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN monetary > 0 THEN 1 END) as has_monetary,
            COUNT(CASE WHEN frequency > 0 THEN 1 END) as has_frequency,
            COUNT(CASE WHEN recency_days IS NOT NULL THEN 1 END) as has_recency,
            MIN(monetary) as min_m,
            MAX(monetary) as max_m,
            AVG(monetary) as avg_m,
            MIN(frequency) as min_f,
            MAX(frequency) as max_f,
            AVG(frequency) as avg_f
        FROM doctors
        WHERE cluster_id IS NOT NULL
    """)

    stats = cursor.fetchone()
    print(f"Total doctors: {stats['total']:,}")
    print(f"  With Monetary > 0: {stats['has_monetary']:,} ({100*stats['has_monetary']/stats['total']:.2f}%)")
    print(f"  With Frequency > 0: {stats['has_frequency']:,} ({100*stats['has_frequency']/stats['total']:.2f}%)")
    print(f"  With Recency data: {stats['has_recency']:,} ({100*stats['has_recency']/stats['total']:.2f}%)")

    print(f"\nMonetary Range: ${stats['min_m']:.2f} - ${stats['max_m']:,.2f} (avg: ${stats['avg_m']:,.2f})")
    print(f"Frequency Range: {stats['min_f']} - {stats['max_f']} (avg: {stats['avg_f']:.2f})")

    # Check for outliers
    cursor.execute("""
        SELECT
            COUNT(CASE WHEN monetary > 1000000 THEN 1 END) as millionaires,
            COUNT(CASE WHEN frequency > 100 THEN 1 END) as super_active,
            COUNT(CASE WHEN monetary = 0 AND frequency = 0 THEN 1 END) as zero_engagement
        FROM doctors
        WHERE cluster_id IS NOT NULL
    """)
    outliers = cursor.fetchone()

    print(f"\nOutliers Detection:")
    print(f"  Monetary > $1M: {outliers['millionaires']:,} doctors")
    print(f"  Frequency > 100: {outliers['super_active']:,} doctors")
    print(f"  Zero engagement (M=0, F=0): {outliers['zero_engagement']:,} doctors")

    # 2. Data Distribution Analysis (Percentiles)
    print("\n[2] DATA DISTRIBUTION (PERCENTILES)")
    print("-" * 80)

    cursor.execute("""
        SELECT monetary, frequency
        FROM doctors
        WHERE cluster_id IS NOT NULL
        ORDER BY monetary
    """)

    data = cursor.fetchall()
    monetary_values = [row['monetary'] for row in data]

    cursor.execute("""
        SELECT monetary, frequency
        FROM doctors
        WHERE cluster_id IS NOT NULL
        ORDER BY frequency
    """)
    data = cursor.fetchall()
    frequency_values = [row['frequency'] for row in data]

    percentiles = [10, 25, 50, 75, 90, 95, 99]

    print("\nMonetary Distribution:")
    for p in percentiles:
        idx = int(len(monetary_values) * p / 100)
        value = monetary_values[idx]
        print(f"  P{p:2d}: ${value:,.2f}")

    print("\nFrequency Distribution:")
    for p in percentiles:
        idx = int(len(frequency_values) * p / 100)
        value = frequency_values[idx]
        print(f"  P{p:2d}: {value}")

    # 3. Clustering Quality Analysis
    print("\n[3] CLUSTERING QUALITY ANALYSIS")
    print("-" * 80)

    cursor.execute("""
        SELECT
            cluster_id,
            cluster_name,
            size_count,
            size_percentage,
            kpi_summary
        FROM cluster_results
        ORDER BY cluster_id
    """)

    clusters = cursor.fetchall()

    print("\nCluster Statistics:")
    for cluster in clusters:
        kpi = json.loads(cluster['kpi_summary'])
        print(f"\nCluster {cluster['cluster_id']}: {cluster['cluster_name']}")
        print(f"  Size: {cluster['size_count']:,} ({cluster['size_percentage']:.1f}%)")
        print(f"  Avg Monetary: ${kpi['avg_monetary']:,.2f}")
        print(f"  Avg Frequency: {kpi['avg_frequency']:.2f}")
        print(f"  Max Monetary: ${kpi['max_monetary']:,.2f}")
        print(f"  Min Monetary: ${kpi['min_monetary']:,.2f}")

    # 4. Cluster Separation Analysis
    print("\n[4] CLUSTER SEPARATION (Inter-cluster distance)")
    print("-" * 80)

    # Calculate cluster centers
    centers = []
    for cluster in clusters:
        kpi = json.loads(cluster['kpi_summary'])
        centers.append([
            kpi['avg_recency_days'],
            kpi['avg_frequency'],
            kpi['avg_monetary']
        ])

    print("\nCluster Centers (R, F, M):")
    for i, center in enumerate(centers):
        print(f"  Cluster {i}: R={center[0]:.2f}, F={center[1]:.2f}, M=${center[2]:,.2f}")

    # 5. Specialty Distribution by Cluster
    print("\n[5] SPECIALTY DISTRIBUTION BY CLUSTER")
    print("-" * 80)

    for cluster_id in [0, 1, 2]:
        cursor.execute(f"""
            SELECT specialty, COUNT(*) as cnt
            FROM doctors
            WHERE cluster_id = {cluster_id} AND specialty IS NOT NULL
            GROUP BY specialty
            ORDER BY cnt DESC
            LIMIT 5
        """)

        top_specialties = cursor.fetchall()
        print(f"\nCluster {cluster_id} - Top 5 Specialties:")
        for spec in top_specialties:
            print(f"  {spec['specialty']:<40} {spec['cnt']:>6,} doctors")

    # 6. State Distribution by Cluster
    print("\n[6] STATE DISTRIBUTION BY CLUSTER")
    print("-" * 80)

    for cluster_id in [0, 1, 2]:
        cursor.execute(f"""
            SELECT state, COUNT(*) as cnt
            FROM doctors
            WHERE cluster_id = {cluster_id} AND state IS NOT NULL
            GROUP BY state
            ORDER BY cnt DESC
            LIMIT 5
        """)

        top_states = cursor.fetchall()
        print(f"\nCluster {cluster_id} - Top 5 States:")
        for state in top_states:
            print(f"  {state['state']:<10} {state['cnt']:>6,} doctors")

    # 7. Data Quality Issues
    print("\n[7] DATA QUALITY ISSUES")
    print("-" * 80)

    issues = []

    # Issue 1: Zero engagement doctors
    cursor.execute("""
        SELECT COUNT(*) FROM doctors
        WHERE cluster_id IS NOT NULL
        AND monetary = 0 AND frequency = 0
    """)
    zero_count = cursor.fetchone()[0]
    if zero_count > 0:
        issues.append(f"ISSUE: {zero_count:,} doctors with zero engagement (M=0, F=0)")

    # Issue 2: Extreme outliers
    cursor.execute("""
        SELECT COUNT(*) FROM doctors
        WHERE cluster_id IS NOT NULL
        AND monetary > 10000000
    """)
    extreme_outliers = cursor.fetchone()[0]
    if extreme_outliers > 0:
        issues.append(f"ISSUE: {extreme_outliers:,} doctors with Monetary > $10M (extreme outliers)")

    # Issue 3: Missing specialty
    cursor.execute("""
        SELECT COUNT(*) FROM doctors
        WHERE cluster_id IS NOT NULL
        AND (specialty IS NULL OR specialty = '')
    """)
    missing_specialty = cursor.fetchone()[0]
    if missing_specialty > 0:
        issues.append(f"WARNING: {missing_specialty:,} doctors missing specialty data")

    if issues:
        print("\nIdentified Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nNo major data quality issues found!")

    # 8. Recommendations
    print("\n[8] OPTIMIZATION RECOMMENDATIONS")
    print("-" * 80)

    recommendations = []

    # Check if log transformation needed
    cursor.execute("""
        SELECT AVG(monetary) / NULLIF(
            (SELECT monetary FROM doctors WHERE cluster_id IS NOT NULL ORDER BY monetary LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM doctors WHERE cluster_id IS NOT NULL)),
        0) as skewness_ratio
        FROM doctors
        WHERE cluster_id IS NOT NULL
    """)
    skewness = cursor.fetchone()[0]

    if skewness and skewness > 10:
        recommendations.append("RECOMMEND: Apply log transformation to Monetary (high skewness detected)")

    # Check cluster balance
    cursor.execute("""
        SELECT
            MAX(size_percentage) as max_pct,
            MIN(size_percentage) as min_pct
        FROM cluster_results
    """)
    balance = cursor.fetchone()

    if balance['max_pct'] / balance['min_pct'] > 2:
        recommendations.append("RECOMMEND: Clusters are imbalanced (largest/smallest > 2x)")

    # Check if more clusters needed
    if len(clusters) < 4:
        recommendations.append("CONSIDER: Testing K=4 or K=5 for finer segmentation")

    recommendations.append("RECOMMEND: Implement incremental clustering for performance")
    recommendations.append("RECOMMEND: Add caching for clustering results")
    recommendations.append("RECOMMEND: Use sampling for quick exploratory analysis")

    print("\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    conn.close()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_data_quality()
