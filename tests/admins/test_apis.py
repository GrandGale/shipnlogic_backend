import random

from faker import Faker
from fastapi.testclient import TestClient

from app.common.dependencies import get_db
from app.main import app


from tests.deps_overrides import get_test_db

# App Dependency Overrides
app.dependency_overrides[get_db] = get_test_db

# Initialize the TestClient
client = TestClient(app)

# Initialize Faker
faker = Faker()

ADMIN = {
    "full_name": faker.name(),
    "email": faker.email(),
    "phone_number": faker.phone_number(),
    "gender": "MALE",
    "permission": "SUPER_ADMIN",
    "password": "admin",
}

ACCESS_TOKEN = "Bearer "
REFRESH_TOKEN = ""


def test_admin_create():
    """This tests the admin_create endpoint"""
    good_admin = ADMIN.copy()

    good_response = client.post(
        "/admins",
        json=good_admin,
    )

    registered_admin = client.post(
        "/admins",
        json=good_admin,
    )

    # Check if the good response status code is 201
    assert good_response.status_code == 201

    # Check if the response data is equal to the fake_admin
    response_data = good_response.json()
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert response_data["data"]["id"] is not None
    assert response_data["data"]["full_name"] == good_admin["full_name"]
    assert response_data["data"]["email"] == good_admin["email"]
    assert response_data["data"]["phone_number"] == good_admin["phone_number"]
    assert response_data["data"]["permission"] == good_admin["permission"]
    assert response_data["data"]["profile_picture_url"] == "/default_profile.jpg"

    # Check if the admin is already registered
    assert registered_admin.status_code == 400
    registered_admin = registered_admin.json()
    assert (
        registered_admin.get("data", {}).get("message")
        == f"Admin with email {good_admin['email']} exists"
    )


def test_admin_login():
    """This test is for the admin login endpoint"""

    admin_credentials = {
        "email": ADMIN["email"],
        "password": ADMIN["password"],
        "remember_me": random.choice([True, False]),
    }

    bad_credentials = {"email": faker.email(), "password": faker.password()}

    good_response = client.post("/admins/login", json=admin_credentials)
    bad_response = client.post("/admins/login", json=bad_credentials)

    # Check invalid credentials
    assert bad_response.status_code == 401
    bad_response_data = bad_response.json()
    assert bad_response_data["status"] == "error"
    assert bad_response_data["data"]["message"] == "Invalid login credentials"

    # Check valid credentials
    assert good_response.status_code == 200
    response_data = good_response.json()
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "admin" in response_data["data"]
    assert "tokens" in response_data["data"]

    admin_data = response_data["data"]["admin"]
    tokens_data = response_data["data"]["tokens"]

    assert admin_data["id"] is not None
    assert admin_data["profile_picture_url"] == "/default_profile.jpg"
    assert admin_data["full_name"] == ADMIN["full_name"]
    assert admin_data["email"] == ADMIN["email"]
    assert admin_data["phone_number"] == ADMIN["phone_number"]
    assert admin_data["permission"] == "SUPER_ADMIN"

    assert tokens_data["token_type"] == "Bearer"
    assert "access_token" in tokens_data
    assert "refresh_token" in tokens_data
    assert tokens_data["access_token"] != ""
    assert tokens_data["refresh_token"] != ""

    # Update access token for further tests
    global ACCESS_TOKEN  # pylint: disable=global-statement
    global REFRESH_TOKEN  # pylint: disable=global-statement
    ACCESS_TOKEN += response_data["data"]["tokens"]["access_token"]
    REFRESH_TOKEN += response_data["data"]["tokens"]["refresh_token"]


def test_admin_me():
    """This test is for the admin me endpoint"""

    # Successful request with valid token
    good_response = client.get("/admins/me", headers={"Authorization": ACCESS_TOKEN})

    # Unauthorized request (no token provided)
    bad_response = client.get("/admins/me", headers={"Authorization": "ACCESS_TOKEN"})

    # Check successful response
    assert good_response.status_code == 200
    good_response_data = good_response.json()
    assert good_response_data["status"] == "success"
    assert "data" in good_response_data

    admin_data = good_response_data["data"]

    assert admin_data["id"] is not None
    assert admin_data["profile_picture_url"] == "/default_profile.jpg"
    assert admin_data["full_name"] == ADMIN["full_name"]
    assert admin_data["email"] == ADMIN["email"]
    assert admin_data["phone_number"] == ADMIN["phone_number"]
    assert admin_data["permission"] == ADMIN["permission"]
    # Check unauthorized access response
    assert bad_response.status_code == 401
    bad_response_data = bad_response.json()
    assert bad_response_data["status"] == "error"
    assert "data" in bad_response_data
    assert bad_response_data["data"]["message"] == "Invalid token"


