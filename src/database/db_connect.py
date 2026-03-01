from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.config.db_conf import settings


engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
