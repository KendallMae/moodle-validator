import time
import pytest
import requests
import mysql.connector


MOODLE_BASE_URL = "http://localhost:8080"
ADMIN_USERNAME = "user"
ADMIN_PASSWORD = "AdminPass123!"

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "database": "moodle",
    "user": "moodleuser",
    "password": "moodlepass",
}


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the local Moodle instance."""
    return MOODLE_BASE_URL


@pytest.fixture(scope="session")
def admin_credentials():
    """Admin username and password as a dict."""
    return {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}


@pytest.fixture(scope="session", autouse=True)
def moodle_ready(base_url):
    """Block until Moodle's login page responds with HTTP 200.

    Polls every 5 seconds for up to 5 minutes. This handles the slow
    first-boot initialization of the Bitnami Moodle container.
    """
    login_url = f"{base_url}/login/index.php"
    timeout = 300
    interval = 5
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            resp = requests.get(login_url, timeout=10)
            if resp.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(interval)

    pytest.fail(f"Moodle did not become ready at {login_url} within {timeout}s")


@pytest.fixture(scope="session")
def db_connection():
    """Session-scoped MariaDB connection to the Moodle database."""
    conn = mysql.connector.connect(**DB_CONFIG)
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def enable_web_services(db_connection):
    """Enable Moodle web services and the REST protocol via direct DB update.

    This is required before any REST API calls will work. It runs once
    per test session and is equivalent to toggling these settings in
    Site Administration > Web services.
    """
    cursor = db_connection.cursor()
    cursor.execute(
        "UPDATE mdl_config SET value='1' WHERE name='enablewebservices'"
    )
    cursor.execute(
        "UPDATE mdl_config SET value='rest' WHERE name='webserviceprotocols'"
    )
    db_connection.commit()
    cursor.close()


@pytest.fixture(scope="session")
def api_token(base_url, admin_credentials):
    """Obtain a REST API token from Moodle's token endpoint.

    Uses the built-in 'moodle_mobile_app' service which is available
    once web services are enabled.
    """
    token_url = (
        f"{base_url}/login/token.php"
        f"?username={admin_credentials['username']}"
        f"&password={admin_credentials['password']}"
        f"&service=moodle_mobile_app"
    )
    resp = requests.get(token_url)
    data = resp.json()

    assert "token" in data, f"Failed to get token: {data}"
    return data["token"]
