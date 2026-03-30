"""
Owner contacts registry module.

Manages a local JSON file that maps owner group names (e.g. "it_team")
to individual contacts with email and phone_number fields.

The JSON structure is:
{
    "Owners": {
        "<group_name>": {
            "<contact_name>": {
                "email": "...",
                "phone_number": "..."
            },
            ...
        },
        ...
    }
}
"""

import json
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Path to the contacts JSON file (relative to this module's directory)
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CONTACTS_FILE = os.path.join(_DATA_DIR, "contacts.json")


def _load_contacts() -> dict:
    """Load and return the contacts dict from the JSON file."""
    if not os.path.exists(CONTACTS_FILE):
        logger.warning(f"Contacts file not found at {CONTACTS_FILE}, returning empty.")
        return {"Owners": {}}
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading contacts file: {e}")
        return {"Owners": {}}


def get_owner_emails(owner_name: str) -> List[str]:
    """
    Resolve an owner group name to a list of email addresses.

    Args:
        owner_name: Key under "Owners" in the contacts JSON (e.g. "it_team").

    Returns:
        List of email addresses for all contacts in the group.

    Raises:
        ValueError: If the owner group is not found or has no contacts with emails.
    """
    data = _load_contacts()
    owners = data.get("Owners", {})
    group = owners.get(owner_name)

    if group is None:
        raise ValueError(f"Owner group '{owner_name}' not found in contacts file.")

    emails = [
        contact["email"]
        for contact in group.values()
        if isinstance(contact, dict) and contact.get("email")
    ]

    if not emails:
        raise ValueError(f"No email addresses found for owner group '{owner_name}'.")

    return emails


def get_owner_phones(owner_name: str) -> List[str]:
    """
    Resolve an owner group name to a list of phone numbers.

    Args:
        owner_name: Key under "Owners" in the contacts JSON (e.g. "it_team").

    Returns:
        List of phone numbers for all contacts in the group.

    Raises:
        ValueError: If the owner group is not found or has no contacts with phone numbers.
    """
    data = _load_contacts()
    owners = data.get("Owners", {})
    group = owners.get(owner_name)

    if group is None:
        raise ValueError(f"Owner group '{owner_name}' not found in contacts file.")

    phones = [
        contact["phone_number"]
        for contact in group.values()
        if isinstance(contact, dict) and contact.get("phone_number")
    ]

    if not phones:
        raise ValueError(f"No phone numbers found for owner group '{owner_name}'.")

    return phones


def save_contacts(data: Dict[str, Any]) -> None:
    """
    Overwrite the contacts JSON file with the provided data.

    Args:
        data: Dict with an "Owners" key following the expected schema.
    """
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Contacts file saved to {CONTACTS_FILE}")


def get_all_contacts() -> dict:
    """Return the full contacts dictionary."""
    return _load_contacts()
