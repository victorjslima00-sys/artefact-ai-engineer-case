"""
Configuration module for the Empório da Música chatbot.
Loads environment variables and provides centralized settings.
"""

import os
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

STORE_TZ = ZoneInfo("America/Campo_Grande")

# --- Reference Date & Time ---
# Configurable date for testing return/warranty policies.
# If REFERENCE_DATE is empty, uses the current system date.
_ref_date_str: str = os.getenv("REFERENCE_DATE", "")


def get_current_datetime() -> datetime:
    """
    Return current datetime in America/Campo_Grande timezone.
    If REFERENCE_DATE is set, uses that date combined with the current Campo Grande local time.
    """
    now_cg = datetime.now(STORE_TZ)
    ref_str = os.getenv("REFERENCE_DATE", _ref_date_str)
    if ref_str:
        ref_d = datetime.strptime(ref_str, "%Y-%m-%d").date()
        return datetime.combine(ref_d, now_cg.time(), tzinfo=STORE_TZ)
    return now_cg


def get_reference_date() -> date:
    """Return the reference date for policy calculations."""
    return get_current_datetime().date()


def is_store_open(dt: datetime) -> tuple[bool, str]:
    """
    Check if store is currently open according to business hours:
    - Seg a Sex: 09h às 18h
    - Sábado: 09h às 13h
    - Domingo e Feriados: Fechado

    Returns (is_open: bool, status_description: str)
    """
    weekday = dt.weekday()  # 0: Seg, ..., 5: Sáb, 6: Dom
    t = dt.time()

    # Segunda a Sexta: 09:00 às 18:00
    if 0 <= weekday <= 4:
        open_time = time(9, 0)
        close_time = time(18, 0)
        if open_time <= t < close_time:
            return True, "Aberto agora (segunda a sexta das 09:00 às 18:00)"
        elif t < open_time:
            return False, f"Fechado agora. Abre hoje às 09:00 (segunda a sexta das 09:00 às 18:00)"
        else:
            next_day_info = "amanhã às 09:00" if weekday < 4 else "sábado às 09:00"
            return False, f"Fechado agora (expediente encerrado às 18:00). Retorno: {next_day_info}"

    # Sábado: 09:00 às 13:00
    elif weekday == 5:
        open_time = time(9, 0)
        close_time = time(13, 0)
        if open_time <= t < close_time:
            return True, "Aberto agora (sábado das 09:00 às 13:00)"
        elif t < open_time:
            return False, "Fechado agora. Abre hoje às 09:00 (sábado das 09:00 às 13:00)"
        else:
            return False, "Fechado agora (expediente de sábado encerrado às 13:00). Retorno: segunda-feira às 09:00"

    # Domingo
    else:
        return False, "Fechado agora (domingo). Retorno: segunda-feira às 09:00"


# --- Data Paths ---
DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# --- Chat History ---
MAX_HISTORY_MESSAGES: int = 8  # Keep the last 8 messages (4 user + 4 assistant turns)
