from sqlalchemy import create_engine
from models import Base

# Configure your database connection
engine = create_engine('sqlite:///mydatabase.db')

# Drop existing tables (if needed)
Base.metadata.drop_all(engine)

# Create new tables
Base.metadata.create_all(engine)

# Optional: Perform data migration if needed

print("Database tables reinitialized successfully.")
