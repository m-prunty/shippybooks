import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def make_engine(db_url: str):
    return create_engine(
        db_url,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        pool_pre_ping=True,  # Verify connections before use (avoids stale connection errors)
        pool_size=10,  # Persistent connections in pool
        max_overflow=20,  # Temporary connections above pool_size under burst load
    )


# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")
#
# engine = create_engine(
#    DATABASE_URL,
#    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
#    pool_pre_ping=True,        # Verify connections before use (avoids stale connection errors)
#    pool_size=10,              # Persistent connections in pool
#    max_overflow=20,           # Temporary connections above pool_size under burst load
#    pool_recycle=1800,         # Recycle connections every 30 min (prevents MySQL "gone away")
# )
#
# session = sessionmaker(bind=engine)()
#
# Base = declarative_base()
#
# class User(Base):
#    __tablename__ = "users"
#
#    id = Column(Integer, primary_key=True, index=True)
#    username = Column(String, unique=True, index=True)
#    email = Column(String, unique=True, index=True)
#    is_active = Column(Boolean, default=True)
#    created_at = Column(DateTime, default=datetime.utcnow())
#    posts = relationship("Post", back_populates="user")
#
# class Post(Base):
#    __tablename__ = "posts"
#
#    id = Column(Integer, primary_key=True, index=True)
#    title = Column(String, index=True)
#    content = Column(String)
#    user_id = Column(Integer, ForeignKey("users.id"))
#
#    created_at = Column(DateTime, default=datetime.utcnow())
#    user = relationship(User, back_populates="posts")
#
# Base.metadata.create_all(bind=engine)
#
# user1 = User(username="testuser", email="test@ex.com")
# user2 = User(username="testuser2", email="test2@ex.com")
#
# post1 = Post(title="First Post", content="This is the first post.", user=user1)
# post2 = Post(title="sec Post 1st", content="This is the sec Post 1st.", user=user1)
# post3 = Post(title="First Post 2nd", content="This is the First Post 2nd.", user=user2)
#
# session.add_all([user1, user2, post1, post2, post3])
# session.commit()
