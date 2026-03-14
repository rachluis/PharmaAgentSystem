"""
Test login with Rui_3 user.
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Try common passwords
passwords = ["123456", "password", "admin", "admin123", "Rui_3"]

print(f"Testing login for user 'Rui_3'...")

for pwd in passwords:
    print(f"Trying password: {pwd}")
    login_data = {
        "username": "Rui_3",
        "password": pwd
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if resp.status_code == 200:
            print(f"✓ Login SUCCESS! Token: {resp.json()['access_token'][:20]}...")
            break
        else:
            print(f"✗ Login failed: {resp.status_code} - {resp.json().get('detail')}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        break  # Verify server is running
