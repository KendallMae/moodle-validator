import time
import subprocess
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
    """Block until Moodle responds to HTTP requests.

    Polls every 5 seconds for up to 5 minutes. This handles the slow
    first-boot initialization of the Bitnami Moodle container.
    """
    url = f"{base_url}/"
    timeout = 300
    interval = 5
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=10, allow_redirects=True)
            if resp.status_code in (200, 303):
                return
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(interval)

    pytest.fail(f"Moodle did not become ready at {url} within {timeout}s")


@pytest.fixture(scope="session")
def db_connection():
    """Session-scoped MariaDB connection to the Moodle database."""
    conn = mysql.connector.connect(**DB_CONFIG)
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def enable_web_services(moodle_ready):
    """Enable Moodle web services and the REST protocol via Moodle's CLI.

    Uses the cfg.php CLI tool which properly handles config changes and
    cache invalidation without corrupting Moodle's internal state.
    """
    subprocess.run(
        ["docker", "compose", "exec", "-T", "moodle",
         "php", "/opt/bitnami/moodle/admin/cli/cfg.php",
         "--name=enablewebservices", "--set=1"],
        capture_output=True,
        timeout=30,
    )
    subprocess.run(
        ["docker", "compose", "exec", "-T", "moodle",
         "php", "/opt/bitnami/moodle/admin/cli/cfg.php",
         "--name=webserviceprotocols", "--set=rest"],
        capture_output=True,
        timeout=30,
    )
    # Enable the moodle_mobile_app external service via Moodle's DB API
    subprocess.run(
        ["docker", "compose", "exec", "-T", "moodle",
         "php", "-r",
         "define('CLI_SCRIPT', true); "
         "require('/opt/bitnami/moodle/config.php'); "
         "$DB->set_field('external_services', 'enabled', 1, "
         "['shortname' => 'moodle_mobile_app']);"],
        capture_output=True,
        timeout=30,
    )


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
