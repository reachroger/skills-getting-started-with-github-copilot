"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for POST /signup endpoint"""

    def test_signup_new_participant_returns_success(self, client, clean_activities):
        """
        ARRANGE: Basketball Team exists with no participants
        ACT: Sign up new participant
        ASSERT: Response is 200 with success message
        """
        # Arrange
        activity = "Basketball Team"
        email = "diana@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"

    def test_signup_new_participant_adds_to_activity(self, client, clean_activities):
        """
        ARRANGE: Basketball Team has 0 participants
        ACT: Sign up participant, then fetch activities
        ASSERT: Participant appears in activity's participant list
        """
        # Arrange
        activity = "Basketball Team"
        email = "diana@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == 1

    def test_signup_duplicate_participant_returns_error(self, client, clean_activities):
        """
        ARRANGE: Alice is already signed up for Chess Club
        ACT: Try to sign up Alice again for Chess Club
        ASSERT: Response is 400 with error message
        """
        # Arrange
        activity = "Chess Club"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_error(self, client, clean_activities):
        """
        ARRANGE: "Nonexistent Activity" does not exist
        ACT: Try to sign up for nonexistent activity
        ASSERT: Response is 404 with activity not found error
        """
        # Arrange
        activity = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_at_max_capacity_returns_error(self, client, clean_activities):
        """
        ARRANGE: Chess Club has max_participants=3 and 2 participants already
        ACT: Sign up 1 more participant to reach capacity, then try to sign up another
        ASSERT: Third signup succeeds, fourth signup fails with 409 Conflict
        """
        # Arrange
        activity = "Chess Club"
        third_participant = "diana@mergington.edu"
        fourth_participant = "evan@mergington.edu"

        # Act - sign up third participant (should succeed)
        response_third = client.post(
            f"/activities/{activity}/signup",
            params={"email": third_participant}
        )

        # Act - sign up fourth participant (should fail)
        response_fourth = client.post(
            f"/activities/{activity}/signup",
            params={"email": fourth_participant}
        )

        # Assert
        assert response_third.status_code == 200
        assert response_fourth.status_code == 409
        assert "maximum capacity" in response_fourth.json()["detail"]

    def test_signup_does_not_affect_other_activities(self, client, clean_activities):
        """
        ARRANGE: Multiple activities exist with different participants
        ACT: Sign up for Basketball Team
        ASSERT: Other activities remain unchanged
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_chess_participants = initial_response.json()["Chess Club"]["participants"].copy()

        # Act
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "diana@mergington.edu"}
        )

        # Act - fetch activities again
        updated_response = client.get("/activities")
        updated_chess_participants = updated_response.json()["Chess Club"]["participants"]

        # Assert
        assert updated_chess_participants == initial_chess_participants

    def test_signup_multiple_participants_to_same_activity(self, client, clean_activities):
        """
        ARRANGE: Basketball Team is empty
        ACT: Sign up two different participants sequentially
        ASSERT: Both participants are in the activity
        """
        # Arrange
        activity = "Basketball Team"
        email1 = "diana@mergington.edu"
        email2 = "evan@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email1})
        client.post(f"/activities/{activity}/signup", params={"email": email2})

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 in participants
        assert email2 in participants
        assert len(participants) == 2
