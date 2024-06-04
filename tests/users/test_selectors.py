# pylint: disable=unused-argument, redefined-outer-name
import pytest
from faker import Faker

from app.main import app
from app.common.security import hash_password
from app.common.dependencies import get_db
from app.user import models as user_models, selectors


from tests.deps_overrides import get_test_db

# App Dependency Overrides
app.dependency_overrides[get_db] = get_test_db

# Intialize Faker
faker = Faker()


@pytest.fixture(scope="session")
def setup():
    """This fixture makes sure we have a user in the database"""
    db = next(get_test_db())

    # Check if there is an existing user
    if not db.query(user_models.User).first():
        user = user_models.User(
            full_name=faker.name(),
            email=faker.email(),
            exception_alert_email=faker.email(),  # noqa
            password=hash_password(raw="admin"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)


@pytest.mark.asyncio
async def test_get_user_by_id(setup):
    """This tests the get_user_by_id selector"""
    # Initialize db
    db = next(get_test_db())

    user = db.query(user_models.User).first()
    assert user is not None

    user_id = user.id
    assert await selectors.get_user_by_id(user_id=user_id, db=db) == user
