import random
from fastapi.testclient import TestClient
from faker import Faker
import pytest

from app.user import models, security, services
from app.main import app
from app.common.dependencies import get_db
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
    "password":"admin",
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
    assert response_data["data"]["exception_alert_email"] == good_user["exception_alert_email"]
    assert response_data["data"]["is_active"] is True
    assert response_data["data"]["is_verified"] is False

    # Check if the user is already registered
    assert registered_user.status_code == 400
    registered_user = registered_user.json()
    assert registered_user.get("data", {}).get("message") == f"user with email {good_user['email']} exists"

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
    assert bad_response.get('data', {}).get('message') == "Invalid login credentials"
    # Check valid credentials
    response_data = good_response.json()

    response_data = good_response.json()
    assert "data" in response_data
    assert response_data["data"]["user"]["id"] is not None
    assert response_data["data"]["user"]["full_name"] == USER["full_name"]
    assert response_data["data"]["user"]["email"] == USER["email"]
    assert response_data["data"]["user"]["exception_alert_email"] == USER["exception_alert_email"]
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
    assert bad_response.get('data', {}).get('message') == "No data to update"

    
    # Check good 
    response_data = good_response.json()

    assert good_response.status_code == 200
    assert response_data["data"]["id"] is not None
    assert response_data["data"]["full_name"] == new_user["full_name"]
    assert response_data["data"]["email"] == USER["email"]
    assert response_data["data"]["exception_alert_email"] == USER["exception_alert_email"]
    assert response_data["data"]["is_active"] is True
    assert response_data["data"]["is_verified"] is False

    # check for bad_user
    assert bad_user.status_code == 401
    bad_user = bad_user.json()  
    assert bad_user.get('data', {}).get('message') == "Invalid token"
