import re

import pytest
from playwright.sync_api import expect


@pytest.mark.ui
def test_admin_login(page, base_url, admin_credentials):
    """Log in as admin and verify we reach the Dashboard."""

    # Navigate to the Moodle login page and wait for it to fully load
    page.goto(f"{base_url}/login/index.php", wait_until="networkidle")

    page.locator("#username").click()
    page.locator("#username").type(admin_credentials["username"])

    page.locator("#password").click()
    page.locator("#password").type(admin_credentials["password"])

    page.locator("#loginbtn").click()

    # Wait for navigation to complete after login
    page.wait_for_load_state("networkidle")

    # Verify we landed on the Dashboard
    expect(page).to_have_title(re.compile(r"Dashboard"))
