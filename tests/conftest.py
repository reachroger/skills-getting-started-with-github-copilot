"""
Shared test fixtures and configuration for FastAPI tests using AAA (Arrange-Act-Assert) pattern.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    Returns a fresh client for each test.
    """
    return TestClient(app)


@pytest.fixture
def clean_activities(monkeypatch):
    """
    Fixture that provides clean activities data for isolated test execution.
    Monkeypatches the app's activities dict to prevent test state pollution.
    """
    clean_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["alice@mergington.edu", "bob@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 2,
            "participants": ["charlie@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and tournament play",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 2,
            "participants": []
        }
    }
    
    # Import app module to patch its activities
    import app as app_module
    monkeypatch.setattr(app_module, "activities", clean_data)
    
    return clean_data
