"""
Unit tests for store operating hours and schedule logic in src.config.
"""

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config import is_store_open, STORE_TZ


class TestStoreOperatingHours(unittest.TestCase):
    def test_weekday_open_hours(self):
        # Terça-feira às 14:30 -> Aberto
        dt = datetime(2026, 3, 24, 14, 30, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertTrue(is_open)
        self.assertIn("Aberto agora", desc)

    def test_weekday_before_opening(self):
        # Quarta-feira às 08:15 -> Fechado, abre às 09:00
        dt = datetime(2026, 3, 25, 8, 15, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertFalse(is_open)
        self.assertIn("Abre hoje às 09:00", desc)

    def test_weekday_after_closing(self):
        # Quinta-feira às 19:00 -> Fechado, retorno amanhã às 09:00
        dt = datetime(2026, 3, 26, 19, 0, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertFalse(is_open)
        self.assertIn("amanhã às 09:00", desc)

    def test_friday_after_closing(self):
        # Sexta-feira às 20:00 -> Fechado, retorno sábado às 09:00
        dt = datetime(2026, 3, 27, 20, 0, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertFalse(is_open)
        self.assertIn("sábado às 09:00", desc)

    def test_saturday_open_hours(self):
        # Sábado às 11:00 -> Aberto
        dt = datetime(2026, 3, 28, 11, 0, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertTrue(is_open)
        self.assertIn("sábado das 09:00 às 13:00", desc)

    def test_saturday_after_closing(self):
        # Sábado às 14:00 -> Fechado, retorno segunda-feira
        dt = datetime(2026, 3, 28, 14, 0, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertFalse(is_open)
        self.assertIn("segunda-feira às 09:00", desc)

    def test_sunday_closed(self):
        # Domingo o dia todo -> Fechado, retorno segunda-feira
        dt = datetime(2026, 3, 29, 10, 0, tzinfo=STORE_TZ)
        is_open, desc = is_store_open(dt)
        self.assertFalse(is_open)
        self.assertIn("domingo", desc)
        self.assertIn("segunda-feira às 09:00", desc)


if __name__ == "__main__":
    unittest.main()
