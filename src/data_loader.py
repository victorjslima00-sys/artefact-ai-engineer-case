"""
Data loader module for the Empório da Música chatbot.
Loads, cleans and provides access to all CSV data files, with support for in-memory stock mutations.
"""

import json
import os
from typing import Optional

import pandas as pd

from src.config import DATA_DIR


def _csv_path(name: str) -> str:
    """Resolve the full path for a data CSV file."""
    return os.path.join(DATA_DIR, f"desafio_tecnico_ai_eng - {name}.csv")


def _safe_json_parse(raw: str) -> dict:
    """Parse a JSON string stored in a CSV cell, returning an empty dict on failure."""
    if pd.isna(raw) or not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def load_categories() -> pd.DataFrame:
    """Load and return the categories table."""
    df = pd.read_csv(_csv_path("categories"), encoding="utf-8")
    return df


def load_products() -> pd.DataFrame:
    """Load, clean and return the products table with parsed specs."""
    df = pd.read_csv(_csv_path("products"), encoding="utf-8")

    # Ensure correct types
    df["price_brl"] = pd.to_numeric(df["price_brl"], errors="coerce")
    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)

    # Parse JSON specs into a dictionary column
    df["specs_parsed"] = df["specs"].apply(_safe_json_parse)

    return df


def load_customers() -> pd.DataFrame:
    """Load and return the customers table."""
    df = pd.read_csv(_csv_path("customers"), encoding="utf-8")
    return df


def load_orders() -> pd.DataFrame:
    """Load and return the orders table."""
    df = pd.read_csv(_csv_path("orders"), encoding="utf-8")

    # Parse dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # Ensure total is numeric
    df["total_brl"] = pd.to_numeric(df["total_brl"], errors="coerce")

    return df


def load_order_items() -> pd.DataFrame:
    """Load and return the order_items table."""
    df = pd.read_csv(_csv_path("order_items"), encoding="utf-8")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    return df


def load_promotions() -> pd.DataFrame:
    """Load and return the promotions table."""
    df = pd.read_csv(_csv_path("promotions"), encoding="utf-8")
    df["discount_percent"] = pd.to_numeric(df["discount_percent"], errors="coerce")
    df["is_active"] = pd.to_numeric(df["is_active"], errors="coerce").fillna(0).astype(int)
    return df


class DataStore:
    """
    Centralized data store that loads all tables once and provides
    convenient access for the agent's tools.
    Supports in-memory mutations (e.g. stock updates from cart/simulation).
    """

    def __init__(self) -> None:
        self.categories: pd.DataFrame = load_categories()
        self.products: pd.DataFrame = load_products()
        self.customers: pd.DataFrame = load_customers()
        self.orders: pd.DataFrame = load_orders()
        self.order_items: pd.DataFrame = load_order_items()
        self.promotions: pd.DataFrame = load_promotions()

        # Pre-compute active promotions for quick lookup
        self._active_promos: pd.DataFrame = self.promotions[self.promotions["is_active"] == 1].copy()

    def get_active_promotion(self, product_id: int) -> Optional[dict]:
        """Return the active promotion for a product, or None."""
        match = self._active_promos[self._active_promos["product_id"] == product_id]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "promotion_id": int(row["promotion_id"]),
            "discount_percent": float(row["discount_percent"]),
            "description": row["description"],
        }

    def get_category_name(self, category_id: int) -> str:
        """Return the category name for a given ID."""
        match = self.categories[self.categories["category_id"] == category_id]
        if match.empty:
            return "Categoria desconhecida"
        return match.iloc[0]["name"]

    def find_customer_by_phone_or_email(self, identifier: str) -> Optional[dict]:
        """
        Look up a customer by phone number or email address.
        Returns customer dict or None if not found.
        """
        identifier = identifier.strip().lower()

        # Try email match
        email_match = self.customers[self.customers["email"].str.lower().str.strip() == identifier]
        if not email_match.empty:
            return email_match.iloc[0].to_dict()

        # Try phone match (normalize: remove spaces, dashes, parentheses)
        def normalize_phone(p: str) -> str:
            return "".join(c for c in str(p) if c.isdigit())

        normalized_input = normalize_phone(identifier)
        if normalized_input:
            self.customers["_phone_norm"] = self.customers["phone"].apply(normalize_phone)
            phone_match = self.customers[self.customers["_phone_norm"] == normalized_input]
            self.customers.drop(columns=["_phone_norm"], inplace=True)
            if not phone_match.empty:
                return phone_match.iloc[0].to_dict()

        return None

    def update_product_stock(self, product_id: int, new_quantity: int) -> bool:
        """Update in-memory product stock quantity directly."""
        mask = self.products["product_id"] == product_id
        if not mask.any():
            return False
        self.products.loc[mask, "stock_quantity"] = int(new_quantity)
        return True

    def adjust_product_stock(self, product_id: int, delta: int) -> Optional[int]:
        """Adjust product stock by delta (positive or negative). Returns new quantity."""
        mask = self.products["product_id"] == product_id
        if not mask.any():
            return None
        current = int(self.products.loc[mask, "stock_quantity"].iloc[0])
        new_qty = max(0, current + delta)
        self.products.loc[mask, "stock_quantity"] = new_qty
        return new_qty

    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """Return a single product row as a dict, or None."""
        match = self.products[self.products["product_id"] == product_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()
