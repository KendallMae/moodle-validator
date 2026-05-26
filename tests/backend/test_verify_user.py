import pytest
import requests
import mysql.connector


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "moodle",
    "user": "moodleuser",
    "password": "moodlepass",
}


@pytest.mark.backend
def test_verify_user_via_api(base_url, api_token):
    """Verify a test user exists by querying the Moodle REST API directly."""

    # First get all user IDs > 2 from DB (skip guest and admin)
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM mdl_user WHERE lastname = 'Validator' LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    assert row is not None, "No test user found in DB -- run UI register test first"

    # Use core_user_get_users_by_field (available in mobile service)
    resp = requests.post(
        f"{base_url}/webservice/rest/server.php",
        data={
            "wstoken": api_token,
            "wsfunction": "core_user_get_users_by_field",
            "moodlewsrestformat": "json",
            "field": "id",
            "values[0]": row["id"],
        },
    )
    assert resp.status_code == 200

    users = resp.json()
    assert isinstance(users, list), f"Unexpected response: {users}"
    assert len(users) > 0, "User not found via API"
    assert users[0]["firstname"] == "Test"
    assert users[0]["lastname"] == "Validator"


@pytest.mark.backend
def test_verify_user_via_db():
    """Verify a test user exists by querying the database directly."""

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username, firstname, lastname, email "
        "FROM mdl_user WHERE lastname = 'Validator'"
    )
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    assert len(users) > 0, "No user with lastname 'Validator' found in mdl_user"
    assert users[0]["firstname"] == "Test"
    assert "testuser_" in users[0]["username"]
