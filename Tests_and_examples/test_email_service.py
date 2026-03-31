"""
Unit tests for Email & SMS Service API.
Run with: pytest test_email_service.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

# Create test client
client = TestClient(app)

# Test fixtures
BASIC_AUTH = ("admin", "changeme")
BEARER_TOKEN = "your-api-token-here"


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check_no_auth(self):
        """Health check should work without authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Root endpoint should return service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestAuthentication:
    """Test authentication mechanisms."""
    
    def test_basic_auth_success(self):
        """Test successful basic authentication."""
        response = client.get("/status", auth=BASIC_AUTH)
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_basic_auth_invalid_credentials(self):
        """Test basic auth with invalid credentials."""
        response = client.get("/status", auth=("wrong", "credentials"))
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_bearer_token_success(self):
        """Test successful bearer token authentication."""
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
        response = client.post(
            "/send-email/token",
            headers=headers,
            json={
                "to": ["test@example.com"],
                "subject": "Test",
                "body": "Test"
            }
        )
        # Mock will fail, but auth should pass
        assert response.status_code != 401
    
    def test_bearer_token_invalid(self):
        """Test bearer token with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post(
            "/send-email/token",
            headers=headers,
            json={
                "to": ["test@example.com"],
                "subject": "Test",
                "body": "Test"
            }
        )
        assert response.status_code == 401


class TestEmailValidation:
    """Test request validation."""
    
    def test_valid_email_request(self):
        """Test request with valid data."""
        payload = {
            "to": ["valid@example.com"],
            "subject": "Test Subject",
            "body": "<h1>Test</h1>",
            "is_html": True
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        # Should not fail validation (may fail SMTP)
        assert response.status_code in [200, 500]
    
    def test_both_to_and_owner(self):
        """Test validation fails when both 'to' and 'owner' are provided."""
        payload = {
            "to": ["test@example.com"],
            "owner": "admin_team",
            "subject": "Test",
            "body": "Test"
        }
        response = client.post("/send-email", json=payload, auth=BASIC_AUTH)
        assert response.status_code == 422
        
    def test_neither_to_nor_owner(self):
        """Test validation fails when neither 'to' nor 'owner' is provided."""
        payload = {
            "subject": "Test",
            "body": "Test"
        }
        response = client.post("/send-email", json=payload, auth=BASIC_AUTH)
        assert response.status_code == 422


class TestEmailSending:
    """Test email sending functionality."""
    
    @patch('email_sender.SMTPEmailSender.send_email', new_callable=AsyncMock)
    def test_send_email_success(self, mock_send):
        """Test successful email sending."""
        mock_send.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "message_id": "test-id-123",
            "timestamp": "2026-03-31T10:00:00"
        }
        
        payload = {
            "to": ["recipient@example.com"],
            "subject": "Test Email",
            "body": "Test body",
            "is_html": False
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_send.assert_called_once()
        

class TestSmsSending:
    """Test SMS sending functionality."""
    
    @patch('sms_sender.SmsSender.send_sms', new_callable=AsyncMock)
    def test_send_sms_success(self, mock_send):
        """Test successful SMS sending."""
        mock_send.return_value = {
            "success": True,
            "message": "SMS sent successfully",
            "message_id": "sms-id-123",
            "timestamp": "2026-03-31T10:00:00"
        }
        
        payload = {
            "recipient": "0501234567",
            "text": "Hello text",
            "recipient_type": 0
        }
        response = client.post(
            "/send-sms",
            json=payload,
            auth=BASIC_AUTH
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_send.assert_called_once()
    
    def test_sms_validation_both_recipient_and_owner(self):
        """Test validation fails when both 'recipient' and 'owner' are provided."""
        payload = {
            "recipient": "0501234567",
            "owner": "admin_team",
            "text": "Hello text"
        }
        response = client.post("/send-sms", json=payload, auth=BASIC_AUTH)
        assert response.status_code == 422
        
    def test_sms_validation_neither(self):
        """Test validation fails when neither 'recipient' nor 'owner' is provided."""
        payload = {
            "text": "Hello text"
        }
        response = client.post("/send-sms", json=payload, auth=BASIC_AUTH)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
