import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_logs():
    username = "test_logger_v2"
    password = "password123"
    
    # 0. Register (if not exists)
    print(f"Registering {username}...")
    requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "password": password,
        "email": f"{username}@test.com",
        "full_name": "Test Logger"
    })

    # 1. Login to get token
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Login successful. Token: {token[:10]}...")
        else:
            print(f"Login failed: {resp.text}")
            return
            
        # 2. Perform some operations to generate logs
        print("Generating logs...")
        
        # Operation 1: Create Doctor (POST) - expect log
        # Just a mock call to a non-existent endpoint or existing one to trigger middleware
        # Let's try to logout (POST)
        requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        
        # Operation 2: Get Doctors (GET) - expect NO log (if middleware filters GET)
        requests.get(f"{BASE_URL}/doctors/?page=1&size=10", headers=headers)
        
        print("Waiting for background tasks...")
        time.sleep(2)
        
        # 3. Fetch logs via system API
        print("Fetching Operation Logs...")
        # Need to re-login since we logged out
        resp = requests.post(f"{BASE_URL}/auth/login", data={"username": "Rui_3", "password": "password123"})
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        log_resp = requests.get(f"{BASE_URL}/system/logs/operation", headers=headers)
        if log_resp.status_code == 200:
            logs = log_resp.json()
            print(f"Found {logs['total']} operation logs.")
            for log in logs['items']:
                print(f"- [{log['method']}] {log['path']} ({log['status']}) - {log['latency_ms']}ms")
        else:
            print(f"Failed to fetch logs: {log_resp.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_logs()
