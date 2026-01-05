from db import Base, engine
from models import User, DailyInput

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
