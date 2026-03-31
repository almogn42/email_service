"""
Example usage of the Email & SMS Service API.
This file shows different ways to interact with the service.
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
# Example 3: Send SMS with Basic Authentication
# ============================================================================

def example_send_sms():
    """Send an SMS using Basic Authentication."""
    print("\n" + "="*70)
    print("Example 3: Send SMS with Basic Auth")
    print("="*70)

    payload = {
        "recipient": "0501234567",
        "text": "Hello from the SMS Service!",
        "recipient_type": 0
    }

    response = requests.post(
        f"{BASE_URL}/send-sms",
        json=payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    return response.json()

# ============================================================================
# Example 4: Send to Owner Group (Email & SMS)
# ============================================================================

def example_send_to_owner():
    """Send an email and SMS to a predefined owner group instead of direct lists."""
    print("\n" + "="*70)
    print("Example 4: Send Email & SMS to an Owner Group")
    print("="*70)

    # 1. Email via owner group
    email_payload = {
        "owner": "admin_team",
        "subject": "System Alert",
        "body": "<p>This is a system alert sent to the admin_team owner group.</p>",
        "is_html": True
    }

    print("-- Sending Email to Owner Group: 'admin_team' --")
    response_email = requests.post(
        f"{BASE_URL}/send-email",
        json=email_payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    print(f"Email Status: {response_email.status_code}")
    print(f"Email Response: {response_email.json()}")

    # 2. SMS via owner group
    sms_payload = {
        "owner": "admin_team",
        "text": "CRITICAL: System alert triggered.",
        "recipient_type": 0
    }

    print("\n-- Sending SMS to Owner Group: 'admin_team' --")
    response_sms = requests.post(
        f"{BASE_URL}/send-sms",
        json=sms_payload,
        auth=HTTPBasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)
    )
    print(f"SMS Status: {response_sms.status_code}")
    print(f"SMS Response: {response_sms.json()}")

# ============================================================================
# Example 5: Get service status
# ============================================================================

def example_get_status():
    """Get service status with authentication."""
    print("\n" + "="*70)
    print("Example 5: Get Service Status")
    print("="*70)
    
    response = requests.get(
        f"{BASE_URL}/status",
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
    print("Email & SMS Service API - Usage Examples")
    print("🚀 "*20)
    
    # Run examples
    try:
        example_basic_auth_email()
        example_bearer_token_email()
        example_send_sms()
        example_send_to_owner()
        example_get_status()
        
        print("\n" + "="*70)
        print("✅ All examples completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the service.")
        print("Make sure the service is running at:", BASE_URL)
        print("\nStart the service with: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
