"""
Quick test to verify analysis tasks API endpoints.
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# First, login to get token
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("=" * 60)
print("Testing Analysis Tasks API")
print("=" * 60)

# Login
print("\n1. Logging in...")
try:
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)  # Use data= for form
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"✓ Login successful! Token: {token[:20]}...")
    else:
        print(f"✗ Login failed: {resp.status_code}")
        print(resp.text)
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test GET /analysis/tasks
print("\n2. Testing GET /analysis/tasks...")
try:
    resp = requests.get(f"{BASE_URL}/analysis/tasks", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"✓ Response: {resp.json()}")
    else:
        print(f"✗ Error: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test GET /analysis/tasks/results/list
print("\n3. Testing GET /analysis/tasks/results/list...")
try:
    resp = requests.get(f"{BASE_URL}/analysis/tasks/results/list", headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        results = resp.json()
        print(f"✓ Found {len(results)} cluster results")
        if results:
            print(f"  First result: cluster_id={results[0].get('cluster_id')}")
    else:
        print(f"✗ Error: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test POST /analysis/tasks (create clustering task)
print("\n4. Testing POST /analysis/tasks (create task)...")
task_data = {
    "task_name": "Test K-Means Analysis",
    "task_type": "clustering",
    "parameters": {
        "k": 3,
        "features": ["recency_days", "frequency", "monetary"]
    }
}
try:
    resp = requests.post(f"{BASE_URL}/analysis/tasks", json=task_data, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        task = resp.json()
        print(f"✓ Task created! ID: {task.get('task_id')}, Status: {task.get('status')}")
    else:
        print(f"✗ Error: {resp.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("API Test Complete!")
print("=" * 60)
