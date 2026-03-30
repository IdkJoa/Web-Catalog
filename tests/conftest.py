import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.models import Base

# --- Use an in-memory SQLite DB for fast integration tests ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables once per session
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(engine):
    """Provides a transactional database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
