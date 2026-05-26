import re

import pytest
from playwright.sync_api import expect


@pytest.mark.ui
def test_admin_login(logged_in_page):
    """Log in as admin and verify we reach the Dashboard."""

    # The logged_in_page fixture handles navigation and credential entry.
    # We just need to verify the Dashboard loaded successfully.
    expect(logged_in_page).to_have_title(re.compile(r"Dashboard"))
