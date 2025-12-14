from app.database import engine, Base
from app.models import User, Doctor, PaymentRecord, ClusterResult

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
