"""
Simplified database setup for Vercel deployment
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for serverless (or PostgreSQL URL if provided)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()