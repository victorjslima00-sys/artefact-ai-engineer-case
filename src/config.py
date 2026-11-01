"""
Configuration module for the Empório da Música chatbot.
Loads environment variables and provides centralized settings.
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# --- Reference Date ---
# Configurable date for testing return/warranty policies.
# If REFERENCE_DATE is empty, uses the current system date.
_ref_date_str: str = os.getenv("REFERENCE_DATE", "")


def get_reference_date() -> date:
    """Return the reference date for policy calculations."""
    if _ref_date_str:
        return datetime.strptime(_ref_date_str, "%Y-%m-%d").date()
    return date.today()


# --- Data Paths ---
DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# --- Chat History ---
MAX_HISTORY_MESSAGES: int = 8  # Keep the last 8 messages (4 user + 4 assistant turns)
