import pytest
from app.database import init_db, engine, Base
import os

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    # Initialize database
    init_db()
    yield
    # We could drop tables here if we wanted to be clean
    # Base.metadata.drop_all(bind=engine)
