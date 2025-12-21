"""
Test ClusterResultResponse validation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas import ClusterResultResponse

# Simulate database data with JSON strings
test_data = {
    "cluster_id": 1,
    "cluster_name": "Test Cluster",
    "size_count": 1000,
    "size_percentage": 25.5,
    "kpi_summary": '{"0": {"count": 229814, "percentage": 31.11}}',  # JSON string
    "cluster_labels": '{"0": "High Value", "1": "Medium Value"}',  # JSON string
    "features_used": '["recency_days", "frequency", "monetary"]',  # JSON string
    "visualization_data": '{"scatter": []}',  # JSON string
    "silhouette_score": 0.65,
    "inertia": 12345.67,
    "is_active": True
}

print("Testing ClusterResultResponse with JSON string fields...")
try:
    result = ClusterResultResponse(**test_data)
    print(f"✓ Success!")
    print(f"  kpi_summary type: {type(result.kpi_summary)}")
    print(f"  cluster_labels type: {type(result.cluster_labels)}")
    print(f"  features_used type: {type(result.features_used)}")
    print(f"\n✓ All validations passed!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
