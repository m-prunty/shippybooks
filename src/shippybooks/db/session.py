from sqlalchemy.orm import Session, sessionmaker

from ..settings import settings
from .base import make_engine

engine = make_engine(settings.database_url)


def get_session() -> Session:
    session = sessionmaker(engine, expire_on_commit=False)
    with session() as session:
        yield session
