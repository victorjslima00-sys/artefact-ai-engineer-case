"""
Tools module for the Empório da Música chatbot.
Defines the functions the agent can call to query structured data.
"""

import unicodedata
from datetime import date, timedelta
from typing import Optional

from src.config import get_reference_date
from src.data_loader import DataStore


def _normalize_text(text: str) -> str:
    """Normalize text: lowercase, remove accents and extra spaces."""
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text.lower())
    without_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return without_accents.strip()


def _normalize_plural_singular(text: str) -> str:
    """Stem common Portuguese singular/plural variations for instrument categories."""
    norm = _normalize_text(text)
    # Special endings
    if norm.endswith("oes"):  # violoes -> violao
        norm = norm[:-3] + "ao"
    elif norm.endswith("es"):
        norm = norm[:-2]
    elif norm.endswith("s") and not norm.endswith("as") and not norm.endswith("is"):
        norm = norm[:-1]
    return norm


def _calculate_max_installments(price: float) -> int:
    """
    Calculate maximum installments based on store policy:
    - up to 3x: without minimum installment, except below R$ 50.00
    - 4x to 6x: minimum installment R$ 80.00
    - 7x to 12x: minimum installment R$ 100.00
    """
    max_inst = 1
    for n in range(2, 13):
        installment_val = price / n
        if n <= 3:
            if installment_val >= 50.0:
                max_inst = n
        elif 4 <= n <= 6:
            if installment_val >= 80.0:
                max_inst = n
        elif 7 <= n <= 12:
            if installment_val >= 100.0:
                max_inst = n
    return max_inst


