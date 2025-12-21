import bcrypt
import time

try:
    start = time.time()
    password = b"password123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print(f"Hashing time: {time.time() - start:.4f}s")
    print(f"Hash: {hashed}")
    
    start = time.time()
    valid = bcrypt.checkpw(password, hashed)
    print(f"Check time: {time.time() - start:.4f}s")
    print(f"Valid: {valid}")
except Exception as e:
    print(f"Error: {e}")
