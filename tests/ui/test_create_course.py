import re
import time

import pytest
from playwright.sync_api import expect

COURSE_FULL_NAME = "Test Course Validator"
COURSE_SHORT_NAME = "tcv_" + str(int(time.time()))


@pytest.mark.ui
def test_create_course(page, base_url, admin_credentials):
    """Create a new course as admin and verify it appears in the course listing."""

    # Log in as admin
    page.goto(f"{base_url}/login/index.php", wait_until="networkidle")
    page.locator("#username").click()
    page.locator("#username").type(admin_credentials["username"])
    page.locator("#password").click()
    page.locator("#password").type(admin_credentials["password"])
    page.locator("#loginbtn").click()
    page.wait_for_load_state("networkidle")

    # Navigate directly to the "Add a new course" page
    page.goto(f"{base_url}/course/edit.php?category=1", wait_until="networkidle")

    # Fill in the course full name and short name
    page.locator("#id_fullname").click()
    page.locator("#id_fullname").fill(COURSE_FULL_NAME)

    page.locator("#id_shortname").click()
    page.locator("#id_shortname").fill(COURSE_SHORT_NAME)

    # Submit the form (Save and display)
    page.locator("#id_saveanddisplay").click()
    page.wait_for_load_state("networkidle")

    # Verify the course page loaded with our course name in the title
    expect(page).to_have_title(re.compile(re.escape(COURSE_FULL_NAME)))
