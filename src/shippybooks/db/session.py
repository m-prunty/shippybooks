from .base import make_engine, Base
from sqlalchemy.orm import Session
from settings import settings

engine = make_engine(settings.database_url)
session = sessionmaker(engine, expire_on_commit=False)

def get_session() -> Session:
    with session() as session:
        yield session
