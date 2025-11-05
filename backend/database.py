from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database configuration for Railway deployment
if os.getenv("DATABASE_URL"):
    # Use Railway-provided PostgreSQL database
    DB_URL = os.getenv("DATABASE_URL")
    # Handle Railway's postgres:// URL format (change to postgresql://)
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
elif os.getenv("ENVIRONMENT") == "production":
    # Fallback for production without DATABASE_URL
    DB_URL = "sqlite:////tmp/todox.db"
else:
    # Local development
    DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
    DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def init_db():
    import models  # noqa
    Base.metadata.create_all(bind=engine)
