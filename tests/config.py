from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import DBBase

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


DBBase.metadata.create_all(bind=engine)
