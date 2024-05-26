from tests.config import TestingSessionLocal


def get_test_db():
    """This function overrides the get_db function in the dependencies module."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
