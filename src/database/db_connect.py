from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.db_conf import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
