import re

import pytest
import requests


@pytest.mark.backend
def test_get_auth_token(base_url, admin_credentials):
    """Obtain a REST API token and validate its format."""

    token_url = (
        f"{base_url}/login/token.php"
        f"?username={admin_credentials['username']}"
        f"&password={admin_credentials['password']}"
        f"&service=moodle_mobile_app"
    )

    resp = requests.get(token_url)
    assert resp.status_code == 200

    data = resp.json()

    # Should contain a 'token' key with no error
    assert "error" not in data, f"Token request returned error: {data}"
    assert "token" in data, f"No token in response: {data}"

    # Moodle tokens are 32-character hex strings
    token = data["token"]
    assert re.match(r"^[a-f0-9]{32}$", token), f"Token format invalid: {token}"
