from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database configuration - simple and robust
if os.getenv("ENVIRONMENT") == "production":
    # Railway production: use in-memory SQLite (ephemeral but works)
    DB_URL = "sqlite:///:memory:"
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
