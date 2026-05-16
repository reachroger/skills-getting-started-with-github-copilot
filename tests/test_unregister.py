"""
Tests for POST /activities/{activity_name}/unregister endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for POST /unregister endpoint"""

    def test_unregister_participant_returns_success(self, client, clean_activities):
        """
        ARRANGE: Alice is signed up for Chess Club
        ACT: Unregister Alice from Chess Club
        ASSERT: Response is 200 with success message
        """
        # Arrange
        activity = "Chess Club"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"

    def test_unregister_participant_removes_from_activity(self, client, clean_activities):
        """
        ARRANGE: Alice and Bob are signed up for Chess Club
        ACT: Unregister Alice, then fetch activities
        ASSERT: Alice is removed from participants, Bob remains
        """
        # Arrange
        activity = "Chess Club"
        email_to_remove = "alice@mergington.edu"
        email_remaining = "bob@mergington.edu"

        # Act
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": email_to_remove}
        )
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]

        # Assert
        assert email_to_remove not in participants
        assert email_remaining in participants
        assert len(participants) == 1

    def test_unregister_participant_not_signed_up_returns_error(self, client, clean_activities):
        """
        ARRANGE: Charlie is not signed up for Chess Club
        ACT: Try to unregister Charlie from Chess Club
        ASSERT: Response is 400 with error message
        """
        # Arrange
        activity = "Chess Club"
        email = "charlie@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_error(self, client, clean_activities):
        """
        ARRANGE: "Nonexistent Activity" does not exist
        ACT: Try to unregister from nonexistent activity
        ASSERT: Response is 404 with activity not found error
        """
        # Arrange
        activity = "Nonexistent Activity"
        email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_frees_up_capacity(self, client, clean_activities):
        """
        ARRANGE: Chess Club is at max capacity (3/3)
        ACT: Unregister one participant, then sign up new participant
        ASSERT: New signup succeeds after unregister freed up space
        """
        # Arrange
        activity = "Chess Club"
        participant_to_remove = "alice@mergington.edu"
        new_participant = "evan@mergington.edu"

        # First, fill the activity to capacity
        client.post(
            f"/activities/{activity}/signup",
            params={"email": "diana@mergington.edu"}
        )

        # Act - unregister someone
        client.post(
            f"/activities/{activity}/unregister",
            params={"email": participant_to_remove}
        )

        # Act - sign up new participant (should succeed now)
        new_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": new_participant}
        )

        # Assert
        assert new_response.status_code == 200

    def test_unregister_does_not_affect_other_activities(self, client, clean_activities):
        """
        ARRANGE: Multiple activities with different participants
        ACT: Unregister from Chess Club
        ASSERT: Other activities remain unchanged
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_prog_participants = initial_response.json()["Programming Class"]["participants"].copy()

        # Act
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": "alice@mergington.edu"}
        )

        # Act - fetch activities again
        updated_response = client.get("/activities")
        updated_prog_participants = updated_response.json()["Programming Class"]["participants"]

        # Assert
        assert updated_prog_participants == initial_prog_participants

    def test_unregister_multiple_participants_sequentially(self, client, clean_activities):
        """
        ARRANGE: Chess Club has 2 participants
        ACT: Unregister both participants sequentially
        ASSERT: Chess Club ends up with no participants
        """
        # Arrange
        activity = "Chess Club"
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/unregister", params={"email": email1})
        client.post(f"/activities/{activity}/unregister", params={"email": email2})

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert len(participants) == 0

    def test_unregister_participant_twice_returns_error(self, client, clean_activities):
        """
        ARRANGE: Alice is signed up for Chess Club
        ACT: Unregister Alice twice
        ASSERT: First unregister succeeds (200), second unregister fails (400)
        """
        # Arrange
        activity = "Chess Club"
        email = "alice@mergington.edu"

        # Act - first unregister
        response_first = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Act - second unregister
        response_second = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response_first.status_code == 200
        assert response_second.status_code == 400
        assert "not signed up" in response_second.json()["detail"]
