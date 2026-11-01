"""
Streamlit UI for Empório da Música.
Modern Storefront with live catalog, interactive cart/checkout simulation,
light/dark theme toggle, and an expandable floating AI Assistant popover.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from src.agent import EmporioChatbot
from src.data_loader import DataStore
from src.config import get_reference_date

# --- Page Configuration ---
st.set_page_config(
    page_title="Empório da Música — Loja Oficial & Atendimento",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Session State Initialization ---
if "store" not in st.session_state:
    st.session_state.store = DataStore()

if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = EmporioChatbot(store=st.session_state.store)
        st.session_state.chatbot_ready = True
    except Exception as e:
        st.session_state.chatbot_ready = False
        st.session_state.chatbot_error = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "cart" not in st.session_state:
    st.session_state.cart = {}  # {product_id: quantity}

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Todas"

if "price_limit" not in st.session_state:
    st.session_state.price_limit = 25000.0

if "toast_msg" not in st.session_state:
    st.session_state.toast_msg = None


# --- Custom CSS for Themes & Modern Storefront ---
theme_vars = {
    "light": {
        "bg_color": "#f8fafc",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "accent": "#d97706",
        "accent_hover": "#b45309",
        "hero_bg": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        "hero_text": "#ffffff",
        "badge_bg": "#fef3c7",
        "badge_text": "#92400e",
        "chat_bg": "#ffffff",
    },
    "dark": {
        "bg_color": "#090d16",
        "card_bg": "#131b2e",
        "card_border": "#1e293b",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent": "#f59e0b",
        "accent_hover": "#fbbf24",
        "hero_bg": "linear-gradient(135deg, #0f172a 0%, #020617 100%)",
        "hero_text": "#f8fafc",
        "badge_bg": "#78350f",
        "badge_text": "#fde68a",
        "chat_bg": "#0f172a",
    }
}

t = theme_vars[st.session_state.theme]

st.markdown(f"""
<style>
    /* Global App Container */
    .stApp {{
        background-color: {t['bg_color']};
        color: {t['text_primary']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Hero Banner */
    .hero-container {{
        background: {t['hero_bg']};
        color: {t['hero_text']};
        padding: 2.2rem 2.5rem;
        border-radius: 18px;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1.5rem;
    }}
    .hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }}
    .hero-pill-badge {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        padding: 0.4rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }}

    /* Product Cards */
    .product-card {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 16px;
        padding: 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .product-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 14px 20px -4px rgba(0, 0, 0, 0.1);
        border-color: {t['accent']};
    }}
    .product-category {{
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: {t['accent']};
        margin-bottom: 0.35rem;
    }}
    .product-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {t['text_primary']};
        margin-bottom: 0.5rem;
        line-height: 1.35;
        min-height: 2.8rem;
    }}
    .product-desc {{
        font-size: 0.85rem;
        color: {t['text_secondary']};
        margin-bottom: 0.8rem;
        line-height: 1.45;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .product-price {{
        font-size: 1.25rem;
        font-weight: 800;
        color: {t['text_primary']};
    }}
    .product-old-price {{
        font-size: 0.85rem;
        text-decoration: line-through;
        color: {t['text_secondary']};
        margin-right: 0.4rem;
    }}
    .promo-tag {{
        background: {t['badge_bg']};
        color: {t['badge_text']};
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 0.5rem;
    }}
    .stock-badge {{
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        display: inline-block;
    }}
    .stock-in {{
        background: #dcfce7;
        color: #166534;
    }}
    .stock-low {{
        background: #fef9c3;
        color: #854d0e;
    }}
    .stock-out {{
        background: #fee2e2;
        color: #991b1b;
    }}

    /* Navigation Bar */
    .top-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 1.2rem 0;
        border-bottom: 1px solid {t['card_border']};
        margin-bottom: 1.2rem;
    }}

    /* Soft floating pills */
    .pill-info-bar {{
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }}
    .pill-item {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        padding: 0.4rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.83rem;
        color: {t['text_secondary']};
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .pill-item strong {{
        color: {t['text_primary']};
    }}
</style>
""", unsafe_allow_html=True)


# --- Helper: Currency Formatter ---
def format_currency(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Top Navbar ---
nav_col1, nav_col2 = st.columns([3, 1])
with nav_col1:
    st.markdown("### 🎸 Empório da Música — Loja Virtual")
with nav_col2:
    theme_col, cart_col = st.columns([1, 1])
    with theme_col:
        is_dark = st.session_state.theme == "dark"
        theme_label = "☀️ Claro" if is_dark else "🌙 Escuro"
        if st.button(theme_label, key="theme_toggle_btn", use_container_width=True):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
    with cart_col:
        total_items_in_cart = sum(st.session_state.cart.values())
        st.button(f"🛒 Carrinho ({total_items_in_cart})", key="cart_btn_top", use_container_width=True)

# --- Hero Banner ---
ref_date = get_reference_date()
st.markdown(f"""
<div class="hero-container">
    <div>
        <h1 class="hero-title">Empório da Música</h1>
        <p class="hero-subtitle">Instrumentos musicais autênticos selecionados para músicos exigentes.</p>
    </div>
    <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
        <div class="hero-pill-badge">📍 Campo Grande/MS</div>
        <div class="hero-pill-badge">📅 {ref_date.strftime('%d/%m/%Y')}</div>
        <div class="hero-pill-badge">⚡ Atendimento IA Ativo</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Interactive Soft Pills Bar ---
st.markdown(f"""
<div class="pill-info-bar">
    <div class="pill-item">
        <span>🕒</span>
        <span>Atendimento: <strong>Seg–Sex 09h às 18h | Sáb 09h às 13h</strong></span>
    </div>
    <div class="pill-item">
        <span>💳</span>
        <span>Pagamento: <strong>PIX 5% OFF ou até 12x s/ juros</strong></span>
    </div>
    <div class="pill-item">
        <span>🛡️</span>
        <span>Garantia: <strong>90 dias legal + Fabricante</strong></span>
    </div>
    <div class="pill-item">
        <span>📞</span>
        <span>WhatsApp: <strong>(67) 3321-4500</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Toast notification ---
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="✅")
    st.session_state.toast_msg = None


# --- Catalog Filters ---
f_col1, f_col2, f_col3 = st.columns([2, 1.5, 1.5])
categories = ["Todas"] + sorted(st.session_state.store.categories["name"].tolist())

with f_col1:
    search_term = st.text_input("🔍 Buscar instrumento...", value=st.session_state.search_query, placeholder="Ex: Takamine, Fender, violão nylon...")
    st.session_state.search_query = search_term

with f_col2:
    selected_cat = st.selectbox("Categoria", categories, index=categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0)
    st.session_state.selected_category = selected_cat

with f_col3:
    max_price_filter = st.slider("Preço máximo (R$)", min_value=150.0, max_value=25000.0, value=float(st.session_state.price_limit), step=100.0)
    st.session_state.price_limit = max_price_filter


# --- Filter Products Dataset ---
df_products = st.session_state.store.products.copy()

if selected_cat != "Todas":
    cat_match = st.session_state.store.categories[st.session_state.store.categories["name"] == selected_cat]
    if not cat_match.empty:
        c_id = cat_match.iloc[0]["category_id"]
        df_products = df_products[df_products["category_id"] == c_id]

if search_term:
    term = search_term.strip().lower()
    df_products = df_products[
        df_products["name"].str.lower().str.contains(term, na=False) |
        df_products["description"].str.lower().str.contains(term, na=False)
    ]

df_products = df_products[df_products["price_brl"] <= max_price_filter]
df_products = df_products.sort_values(by="price_brl")


# --- Main Layout: Catalog (Left/Center) & Live Stock/Cart Controls ---
col_catalog, col_drawer = st.columns([2.8, 1.2])

with col_catalog:
    st.markdown(f"#### Catálogo de Produtos ({len(df_products)} disponíveis)")

    if df_products.empty:
        st.info("Nenhum instrumento encontrado com os filtros selecionados.")
    else:
        # Render grid with 3 products per row
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df_products.iterrows()):
            p_id = int(row["product_id"])
            p_name = row["name"]
            p_price = float(row["price_brl"])
            p_stock = int(row["stock_quantity"])
            p_desc = row["description"]
            p_cat = st.session_state.store.get_category_name(int(row["category_id"]))
            p_promo = st.session_state.store.get_active_promotion(p_id)
            p_status = row["status"]

            with cols[idx % 3]:
                # Card HTML container
                promo_badge_html = ""
                price_html = f'<div class="product-price">{format_currency(p_price)}</div>'

                if p_promo:
                    disc = p_promo["discount_percent"]
                    final_p = p_price * (1 - disc / 100)
                    promo_badge_html = f'<div class="promo-tag">🔥 {disc:.0f}% OFF — {p_promo["description"]}</div>'
                    price_html = f'<div><span class="product-old-price">{format_currency(p_price)}</span><span class="product-price" style="color: #dc2626;">{format_currency(final_p)}</span></div>'

                if p_status == "discontinued":
                    stock_html = '<span class="stock-badge stock-out">Descontinuado</span>'
                elif p_status == "coming_soon":
                    stock_html = '<span class="stock-badge stock-low">Em Breve</span>'
                elif p_stock <= 0:
                    stock_html = '<span class="stock-badge stock-out">Esgotado (0)</span>'
                elif p_stock <= 3:
                    stock_html = f'<span class="stock-badge stock-low">Apenas {p_stock} em estoque</span>'
                else:
                    stock_html = f'<span class="stock-badge stock-in">{p_stock} em estoque</span>'

                st.markdown(f"""
                <div class="product-card">
                    <div>
                        <div class="product-category">{p_cat}</div>
                        <div class="product-title">{p_name}</div>
                        {promo_badge_html}
                        <div class="product-desc">{p_desc}</div>
                    </div>
                    <div style="margin-top: 0.8rem; display: flex; justify-content: space-between; align-items: baseline;">
                        {price_html}
                        {stock_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons below card
                btn_c1, btn_c2 = st.columns([1, 1])
                with btn_c1:
                    can_buy = p_stock > 0 and p_status == "active"
                    if st.button("🛒 Comprar", key=f"buy_{p_id}", disabled=not can_buy, use_container_width=True):
                        st.session_state.cart[p_id] = st.session_state.cart.get(p_id, 0) + 1
                        st.session_state.store.adjust_product_stock(p_id, -1)
                        st.session_state.toast_msg = f"{p_name} adicionado ao carrinho! (Estoque atualizado)"
                        st.rerun()

                with btn_c2:
                    if st.button("💬 Consultar", key=f"chat_{p_id}", use_container_width=True):
                        st.session_state.pending_prompt = f"Gostaria de saber mais sobre o instrumento '{p_name}'. Qual o preço e o estoque atual?"
                        st.rerun()

                st.write("")  # Vertical spacing between rows


with col_drawer:
    # --- Live Cart & Stock Simulation Box ---
    st.markdown("#### 🛍️ Simulação de Compra & Estoque")
    st.caption("Qualquer compra aqui altera o estoque no sistema em tempo real. Teste e pergunte ao Chatbot!")

    if not st.session_state.cart:
        st.info("Seu carrinho está vazio. Adicione instrumentos pelo catálogo.")
    else:
        total_order_val = 0.0
        for cart_p_id, qty in list(st.session_state.cart.items()):
            prod = st.session_state.store.get_product_by_id(cart_p_id)
            if prod:
                price = float(prod["price_brl"])
                promo = st.session_state.store.get_active_promotion(cart_p_id)
                if promo:
                    price = price * (1 - promo["discount_percent"] / 100)
                subtotal = price * qty
                total_order_val += subtotal

                cart_item_col1, cart_item_col2 = st.columns([3, 1])
                with cart_item_col1:
                    st.markdown(f"**{prod['name']}**")
                    st.caption(f"{qty}x {format_currency(price)} = **{format_currency(subtotal)}**")
                with cart_item_col2:
                    if st.button("❌", key=f"del_cart_{cart_p_id}"):
                        # Restore stock
                        st.session_state.store.adjust_product_stock(cart_p_id, qty)
                        del st.session_state.cart[cart_p_id]
                        st.session_state.toast_msg = f"Item removido do carrinho. Estoque restaurado."
                        st.rerun()
                st.divider()

        st.markdown(f"**Total da Compra: {format_currency(total_order_val)}**")
        st.caption(f"À vista no PIX (5% off): **{format_currency(total_order_val * 0.95)}**")

        if st.button("Finalizar Pedido Simulado", use_container_width=True, type="primary"):
            st.session_state.cart = {}
            st.success("Pedido concluído com sucesso! O estoque foi reservado permanentemente na sessão.")
            st.rerun()

    st.markdown("---")

    # --- Live Inventory Lab (Direct stock modification for test validation) ---
    st.markdown("#### 🔧 Painel de Testes de Estoque")
    st.caption("Altere a quantidade de qualquer produto e confira se o chatbot detecta a mudança:")

    test_product_name = st.selectbox(
        "Selecione um instrumento:",
        options=st.session_state.store.products["name"].tolist(),
        key="stock_test_select"
    )
    p_row = st.session_state.store.products[st.session_state.store.products["name"] == test_product_name].iloc[0]
    curr_qty = int(p_row["stock_quantity"])

    stock_col1, stock_col2 = st.columns([1, 1])
    with stock_col1:
        new_stock_val = st.number_input("Estoque:", min_value=0, max_value=999, value=curr_qty, key=f"num_stock_{p_row['product_id']}")
    with stock_col2:
        st.write("")
        st.write("")
        if st.button("Aplicar", key="btn_apply_stock", use_container_width=True):
            st.session_state.store.update_product_stock(int(p_row["product_id"]), int(new_stock_val))
            st.session_state.toast_msg = f"Estoque de '{test_product_name}' alterado para {new_stock_val}!"
            st.rerun()


# --- Floating Chatbot Popover (Soft Widget UI) ---
st.markdown("---")

chat_popover = st.popover("💬 Conversar com o Atendente Virtual (IA)", use_container_width=True)

with chat_popover:
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
        <div>
            <h4 style="margin: 0; color: {t['text_primary']};">🎸 Atendimento Empório da Música</h4>
            <span style="font-size: 0.8rem; color: {t['text_secondary']};">Assistente virtual inteligente conectado ao estoque</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chatbot_ready:
        st.error(f"Erro ao inicializar IA: {st.session_state.get('chatbot_error', 'Verifique a GEMINI_API_KEY')}")
    else:
        # Reset chat button
        if st.button("🧹 Limpar Conversa", key="clear_chat_popover_btn"):
            st.session_state.messages = []
            st.session_state.chatbot.reset_history()
            st.rerun()

        # Chat container
        chat_container = st.container(height=420)

        with chat_container:
            # Default welcome message
            if not st.session_state.messages:
                welcome_text = (
                    "Olá! 👋 Bem-vindo(a) à **Empório da Música**! Sou o assistente virtual da loja. "
                    "Posso te ajudar com dúvidas sobre instrumentos, promoções, políticas de devolução e disponibilidade de estoque. "
                    "Como posso te ajudar hoje? 🎵"
                )
                with st.chat_message("assistant", avatar="🎸"):
                    st.markdown(welcome_text)

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🎸" if msg["role"] == "assistant" else None):
                    st.markdown(msg["content"])

        # Handle pre-filled prompt from catalog "Consultar" button
        initial_input = ""
        if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
            initial_input = st.session_state.pending_prompt
            del st.session_state.pending_prompt

        user_input = st.chat_input("Digite sua mensagem para o atendente...", key="popover_chat_input")

        # If user submitted from chat input or clicked "Consultar"
        prompt_to_send = user_input or initial_input

        if prompt_to_send:
            st.session_state.messages.append({"role": "user", "content": prompt_to_send})

            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_to_send)

                with st.chat_message("assistant", avatar="🎸"):
                    with st.spinner("Consultando dados da loja..."):
                        try:
                            reply = st.session_state.chatbot.send_message(prompt_to_send)
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        except Exception as ex:
                            err_msg = f"Desculpe, ocorreu um erro ao consultar o sistema: {str(ex)}"
                            st.error(err_msg)
                            st.session_state.messages.append({"role": "assistant", "content": err_msg})
            st.rerun()
