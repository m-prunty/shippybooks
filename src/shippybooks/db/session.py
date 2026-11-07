from sqlalchemy.orm import Session, sessionmaker

from ..settings import settings
from .base import make_engine

engine = make_engine(settings.database_url)
session = sessionmaker(engine, expire_on_commit=False)


def get_session() -> Session:
    with session() as session:
        yield session