def test_admin_edit():
    """This test is for the admin edit endpoint"""
    new_admin = ADMIN.copy()
    new_admin["full_name"] = faker.name()
    new_admin["permission"] = "ADMIN"

    good_response = client.put(
        "/admins", headers={"Authorization": ACCESS_TOKEN}, json=new_admin
    )

    bad_response = client.put(
        "/admins", headers={"Authorization": ACCESS_TOKEN}, json={}
    )
    new_admin["permission"] = "SUPER_ADMIN"
    bad_admin_response = client.put(
        "/admins", headers={"Authorization": ACCESS_TOKEN}, json=new_admin
    )

    # Check bad response
    assert bad_response.status_code == 400
    bad_response = bad_response.json()
    assert bad_response["status"] == "error"
    assert bad_response.get("data", {}).get("message") == "No data to update"

    # Check bad admin response
    assert bad_admin_response.status_code == 400
    bad_admin_response = bad_admin_response.json()
    assert bad_admin_response["status"] == "error"
    assert (
        bad_admin_response.get("data", {}).get("message") == "You cannot edit an admin"
    )

    # Check good response
    assert good_response.status_code == 200
    response_data = good_response.json()
    assert response_data["status"] == "success"
    assert "data" in response_data

    admin_data = response_data["data"]

    assert admin_data["id"] is not None
    assert admin_data["profile_picture_url"] == "/default_profile.jpg"
    assert admin_data["full_name"] == new_admin["full_name"]
    assert admin_data["email"] == new_admin["email"]
    assert admin_data["phone_number"] == new_admin["phone_number"]
    assert admin_data["permission"] == "ADMIN"


def test_generate_admin_access_token():
    """This test is for the admin access token generation endpoint"""

    # Valid refresh token
    good_response = client.post("/admins/token", json={"refresh_token": REFRESH_TOKEN})

    # Invalid refresh token
    bad_response = client.post("/admins/token", json={"refresh_token": faker.sha256()})

    # Check valid response
    assert good_response.status_code == 200
    good_response_data = good_response.json()
    assert good_response_data["status"] == "success"
    assert "data" in good_response_data
    assert "access_token" in good_response_data["data"]
    assert isinstance(good_response_data["data"]["access_token"], str)

    # Check invalid response
    assert bad_response.status_code == 401
    bad_response_data = bad_response.json()
    assert bad_response_data["status"] == "error"
    assert bad_response_data["data"]["message"] == "Invalid Token"


def test_admin_logout():
    """This test is for the admin logout endpoint"""

    # Logout with valid access token
    good_response = client.delete(
        "/admins/logout", headers={"Authorization": ACCESS_TOKEN}
    )

    # Check valid response
    assert good_response.status_code == 200
    good_response_data = good_response.json()
    assert good_response_data["status"] == "success"
    assert good_response_data["data"]["message"] == "Admin has been logged out"

    # Try to use the same access token after logout
    invalid_response = client.delete(
        "/admins/logout", headers={"Authorization": faker.sha256()}
    )

    # Check invalid response
    assert invalid_response.status_code == 401
    invalid_response_data = invalid_response.json()
    assert invalid_response_data["status"] == "error"
    assert invalid_response_data["data"]["message"] == "Invalid token"


def test_admin_configurations():
    """This test is for the admin configurations endpoint"""

    # Successful request with valid token
    good_response = client.get(
        "/admins/configurations", headers={"Authorization": ACCESS_TOKEN}
    )

    # Unauthorized request (invalid token provided)
    bad_response = client.get(
        "/admins/configurations", headers={"Authorization": "Bearer INVALID_TOKEN"}
    )

    # Check successful response
    assert good_response.status_code == 200
    good_response_data = good_response.json()
    assert good_response_data["status"] == "success"
    assert "data" in good_response_data

    config_data = good_response_data["data"]

    assert config_data["id"] is not None
    assert isinstance(config_data["notification_email"], bool)
    assert isinstance(config_data["notification_inapp"], bool)

    # Check unauthorized access response
    assert bad_response.status_code == 401
    bad_response_data = bad_response.json()
    assert bad_response_data["status"] == "error"
    assert "data" in bad_response_data
    assert bad_response_data["data"]["message"] == "Invalid Token"


def test_admin_configurations_edit():
    """This test is for the admin configurations edit endpoint"""

    # New configurations data
    new_configurations = {
        "notification_email": False,
        "notification_inapp": True,
    }

    # Successful request with valid token
    good_response = client.put(
        "/admins/configurations",
        headers={"Authorization": ACCESS_TOKEN},
        json=new_configurations,
    )

    # Unauthorized request (invalid token provided)
    bad_response = client.put(
        "/admins/configurations",
        headers={"Authorization": faker.sha256()},
        json=new_configurations,
    )

    # Check successful response
    assert good_response.status_code == 200
    good_response_data = good_response.json()
    assert good_response_data["status"] == "success"
    assert "data" in good_response_data

    config_data = good_response_data["data"]

    assert config_data["id"] is not None
    assert config_data["notification_email"] == new_configurations["notification_email"]
    assert config_data["notification_inapp"] == new_configurations["notification_inapp"]

    # Check unauthorized access response
    assert bad_response.status_code == 401
    bad_response_data = bad_response.json()
    assert bad_response_data["status"] == "error"
    assert "data" in bad_response_data
    assert bad_response_data["data"]["message"] == "Invalid token"
