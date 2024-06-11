import random

from faker import Faker
from fastapi.testclient import TestClient

from app.common.dependencies import get_db
from app.main import app
from app.user import models as user_models, security

from tests.deps_overrides import get_test_db

# App Dependency Overrides
app.dependency_overrides[get_db] = get_test_db


# Initialize the TestClient
client = TestClient(app)

# Intialize Faker
faker = Faker()

USER = {
    "full_name": faker.name(),
    "email": faker.email(),
    "exception_alert_email": faker.email(),
    "password": "admin",
}
ACCESS_TOKEN = "Bearer "
REFRESH_TOKEN = ""


def test_user_create():
    """This tests the create_user endpoint"""
    good_user = USER.copy()

    good_response = client.post(
        "/users",
        json=good_user,
    )

    registered_user = client.post(
        "/users",
        json=good_user,
    )

    # Check if the good response status code is 201
    assert good_response.status_code == 201

    # Check if the response data is equal to the fake_user
    response_data = good_response.json()
    assert "data" in response_data
    assert response_data["data"]["id"] is not None
    assert response_data["data"]["full_name"] == good_user["full_name"]
    assert response_data["data"]["email"] == good_user["email"]
    assert (
        response_data["data"]["exception_alert_email"]
        == good_user["exception_alert_email"]
    )
    assert response_data["data"]["is_active"] is True
    assert response_data["data"]["is_verified"] is False

    # Check if the user is already registered
    assert registered_user.status_code == 400
    registered_user = registered_user.json()
    assert (
        registered_user.get("data", {}).get("message")
        == f"user with email {good_user['email']} exists"
    )


def test_user_login():
    """This test is for the user login endpoint"""

    good_credentials = {
        "email": USER["email"],
        "password": USER["password"],
        "remember_me": random.choice([True, False]),
    }
    bad_credentials = {
        "email": faker.email(),
        "password": faker.password(),
        "remember_me": random.choice([True, False]),
    }
    good_response = client.post("/users/login", json=good_credentials)
    bad_response = client.post("/users/login", json=bad_credentials)

    # Check invalid credentials
    assert bad_response.status_code == 401
    bad_response = bad_response.json()
    assert bad_response.get("data", {}).get("message") == "Invalid login credentials"
    # Check valid credentials
    response_data = good_response.json()

    response_data = good_response.json()
    assert "data" in response_data
    assert response_data["data"]["user"]["id"] is not None
    assert response_data["data"]["user"]["full_name"] == USER["full_name"]
    assert response_data["data"]["user"]["email"] == USER["email"]
    assert (
        response_data["data"]["user"]["exception_alert_email"]
        == USER["exception_alert_email"]
    )
    assert response_data["data"]["user"]["is_active"] is True
    assert response_data["data"]["user"]["is_verified"] is False
    # Check if tokens were provided
    assert response_data["data"]["tokens"]["token_type"] == "Bearer"
    assert "access_token" in response_data["data"]["tokens"]
    assert "refresh_token" in response_data["data"]["tokens"]
    assert response_data["data"]["tokens"]["access_token"] != ""
    assert response_data["data"]["tokens"]["refresh_token"] != ""

    # Update access token
    global ACCESS_TOKEN  # pylint: disable=global-statement
    global REFRESH_TOKEN  # pylint: disable=global-statement
    ACCESS_TOKEN += response_data["data"]["tokens"]["access_token"]
    REFRESH_TOKEN += response_data["data"]["tokens"]["refresh_token"]


def test_user_me():
    """This test is for the user detail (me) endpoint"""
    good_response = client.get(
        "/users/me",
        headers={"Authorization": ACCESS_TOKEN},
    )
    bad_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {faker.sha256()}"},  # Invalid Token
    )

    # Check bad response
    assert bad_response.status_code == 401

    # Check good response
    response_data = good_response.json()

    assert good_response.status_code == 200
    assert response_data["data"]["id"] is not None
    assert response_data["data"]["full_name"] == USER["full_name"]
    assert response_data["data"]["email"] == USER["email"]
    assert (
        response_data["data"]["exception_alert_email"] == USER["exception_alert_email"]
    )
    assert response_data["data"]["is_active"] is True
    assert response_data["data"]["is_verified"] is False


