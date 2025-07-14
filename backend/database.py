
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the database file path
DATABASE_URL = "sqlite:///./vkyc_audit.db"
DATABASE_DIR = os.path.dirname(DATABASE_URL.split("///")[1])

# Create the base class for declarative models
Base = declarative_base()

# Define the Recording model
class Recording(Base):
    __tablename__ = "recordings"
    id = Column(Integer, primary_key=True, index=True)
    lan_id = Column(String, unique=True, nullable=False, index=True)
    call_duration_minutes = Column(Integer)
    status = Column(String, nullable=False, default="APPROVED")
    time = Column(String)
    date = Column(String, nullable=False, index=True)
    nfs_upload_time = Column(String)
    nfs_file_path = Column(Text, unique=True, nullable=False)

# Define the User model for authentication
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # e.g., 'TL', 'Manager'

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database by creating all tables.
    It also creates the directory for the database file if it doesn't exist.
    """
    # Ensure the directory for the database file exists
    if not os.path.exists(DATABASE_DIR) and DATABASE_DIR:
        os.makedirs(DATABASE_DIR)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized and all tables created.")

if __name__ == "__main__":
    init_db()
