import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Checking imports...")

try:
    print("Importing app.schemas...")
    from app import schemas
    print("✅ schemas imported")
except Exception as e:
    print(f"❌ schemas failed: {e}")

try:
    print("Importing app.routers.auth...")
    from app.routers import auth
    print("✅ routers.auth imported")
except Exception as e:
    print(f"❌ routers.auth failed: {e}")

try:
    print("Importing app.routers.doctors...")
    from app.routers import doctors
    print("✅ routers.doctors imported")
except Exception as e:
    print(f"❌ routers.doctors failed: {e}")

try:
    print("Importing app.routers.reports...")
    from app.routers import reports
    print("✅ routers.reports imported")
except Exception as e:
    print(f"❌ routers.reports failed: {e}")

try:
    print("Importing app.routers.analysis_tasks...")
    from app.routers import analysis_tasks
    print("✅ routers.analysis_tasks imported")
except Exception as e:
    print(f"❌ routers.analysis_tasks failed: {e}")

try:
    print("Importing app.main...")
    from app import main
    print("✅ main imported")
except Exception as e:
    print(f"❌ main failed: {e}")
