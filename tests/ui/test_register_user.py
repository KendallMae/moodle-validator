import re
import time

import pytest
from playwright.sync_api import expect

TEST_USERNAME = "testuser_" + str(int(time.time()))
TEST_PASSWORD = "TestPass123!"
TEST_FIRSTNAME = "Test"
TEST_LASTNAME = "Validator"
TEST_EMAIL = f"{TEST_USERNAME}@example.com"


@pytest.mark.ui
def test_register_user(page, base_url, admin_credentials):
    """Create a new user as admin and verify they appear in the user list."""

    # Log in as admin
    page.goto(f"{base_url}/login/index.php", wait_until="networkidle")
    page.locator("#username").click()
    page.locator("#username").type(admin_credentials["username"])
    page.locator("#password").click()
    page.locator("#password").type(admin_credentials["password"])
    page.locator("#loginbtn").click()
    page.wait_for_load_state("networkidle")

    # Navigate to the "Add a new user" page
    page.goto(f"{base_url}/user/editadvanced.php?id=-1", wait_until="networkidle")

    # Fill in required fields
    page.locator("#id_username").click()
    page.locator("#id_username").fill(TEST_USERNAME)

    # Reveal the password field by toggling the "Generate password" checkbox
    # and removing the d-none class that Moodle uses to hide it
    page.locator("#id_createpassword").click()
    page.wait_for_timeout(500)
    page.locator("#id_createpassword").click()
    page.wait_for_timeout(500)

    # Force the field visible via JS in case the checkbox toggle didn't work
    page.evaluate("document.getElementById('id_newpassword').classList.remove('d-none')")
    page.locator("#id_newpassword").fill(TEST_PASSWORD)

    page.locator("#id_firstname").click()
    page.locator("#id_firstname").fill(TEST_FIRSTNAME)

    page.locator("#id_lastname").click()
    page.locator("#id_lastname").fill(TEST_LASTNAME)

    page.locator("#id_email").click()
    page.locator("#id_email").fill(TEST_EMAIL)

    # Submit the form
    page.locator("#id_submitbutton").click()
    page.wait_for_load_state("networkidle")

    # Navigate to the user browse page and search for our user
    page.goto(
        f"{base_url}/admin/user.php?s={TEST_USERNAME}", wait_until="networkidle"
    )

    # Verify the new user appears in the results
    expect(page.locator("table.generaltable")).to_contain_text(TEST_FIRSTNAME)
    expect(page.locator("table.generaltable")).to_contain_text(TEST_LASTNAME)
