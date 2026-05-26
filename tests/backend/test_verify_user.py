import pytest
import requests


@pytest.mark.backend
def test_verify_user_via_api(base_url, api_token, db_connection):
    """Verify a test user exists by querying the Moodle REST API directly."""

    # Look up the user ID from the database first
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute("SELECT id FROM mdl_user WHERE lastname = 'Validator' LIMIT 1")
    row = cursor.fetchone()
    cursor.close()

    assert row is not None, "No test user found in DB -- run UI register test first"

    # Use core_user_get_users_by_field (available in the mobile service)
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
def test_verify_user_via_db(db_connection):
    """Verify a test user exists by querying the database directly."""

    # Query mdl_user for the test user created by the UI test
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, firstname, lastname, email "
        "FROM mdl_user WHERE lastname = 'Validator'"
    )
    users = cursor.fetchall()
    cursor.close()

    assert len(users) > 0, "No user with lastname 'Validator' found in mdl_user"
    assert users[0]["firstname"] == "Test"
    assert "testuser_" in users[0]["username"]
