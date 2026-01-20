"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store initial state
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "instructor": "Mr. Chen",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice sessions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "instructor": "Coach Martinez",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "instructor": "Coach Williams",
            "max_participants": 10,
            "participants": ["alex@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and theatrical productions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "instructor": "Ms. Rodriguez",
            "max_participants": 25,
            "participants": ["sophie@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, sculpture, and digital art",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "instructor": "Mr. Thompson",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "instructor": "Ms. Garcia",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM topics",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "instructor": "Dr. Patel",
            "max_participants": 18,
            "participants": ["olivia@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(initial_activities)
    yield
    # Reset after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Basketball Team" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert "schedule" in chess_club
        assert "description" in chess_club or "instructor" in chess_club

    def test_get_activities_participants_list_is_valid(self, client):
        """Test that participants list is a list of strings"""
        response = client.get("/activities")
        data = response.json()
        for activity in data.values():
            assert isinstance(activity["participants"], list)
            for participant in activity["participants"]:
                assert isinstance(participant, str)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_new_participant_actually_added(self, client):
        """Test that signup actually adds participant to activity"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up a duplicate participant fails"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_with_empty_email_fails(self, client):
        """Test that signup with empty email is handled"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        # Should succeed but the email would be empty
        assert response.status_code == 200

    def test_signup_multiple_different_participants(self, client):
        """Test signing up multiple different participants"""
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "student1@mergington.edu" in data["Chess Club"]["participants"]
        assert "student2@mergington.edu" in data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_actually_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_multiple_participants(self, client):
        """Test unregistering multiple participants from same activity"""
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "daniel@mergington.edu"}
        )
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 0


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