def test_user_edit():
    """This test is for the user edit endpoint"""
    new_user = USER.copy()
    new_user["full_name"] = faker.name()

    good_response = client.put(
        "/users",
        headers={"Authorization": ACCESS_TOKEN},
        json=new_user,
    )

    bad_response = client.put(
        "/users",
        headers={"Authorization": ACCESS_TOKEN},
        json={},
    )

    bad_user = client.put(
        "/users",
        headers={"Authorization": "BAD_ACCESS_TOKEN"},
        json={},
    )
    # Check bad response
    assert bad_response.status_code == 400
    bad_response = bad_response.json()
    assert bad_response.get("data", {}).get("message") == "No data to update"

    # Check good
    response_data = good_response.json()

    assert good_response.status_code == 200
    assert response_data["data"]["id"] is not None
    assert response_data["data"]["full_name"] == new_user["full_name"]
    assert response_data["data"]["email"] == USER["email"]
    assert (
        response_data["data"]["exception_alert_email"] == USER["exception_alert_email"]
    )
    assert response_data["data"]["is_active"] is True
    assert response_data["data"]["is_verified"] is False

    # check for bad_user
    assert bad_user.status_code == 401
    bad_user = bad_user.json()
    assert bad_user.get("data", {}).get("message") == "Invalid token"


def test_user_token():
    """This test is for the user token endpoint"""
    bad_response = client.post("/users/token", json={"refresh_token": faker.sha256()})
    good_response = client.post("/users/token", json={"refresh_token": REFRESH_TOKEN})

    # Check bad response
    assert bad_response.status_code == 401

    # Check good response
    response_data = good_response.json()
    assert good_response.status_code == 200
    assert "access_token" in response_data["data"]


def test_user_logout():
    """This test is for the user logout endpoint"""

    bad_response = client.delete(
        "/users/logout",
        headers={"Authorization": f"Bearer {faker.sha256()}"},  # Invalid Token
    )
    good_response = client.delete(
        "/users/logout",
        headers={"Authorization": ACCESS_TOKEN},
    )

    # Check bad response
    assert bad_response.status_code == 401

    # Check good response
    assert good_response.status_code == 200


def test_user_notifications():
    """This test is for the user notifications endpoint"""
    db = next(get_test_db())

    # Get existing user
    existing_user = db.query(user_models.User).first()

    assert existing_user is not None

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    good_response = client.get(
        "/users/notifications",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Check good response
    assert good_response.status_code == 200


def test_user_notification_read():
    """This test is for the user notification read endpoint"""
    db = next(get_test_db())

    # Get existing user
    existing_user = db.query(user_models.User).first()

    assert existing_user is not None

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"GUARDIAN-{existing_user.id}", expire_in=3
    )

    # Get existing notification
    existing_notification = db.query(user_models.UserNotification).first()

    assert existing_notification is not None

    good_response = client.put(
        "/users/notifications/read",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Check good response
    assert good_response.status_code == 200


def test_user_password_change():
    """This test is for the user change password endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a guardian exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    bad_response = client.put(
        "/users/password/change",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"old_password": faker.password(), "new_password": faker.password()},
    )
    good_response = client.put(
        "/users/password/change",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"old_password": "admin", "new_password": "admin"},
    )

    # Check bad response
    assert bad_response.status_code == 400

    # Check good response
    assert good_response.status_code == 200


def test_user_password_confirm():
    """This test is for the user confirm password endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    bad_response = client.post(
        "/users/password/confirm",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"password": faker.password()},
    )
    good_response = client.post(
        "/users/password/confirm",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"password": "admin"},
    )

    # Check bad response
    bad_response_data = bad_response.json()

    assert bad_response_data["data"]["is_correct"] is False

    # Check good response
    good_response_data = good_response.json()

    assert good_response_data["data"]["is_correct"] is True


def test_get_user_configurations():
    """This test is for the get user configurations endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    good_response = client.get(
        "/users/configurations",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Check good response
    assert good_response.status_code == 200


def test_user_configurations_edit():
    """This test is for the user configurations edit endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    good_response = client.put(
        "/users/configurations",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"notification_email": False, "notification_inapp": False},
    )

    # Check good response
    assert good_response.status_code == 200


def test_news_letter_subscribe():
    """This test is for the news letter subscribe endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    good_response = client.post(
        "/users/newsletter",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": faker.email()},
    )

    # Check good response
    assert good_response.status_code == 200


COMPANY = {
    "name": faker.name(),
    "registration_number": faker.name(),
    "email": faker.email(),
    "phone": faker.phone_number(),
    "address": faker.address(),
    "tax_identification_number": faker.name(),
}


def test_company_create():
    """This test is for the create company endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )
    company = COMPANY.copy()

    good_response = client.post(
        "users/company",
        headers={"Authorization": f"Bearer {access_token}"},
        json=company,
    )

    # Check good response
    assert good_response.status_code == 200


def test_company_edit():
    """This test is for the edit company endpoint"""
    db = next(get_test_db())

    # Generate good reset password token
    existing_user = db.query(user_models.User).first()
    assert existing_user is not None  # Confirm that a user exists

    # Generate access token
    access_token = security.generate_user_token(
        token_type="access", sub=f"USER-{existing_user.id}", expire_in=3
    )

    bad_response = client.put(
        "users/company",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )

    good_response = client.put(
        "users/company",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": faker.name()},
    )

    # Check good response
    assert good_response.status_code == 200
    assert bad_response.status_code == 400
