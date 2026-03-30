"""
Unit tests for Email Service API.
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
    
    def test_basic_auth_missing(self):
        """Test endpoint that requires auth without providing it."""
        response = client.get("/status")
        assert response.status_code == 401  # HTTPBasic returns 401 on missing auth
    
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
    
    def test_invalid_email_format(self):
        """Test with invalid email format."""
        payload = {
            "to": ["not-an-email"],
            "subject": "Test",
            "body": "Test"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_field(self):
        """Test with missing required field."""
        payload = {
            "to": ["test@example.com"],
            # Missing subject
            "body": "Test"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code == 422
    
    def test_empty_to_list(self):
        """Test with empty recipient list."""
        payload = {
            "to": [],
            "subject": "Test",
            "body": "Test"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        # FastAPI will reject empty list for required field
        assert response.status_code == 422
    
    def test_subject_too_long(self):
        """Test with subject exceeding max length."""
        payload = {
            "to": ["test@example.com"],
            "subject": "x" * 300,  # Max is 255
            "body": "Test"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code == 422
    
    def test_empty_body(self):
        """Test with empty body."""
        payload = {
            "to": ["test@example.com"],
            "subject": "Test",
            "body": ""
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code == 422


class TestEmailSending:
    """Test email sending functionality."""
    
    @patch('email_sender.SMTPEmailSender.send_email')
    async def test_send_email_success(self, mock_send):
        """Test successful email sending."""
        # Mock the SMTP send
        mock_send.return_value = {
            "success": True,
            "message": "Email sent successfully",
            "message_id": "test-id-123",
            "timestamp": "2026-03-16T10:00:00"
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
        assert "message_id" in response.json()
    
    @patch('email_sender.SMTPEmailSender.send_email')
    async def test_send_email_failure(self, mock_send):
        """Test email sending failure."""
        mock_send.return_value = {
            "success": False,
            "message": "SMTP authentication failed",
            "timestamp": "2026-03-16T10:00:00"
        }
        
        payload = {
            "to": ["recipient@example.com"],
            "subject": "Test Email",
            "body": "Test body"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        
        assert response.status_code == 500
    
    def test_multiple_recipients(self):
        """Test sending to multiple recipients."""
        payload = {
            "to": ["user1@example.com", "user2@example.com", "user3@example.com"],
            "subject": "Broadcast Email",
            "body": "Hello everyone!"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        # Validation should pass
        assert response.status_code in [200, 500]
    
    def test_with_cc_and_bcc(self):
        """Test email with CC and BCC."""
        payload = {
            "to": ["recipient@example.com"],
            "cc": ["cc@example.com"],
            "bcc": ["bcc@example.com"],
            "subject": "Email with CC/BCC",
            "body": "Test"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code in [200, 500]
    
    def test_html_vs_plain_text(self):
        """Test both HTML and plain text modes."""
        # HTML mode
        payload_html = {
            "to": ["test@example.com"],
            "subject": "HTML Email",
            "body": "<h1>Hello</h1>",
            "is_html": True
        }
        response = client.post(
            "/send-email",
            json=payload_html,
            auth=BASIC_AUTH
        )
        assert response.status_code in [200, 500]
        
        # Plain text mode
        payload_text = {
            "to": ["test@example.com"],
            "subject": "Plain Text Email",
            "body": "Hello World",
            "is_html": False
        }
        response = client.post(
            "/send-email",
            json=payload_text,
            auth=BASIC_AUTH
        )
        assert response.status_code in [200, 500]


class TestResponseFormat:
    """Test response formatting."""
    
    def test_error_response_format(self):
        """Test that error responses have correct format."""
        response = client.get("/status", auth=("wrong", "user"))
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "status_code" in data
        assert "timestamp" in data


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_special_characters_in_body(self):
        """Test email with special characters."""
        payload = {
            "to": ["test@example.com"],
            "subject": "Special: © ® ™ € £",
            "body": "Body with émojis 🎉 and special chars: <>&\"'"
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        assert response.status_code in [200, 400, 422, 500]
    
    def test_very_long_body(self):
        """Test email with very long body."""
        payload = {
            "to": ["test@example.com"],
            "subject": "Long Email",
            "body": "x" * 100000  # 100KB body
        }
        response = client.post(
            "/send-email",
            json=payload,
            auth=BASIC_AUTH
        )
        # Should be accepted (size validation not strict)
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
