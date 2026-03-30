"""
Example usage of the Email Service API.
This file shows different ways to interact with the email service.
"""

import requests
from requests.auth import HTTPBasicAuth
import asyncio
from typing import List

# Configuration
BASE_URL = "http://localhost:8000"
BASIC_AUTH_USER = "admin"
BASIC_AUTH_PASS = "changeme"
API_TOKEN = "your-api-token-here"

# ============================================================================
# Example 1: Send email with Basic Authentication
# ============================================================================

def example_basic_auth_email():
    """Send email using HTTP Basic Authentication."""
    print("\n" + "="*70)
    print("Example 1: Send Email with Basic Auth")
    print("="*70)
    
    payload = {
        "to": ["recipient@example.com"],
        "subject": "Hello from Email Service",
        "body": "<h1>Welcome</h1><p>This is your first email from the service!</p>",
        "is_html": True,
        "cc": ["cc@example.com"],
        "bcc": None
    }
    
    response = requests.post(
        f"{BASE_URL}/send-email",
        json=payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Example 2: Send email with Bearer Token (OAuth/API Key)
# ============================================================================

def example_bearer_token_email():
    """Send email using Bearer Token authentication."""
    print("\n" + "="*70)
    print("Example 2: Send Email with Bearer Token")
    print("="*70)
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    payload = {
        "to": ["another@example.com"],
        "subject": "API Token Authentication Test",
        "body": "This email was sent using Bearer token authentication.",
        "is_html": False
    }
    
    response = requests.post(
        f"{BASE_URL}/send-email/token",
        json=payload,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Example 3: Get service status
# ============================================================================

def example_get_status():
    """Get service status with authentication."""
    print("\n" + "="*70)
    print("Example 3: Get Service Status")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/status",
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Example 4: Health check (no auth required)
# ============================================================================

def example_health_check():
    """Check service health."""
    print("\n" + "="*70)
    print("Example 4: Health Check (No Auth Required)")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Example 5: Send HTML email with multiple recipients
# ============================================================================

def example_html_email_multiple_recipients():
    """Send formatted HTML email to multiple recipients."""
    print("\n" + "="*70)
    print("Example 5: Send HTML Email to Multiple Recipients")
    print("="*70)
    
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .container { max-width: 600px; margin: 0 auto; }
            .header { background-color: #007bff; color: white; padding: 20px; }
            .content { padding: 20px; }
            .button { background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Our Service</h1>
            </div>
            <div class="content">
                <p>Hello!</p>
                <p>You've been invited to join our service. Click the button below to get started:</p>
                <p>
                    <a href="https://example.com/signup" class="button">Sign Up Now</a>
                </p>
                <p>Best regards,<br>The Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    payload = {
        "to": ["user1@example.com", "user2@example.com", "user3@example.com"],
        "subject": "You're invited to join our service",
        "body": html_body,
        "is_html": True,
        "cc": ["manager@example.com"]
    }
    
    response = requests.post(
        f"{BASE_URL}/send-email",
        json=payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Example 6: Send bulk emails (sequential)
# ============================================================================

def example_bulk_email_sending():
    """Send the same email to multiple recipients."""
    print("\n" + "="*70)
    print("Example 6: Bulk Email Sending")
    print("="*70)
    
    recipients = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "user4@example.com"
    ]
    
    results = []
    
    for recipient in recipients:
        payload = {
            "to": [recipient],
            "subject": f"Personalized message for {recipient}",
            "body": f"""
            <h2>Hello {recipient}</h2>
            <p>This is a personalized email sent to you.</p>
            <p>Thank you for being part of our service!</p>
            """,
            "is_html": True
        }
        
        response = requests.post(
            f"{BASE_URL}/send-email",
            json=payload,
            auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
        )
        
        results.append({
            "recipient": recipient,
            "status": response.status_code,
            "result": response.json()
        })
        
        print(f"✓ Sent to {recipient}: {response.status_code}")
    
    print(f"\nBulk sending complete. {len(results)} emails processed.")
    return results

# ============================================================================
# Example 7: Error handling
# ============================================================================

def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "="*70)
    print("Example 7: Error Handling")
    print("="*70)
    
    # Test 1: Invalid credentials
    print("\n1. Invalid Credentials:")
    response = requests.post(
        f"{BASE_URL}/send-email",
        json={
            "to": ["test@example.com"],
            "subject": "Test",
            "body": "Test"
        },
        auth=HTTPBasicAuth("wrong_user", "wrong_pass")
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: Invalid email format
    print("\n2. Invalid Email Format:")
    response = requests.post(
        f"{BASE_URL}/send-email",
        json={
            "to": ["not-an-email"],  # Invalid email
            "subject": "Test",
            "body": "Test"
        },
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 3: Missing required field
    print("\n3. Missing Required Field:")
    response = requests.post(
        f"{BASE_URL}/send-email",
        json={
            "to": ["recipient@example.com"],
            # Missing "subject"
            "body": "Test"
        },
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

# ============================================================================
# Example 8: Using plain text email
# ============================================================================

def example_plain_text_email():
    """Send plain text email."""
    print("\n" + "="*70)
    print("Example 8: Plain Text Email")
    print("="*70)
    
    payload = {
        "to": ["recipient@example.com"],
        "subject": "Plain Text Email",
        "body": """
Dear John,

Thank you for reaching out to us. We're excited to help you with our service.

Please find the details below:
- Service: Email API
- Version: 1.0.0
- Status: Operational

If you have any questions, feel free to contact us.

Best regards,
Support Team
        """,
        "is_html": False  # Plain text
    }
    
    response = requests.post(
        f"{BASE_URL}/send-email",
        json=payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json()

# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🚀 "*20)
    print("Email Service API - Usage Examples")
    print("🚀 "*20)
    
    # Run examples
    try:
        example_health_check()
        example_basic_auth_email()
        example_bearer_token_email()
        example_get_status()
        example_html_email_multiple_recipients()
        example_plain_text_email()
        example_bulk_email_sending()
        example_error_handling()
        
        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the service.")
        print("Make sure the service is running at:", BASE_URL)
        print("\nStart the service with: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
