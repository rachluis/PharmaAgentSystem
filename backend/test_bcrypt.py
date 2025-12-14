from app.core.security import verify_password, get_password_hash
import time

password = "secret_password"
print("Hashing password...")
start = time.time()
hashed = get_password_hash(password)
end = time.time()
print(f"Hashing took: {end - start:.4f} seconds")

print("Verifying password...")
start = time.time()
result = verify_password(password, hashed)
end = time.time()
print(f"Verification took: {end - start:.4f} seconds")
print(f"Result: {result}")
