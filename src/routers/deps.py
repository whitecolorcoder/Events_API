from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.db_connect import SessionLocal


def get_session() -> Session:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
