"""
Quick test to verify the fix for analysis tasks API.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas import AnalysisTaskResponse
from datetime import datetime

# Test the field_validator
print("Testing AnalysisTaskResponse with JSON string parameters...")

# Simulate database data (parameters as JSON string)
test_data = {
    "task_id": 1,
    "task_name": "Test Clustering",
    "task_type": "clustering",
    "parameters": '{"k": 5, "features": ["recency_days", "frequency", "monetary"]}',  # JSON string
    "status": "pending",
    "progress": 0,
    "created_at": datetime.now()
}

try:
    task = AnalysisTaskResponse(**test_data)
    print(f"✓ Success! Parameters parsed correctly:")
    print(f"  Type: {type(task.parameters)}")
    print(f"  Value: {task.parameters}")
    print(f"\n✓ Validation passed!")
except Exception as e:
    print(f"✗ Error: {e}")
