import requests
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_avatar_upload():
    print("Testing Avatar Upload...")
    
    # 1. Login
    username = "test_logger_v2" # Using the user created in previous test
    password = "password123"
    
    print(f"Logging in as {username}...")
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
        
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")
    
    # 2. Create a dummy image file
    filename = "test_avatar.png"
    with open(filename, "wb") as f:
        f.write(os.urandom(1024)) # Random binary data simulating an image
        
    # 3. Upload
    print("Uploading avatar...")
    with open(filename, "rb") as f:
        files = {"file": ("test_avatar.png", f, "image/png")}
        resp = requests.post(f"{BASE_URL}/auth/upload-avatar", headers=headers, files=files)
        
    if resp.status_code == 200:
        user = resp.json()
        print("Upload successful!")
        print(f"New Avatar URL: {user['avatar_url']}")
        
        # 4. Verify static file access
        # The URL returned is like /uploads/avatars/xxx. We need to prepend base URL (without /api/v1)
        # Backend mounts /uploads at root.
        static_url = f"http://127.0.0.1:8000{user['avatar_url']}"
        print(f"Verifying static file access at: {static_url}")
        static_resp = requests.get(static_url)
        if static_resp.status_code == 200:
            print("Static file is accessible.")
        else:
            print(f"Static file access failed: {static_resp.status_code}")
            
    else:
        print(f"Upload failed: {resp.text}")
        
    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    test_avatar_upload()