def _format_price(value: float) -> str:
    """Format a numeric value as BRL currency."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _product_summary(row, store: DataStore, include_specs: bool = False) -> dict:
    """Build a summary dict for a single product row."""
    product_id = int(row["product_id"])
    promo = store.get_active_promotion(product_id)
    category = store.get_category_name(int(row["category_id"]))
    price_val = float(row["price_brl"])

    summary = {
        "product_id": product_id,
        "name": row["name"],
        "category": category,
        "price": _format_price(price_val),
        "status": row["status"],
        "stock": int(row["stock_quantity"]),
        "description": row["description"],
    }

    if include_specs and row.get("specs_parsed"):
        summary["specs"] = row["specs_parsed"]

    if promo:
        discounted = price_val * (1 - promo["discount_percent"] / 100)
        summary["promotion"] = {
            "description": promo["description"],
            "discount": f"{promo['discount_percent']:.0f}%",
            "original_price": _format_price(price_val),
            "promotional_price": _format_price(discounted),
        }
        # Desconto do PIX NÃO se aplica sobre preço promocional
    else:
        # Produtos sem promoção ativa: inclui pix_price (5% off tabela) e parcelamento
        pix_price_val = price_val * 0.95
        max_inst = _calculate_max_installments(price_val)
        summary["pix_price"] = _format_price(pix_price_val)
        summary["max_installments"] = f"{max_inst}x sem juros"

    if row["status"] == "discontinued":
        summary["note"] = "Este produto foi descontinuado e não está mais disponível para venda."
    elif row["status"] == "coming_soon":
        summary["note"] = "Este produto ainda não está disponível. Em breve no catálogo."
    elif int(row["stock_quantity"]) == 0:
        summary["note"] = "Produto temporariamente fora de estoque."

    return summary


# ---------- Tool Functions ----------


def search_products(
    store: DataStore,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    search_term: Optional[str] = None,
    only_available: bool = True,
) -> dict:
    """
    Search for products by category, price range, or keyword.
    Returns a list of matching products with prices and availability.
    """
    df = store.products.copy()

    # Default: only show active products with stock > 0
    if only_available:
        df = df[(df["status"] == "active") & (df["stock_quantity"] > 0)]

    if category:
        cat_norm = _normalize_text(category)
        cat_stem = _normalize_plural_singular(category)
        
        # Check direct substring matching on normalized category names
        matching_ids = []
        for _, cat_row in store.categories.iterrows():
            c_name = cat_row["name"]
            c_norm = _normalize_text(c_name)
            c_stem = _normalize_plural_singular(c_name)
            if cat_norm in c_norm or cat_stem in c_norm or cat_stem in c_stem:
                matching_ids.append(cat_row["category_id"])

        if matching_ids:
            df = df[df["category_id"].isin(matching_ids)]
        else:
            return {"results": [], "message": f"Categoria '{category}' não encontrada. Categorias disponíveis: {', '.join(store.categories['name'].tolist())}"}

    if max_price is not None:
        df = df[df["price_brl"] <= max_price]

    if min_price is not None:
        df = df[df["price_brl"] >= min_price]

    if search_term:
        term_lower = search_term.lower()
        df = df[
            df["name"].str.lower().str.contains(term_lower, na=False)
            | df["description"].str.lower().str.contains(term_lower, na=False)
        ]

    if df.empty:
        return {"results": [], "message": "Nenhum produto encontrado com os critérios informados."}

    # Sort by price ascending
    df = df.sort_values("price_brl")

    results = [_product_summary(row, store) for _, row in df.iterrows()]
    return {"results": results, "total_found": len(results)}


def get_product_details(store: DataStore, product_id: Optional[int] = None, product_name: Optional[str] = None) -> dict:
    """
    Get detailed information about a specific product by ID or name.
    Includes specs, promotion info, and availability.
    """
    df = store.products

    if product_id is not None:
        match = df[df["product_id"] == product_id]
    elif product_name:
        name_lower = product_name.lower()
        match = df[df["name"].str.lower().str.contains(name_lower, na=False)]
    else:
        return {"error": "Informe o ID ou o nome do produto."}

    if match.empty:
        return {"error": "Produto não encontrado."}

    results = [_product_summary(row, store, include_specs=True) for _, row in match.iterrows()]
    return {"results": results}


def check_order_status(
    store: DataStore,
    customer_identifier: str,
    order_id: Optional[int] = None,
) -> dict:
    """
    Check order status for a customer identified by phone or email.
    Requires customer identification for LGPD compliance.
    """
    customer = store.find_customer_by_phone_or_email(customer_identifier)
    if customer is None:
        return {
            "error": "Não encontrei nenhum cadastro com esse telefone ou e-mail. "
            "Verifique os dados informados ou entre em contato com a loja."
        }

    customer_id = int(customer["customer_id"])
    customer_name = customer["name"]

    orders_df = store.orders[store.orders["customer_id"] == customer_id].copy()

    if order_id is not None:
        orders_df = orders_df[orders_df["order_id"] == order_id]

    if orders_df.empty:
        if order_id:
            return {"message": f"Pedido #{order_id} não encontrado para o cliente {customer_name}."}
        return {"message": f"Nenhum pedido encontrado para {customer_name}."}

    ref_date = get_reference_date()
    results = []
    for _, order in orders_df.iterrows():
        # Get items for this order
        items_df = store.order_items[store.order_items["order_id"] == int(order["order_id"])]
        items = []
        for _, item in items_df.iterrows():
            prod = store.products[store.products["product_id"] == int(item["product_id"])]
            if not prod.empty:
                items.append({
                    "product": prod.iloc[0]["name"],
                    "quantity": int(item["quantity"]),
                })

        order_info = {
            "order_id": int(order["order_id"]),
            "date": order["order_date"].strftime("%d/%m/%Y") if not str(order["order_date"]) == "NaT" else "N/A",
            "status": order["status"],
            "total": _format_price(float(order["total_brl"])),
            "payment_method": order["payment_method"],
            "items": items,
        }

        # Add tracking if available
        if order.get("tracking_code") and str(order["tracking_code"]) != "nan":
            order_info["tracking_code"] = order["tracking_code"]

        if order.get("estimated_delivery") and str(order["estimated_delivery"]) != "nan":
            order_info["estimated_delivery"] = order["estimated_delivery"]

        if order.get("notes") and str(order["notes"]) != "nan":
            order_info["notes"] = order["notes"]

        # Calculate return eligibility (7 calendar days from receipt).
        # The dataset lacks an actual delivery_date; for delivered orders,
        # estimated_delivery is the only available date and is therefore a proxy.
        if order["status"] == "delivered":
            raw_delivery_date = order.get("estimated_delivery")
            delivery_date = None
            if raw_delivery_date is not None and str(raw_delivery_date).strip().lower() not in {"", "nan", "nat", "none"}:
                try:
                    delivery_date = date.fromisoformat(str(raw_delivery_date)[:10])
                except ValueError:
                    pass

            if delivery_date is None:
                order_info["return_eligible"] = None
                order_info["return_eligibility_status"] = "unknown"
                order_info["return_eligibility_note"] = (
                    "A data efetiva de entrega não está disponível; confirme-a com o cliente."
                )
            else:
                days_since = (ref_date - delivery_date).days
                if days_since < 0:
                    order_info["return_eligible"] = None
                    order_info["return_eligibility_status"] = "unknown"
                    order_info["return_eligibility_note"] = (
                        "A data estimada está no futuro; confirme a data efetiva de entrega."
                    )
                else:
                    order_info["return_eligible"] = days_since <= 7
                    order_info["return_eligibility_status"] = "provisional"
                    order_info["return_eligibility_basis"] = "estimated_delivery (proxy; data efetiva ausente)"
                    order_info["return_deadline"] = (delivery_date + timedelta(days=7)).strftime("%d/%m/%Y")
                    if days_since > 7:
                        order_info["days_since_delivery_estimate"] = days_since

        results.append(order_info)

    return {"customer_name": customer_name, "orders": results}


def list_active_promotions(store: DataStore) -> dict:
    """
    List all currently active promotions with product details and discounted prices.
    """
    active = store.promotions[store.promotions["is_active"] == 1]

    if active.empty:
        return {"message": "Não há promoções ativas no momento."}

    results = []
    for _, promo in active.iterrows():
        prod = store.products[store.products["product_id"] == int(promo["product_id"])]
        if prod.empty:
            continue
        product = prod.iloc[0]
        original = float(product["price_brl"])
        discount = float(promo["discount_percent"])
        discounted = original * (1 - discount / 100)

        results.append({
            "product": product["name"],
            "category": store.get_category_name(int(product["category_id"])),
            "original_price": _format_price(original),
            "discount": f"{discount:.0f}%",
            "promotional_price": _format_price(discounted),
            "promotion": promo["description"],
            "available": product["status"] == "active" and int(product["stock_quantity"]) > 0,
        })

    return {"active_promotions": results, "total": len(results)}


# ---------- Tool Declarations for Gemini API ----------

TOOL_DECLARATIONS = [
    {
        "name": "search_products",
        "description": (
            "Busca produtos no catálogo da Empório da Música por categoria, faixa de preço ou palavra-chave. "
            "Use quando o cliente perguntar sobre produtos disponíveis, opções de instrumentos ou catálogo."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Nome da categoria (ex: Violões, Guitarras, Baixos, Ukuleles, Baterias, Teclados, Sopro). Opcional.",
                },
                "max_price": {
                    "type": "number",
                    "description": "Preço máximo em reais. Opcional.",
                },
                "min_price": {
                    "type": "number",
                    "description": "Preço mínimo em reais. Opcional.",
                },
                "search_term": {
                    "type": "string",
                    "description": "Termo de busca no nome ou descrição do produto (ex: 'Yamaha', 'nylon', 'dreadnought'). Opcional.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_product_details",
        "description": (
            "Obtém informações detalhadas de um produto específico: preço, especificações técnicas, estoque, "
            "promoção ativa e disponibilidade. Use quando o cliente perguntar sobre um produto específico."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Nome ou parte do nome do produto (ex: 'Takamine GD20', 'Taylor 110e').",
                },
                "product_id": {
                    "type": "integer",
                    "description": "ID numérico do produto, se conhecido.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "check_order_status",
        "description": (
            "Consulta o status de pedidos de um cliente. REQUER identificação do cliente por telefone ou e-mail "
            "para conformidade com LGPD. Se o cliente não informou telefone ou e-mail, peça antes de chamar esta função."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_identifier": {
                    "type": "string",
                    "description": "Telefone ou e-mail do cliente para identificação.",
                },
                "order_id": {
                    "type": "integer",
                    "description": "Número do pedido específico, se o cliente informou. Opcional.",
                },
            },
            "required": ["customer_identifier"],
        },
    },
    {
        "name": "list_active_promotions",
        "description": (
            "Lista todas as promoções ativas com produtos, preços originais, descontos e preços promocionais. "
            "Use quando o cliente perguntar sobre promoções, descontos ou ofertas."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
