import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Should return all activities in the database"""
        # Arrange
        expected_activity_count = 9
        expected_activities = ["Chess Club", "Programming Class", "Basketball Club"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        for activity_name in expected_activities:
            assert activity_name in data
    
    def test_activities_have_required_fields(self):
        """Each activity should have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant_to_activity(self):
        """Should successfully add a participant to an activity"""
        # Arrange
        activity_name = "Chess%20Club"
        email = "newstudent@mergington.edu"
        expected_message_part = "Signed up"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert expected_message_part in data["message"]
        assert email in data["message"]
    
    def test_signup_duplicate_participant_fails(self):
        """Should prevent duplicate sign-ups"""
        # Arrange
        activity_name = "Programming%20Class"
        email = "duplicate_test@mergington.edu"
        expected_error_message = "already signed up"
        
        # Act - First signup
        first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Act - Second signup (duplicate)
        second_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert expected_error_message in second_response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Should return 404 for non-existent activities"""
        # Arrange
        activity_name = "Nonexistent%20Club"
        email = "test@mergington.edu"
        expected_status_code = 404
        expected_error = "Activity not found"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        data = response.json()
        
        # Assert
        assert response.status_code == expected_status_code
        assert expected_error in data["detail"]
    
    def test_signup_empty_email_fails(self):
        """Should handle missing email parameter"""
        # Arrange
        activity_name = "Tennis%20Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self):
        """GET / should redirect to /static/index.html"""
        # Arrange
        expected_status_code = 307
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status_code
        assert expected_redirect_path in response.headers["location"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
