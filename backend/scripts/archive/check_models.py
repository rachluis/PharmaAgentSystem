import sys
import os
from sqlalchemy.orm import configure_mappers

# Add current directory to path
sys.path.append(os.getcwd())

print("Importing app.models...")
try:
    from app import models
    print("✅ Models imported")
    
    print("Configuring mappers...")
    configure_mappers()
    print("✅ Mappers configured successfully")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
