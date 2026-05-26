import pytest
import requests


@pytest.mark.backend
def test_verify_course_via_api(base_url, api_token):
    """Verify a course exists by querying the Moodle REST API directly."""

    # Call the core_course_get_courses web service function
    resp = requests.post(
        f"{base_url}/webservice/rest/server.php",
        data={
            "wstoken": api_token,
            "wsfunction": "core_course_get_courses",
            "moodlewsrestformat": "json",
        },
    )
    assert resp.status_code == 200

    courses = resp.json()
    assert isinstance(courses, list), f"Unexpected response: {courses}"

    # Filter out the default "Site" course (id=1) and check at least one real course exists
    real_courses = [c for c in courses if c["id"] != 1]
    assert len(real_courses) > 0, "No courses found besides the default site course"


@pytest.mark.backend
def test_verify_course_via_db(db_connection):
    """Verify a course exists by querying the database directly."""

    # Query the mdl_course table, skipping the default site course (id=1)
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, fullname, shortname FROM mdl_course WHERE id != 1"
    )
    courses = cursor.fetchall()
    cursor.close()

    assert len(courses) > 0, "No courses found in mdl_course table"
    assert courses[0]["fullname"] is not None
    assert courses[0]["shortname"] is not None
