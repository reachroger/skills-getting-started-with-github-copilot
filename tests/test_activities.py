"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client, clean_activities):
        """
        ARRANGE: Client is ready with clean activities data
        ACT: Send GET request to /activities
        ASSERT: Response code is 200 and returns all activities
        """
        # Arrange - already done by fixtures

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) == 3

    def test_get_activities_returns_correct_structure(self, client, clean_activities):
        """
        ARRANGE: Client is ready
        ACT: Fetch activities
        ASSERT: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange - already done by fixtures

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_all_activity_names(self, client, clean_activities):
        """
        ARRANGE: Clean activities with 3 known activities
        ACT: Fetch all activities
        ASSERT: All expected activity names are present
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_shows_correct_participant_list(self, client, clean_activities):
        """
        ARRANGE: Chess Club has 2 participants: alice@mergington.edu, bob@mergington.edu
        ACT: Fetch activities
        ASSERT: Chess Club participants list matches expected participants
        """
        # Arrange
        expected_participants = ["alice@mergington.edu", "bob@mergington.edu"]

        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]

        # Assert
        assert chess_club["participants"] == expected_participants

    def test_get_activities_shows_empty_participant_list(self, client, clean_activities):
        """
        ARRANGE: Basketball Team has no participants
        ACT: Fetch activities
        ASSERT: Basketball Team participants list is empty
        """
        # Arrange - already done by fixtures (Basketball Team has no participants)

        # Act
        response = client.get("/activities")
        activities = response.json()
        basketball = activities["Basketball Team"]

        # Assert
        assert basketball["participants"] == []
        assert len(basketball["participants"]) == 0
