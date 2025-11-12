from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
sys.path.insert(0, '/app')

try:
    from models import Base
except ImportError:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

# PostgreSQL Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@progress-db:5432/progress_db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Configure the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    """Create all tables defined in models.py"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()