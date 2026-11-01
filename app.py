"""
Streamlit UI for Empório da Música.
Modern Storefront with live catalog, interactive cart/checkout simulation,
light/dark theme toggle, sound notification, and a floating interactive AI widget.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from src.agent import EmporioChatbot
from src.data_loader import DataStore
from src.config import get_reference_date

# --- Page Configuration ---
st.set_page_config(
    page_title="Empório da Música — Loja Oficial & Atendimento IA",
    page_icon="🎸",
    layout="wide",
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

if "sound_played" not in st.session_state:
    st.session_state.sound_played = False


# --- Custom CSS for Themes, Storefront & Floating Widget ---
theme_vars = {
    "light": {
        "bg_color": "#f8fafc",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#0f172a",
        "text_secondary": "#64748b",
        "accent": "#d97706",
        "hero_bg": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        "hero_text": "#ffffff",
        "badge_bg": "#fef3c7",
        "badge_text": "#92400e",
        "chat_window_bg": "#ffffff",
    },
    "dark": {
        "bg_color": "#090d16",
        "card_bg": "#131b2e",
        "card_border": "#1e293b",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent": "#f59e0b",
        "hero_bg": "linear-gradient(135deg, #0f172a 0%, #020617 100%)",
        "hero_text": "#f8fafc",
        "badge_bg": "#78350f",
        "badge_text": "#fde68a",
        "chat_window_bg": "#131b2e",
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
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    .hero-title {{
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 0.3rem;
        margin-bottom: 0;
    }}
    .hero-pill-badge {{
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }}

    /* Product Cards */
    .product-card {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        border-radius: 14px;
        padding: 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}
    .product-category {{
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: {t['accent']};
        margin-bottom: 0.25rem;
    }}
    .product-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {t['text_primary']};
        margin-bottom: 0.4rem;
        line-height: 1.3;
    }}
    .product-desc {{
        font-size: 0.82rem;
        color: {t['text_secondary']};
        margin-bottom: 0.7rem;
        line-height: 1.4;
    }}
    .product-price {{
        font-size: 1.2rem;
        font-weight: 800;
        color: {t['text_primary']};
    }}
    .product-old-price {{
        font-size: 0.82rem;
        text-decoration: line-through;
        color: {t['text_secondary']};
        margin-right: 0.4rem;
    }}
    .promo-tag {{
        background: {t['badge_bg']};
        color: {t['badge_text']};
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.18rem 0.5rem;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 0.4rem;
    }}
    .stock-badge {{
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.2rem 0.55rem;
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

    /* Soft floating pills */
    .pill-info-bar {{
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 1.2rem;
    }}
    .pill-item {{
        background: {t['card_bg']};
        border: 1px solid {t['card_border']};
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        color: {t['text_secondary']};
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .pill-item strong {{
        color: {t['text_primary']};
    }}

    /* Floating Circle AI Chatbot Button (Bottom-Right) */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        bottom: 28px !important;
        right: 28px !important;
        z-index: 999999 !important;
    }}
    div[data-testid="stPopover"] > button {{
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 50% !important;
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        max-width: 62px !important;
        padding: 0 !important;
        font-size: 1.85rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 25px rgba(217, 119, 6, 0.5) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        animation: pulse-glow 2.5s infinite !important;
    }}
    div[data-testid="stPopover"] > button:hover {{
        transform: scale(1.12) !important;
        box-shadow: 0 14px 30px rgba(217, 119, 6, 0.75) !important;
    }}

    @keyframes pulse-glow {{
        0% {{ box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.6); }}
        70% {{ box-shadow: 0 0 0 14px rgba(217, 119, 6, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(217, 119, 6, 0); }}
    }}
</style>
""", unsafe_allow_html=True)


# --- Pleasant Greeting Sound Notification (Web Audio Synthesizer) ---
if not st.session_state.sound_played:
    st.markdown("""
    <script>
    (function() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const ctx = new AudioContext();
                const now = ctx.currentTime;
                // Note 1 (E5 - 659.25Hz)
                const osc1 = ctx.createOscillator();
                const gain1 = ctx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(659.25, now);
                gain1.gain.setValueAtTime(0.18, now);
                gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
                osc1.connect(gain1);
                gain1.connect(ctx.destination);
                osc1.start(now);
                osc1.stop(now + 0.35);

                // Note 2 (B5 - 987.77Hz - pleasant chime)
                const osc2 = ctx.createOscillator();
                const gain2 = ctx.createGain();
                osc2.type = 'sine';
                osc2.frequency.setValueAtTime(987.77, now + 0.12);
                gain2.gain.setValueAtTime(0.18, now + 0.12);
                gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
                osc2.connect(gain2);
                gain2.connect(ctx.destination);
                osc2.start(now + 0.12);
                osc2.stop(now + 0.6);
            }
        } catch(e) {
            console.log('Audio notification initialized on user gesture');
        }
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state.sound_played = True


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
        st.markdown(f"**🛒 Carrinho:** `{total_items_in_cart}`")

# --- Hero Banner ---
ref_date = get_reference_date()
st.markdown(f"""
<div class="hero-container">
    <div>
        <h1 class="hero-title">Empório da Música</h1>
        <p class="hero-subtitle">Instrumentos musicais autênticos selecionados para músicos exigentes.</p>
    </div>
    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
        <div class="hero-pill-badge">📍 Campo Grande/MS</div>
        <div class="hero-pill-badge">📅 {ref_date.strftime('%d/%m/%Y')}</div>
        <div class="hero-pill-badge">⚡ Atendente Flutuante Ativo</div>
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

# --- Storefront Grid & Live Simulation Box ---
col_catalog, col_drawer = st.columns([2.8, 1.2])

with col_catalog:
    st.markdown(f"#### Catálogo de Instrumentos ({len(df_products)} disponíveis)")

    if df_products.empty:
        st.info("Nenhum instrumento encontrado com os filtros selecionados.")
    else:
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df_products.iterrows()):
            p_id = int(row["product_id"])
            p_name = str(row["name"])
            p_price = float(row["price_brl"])
            p_stock = int(row["stock_quantity"])
            p_desc = str(row["description"])
            p_cat = str(st.session_state.store.get_category_name(int(row["category_id"])))
            p_promo = st.session_state.store.get_active_promotion(p_id)
            p_status = str(row["status"])

            with cols[idx % 3]:
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

                clean_desc = p_desc[:110] + "..." if len(p_desc) > 110 else p_desc
                card_content = (
                    f'<div class="product-card">'
                    f'<div>'
                    f'<div class="product-category">{p_cat}</div>'
                    f'<div class="product-title">{p_name}</div>'
                    f'{promo_badge_html}'
                    f'<div class="product-desc">{clean_desc}</div>'
                    f'</div>'
                    f'<div style="margin-top: 0.6rem; display: flex; justify-content: space-between; align-items: baseline;">'
                    f'{price_html}'
                    f'{stock_html}'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_content, unsafe_allow_html=True)

                btn_c1, btn_c2 = st.columns([1, 1])
                with btn_c1:
                    can_buy = p_stock > 0 and p_status == "active"
                    if st.button("🛒 Comprar", key=f"buy_{p_id}", disabled=not can_buy, use_container_width=True):
                        st.session_state.cart[p_id] = st.session_state.cart.get(p_id, 0) + 1
                        st.session_state.store.adjust_product_stock(p_id, -1)
                        st.session_state.toast_msg = f"{p_name} adicionado ao carrinho! Estoque atualizado."
                        st.rerun()

                with btn_c2:
                    if st.button("💬 Perguntar", key=f"chat_{p_id}", use_container_width=True):
                        st.session_state.active_chat_prompt = f"Gostaria de saber mais sobre o instrumento '{p_name}'. Qual o preço e o estoque atual?"
                        st.session_state.toast_msg = "Abra o Atendente Flutuante no canto inferior direito para conversar!"
                        st.rerun()

                st.write("")

with col_drawer:
    st.markdown("#### 🛍️ Carrinho & Simulação")
    st.caption("Compras alteram o estoque no sistema em tempo real.")

    if not st.session_state.cart:
        st.info("Seu carrinho está vazio.")
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

                cart_c1, cart_c2 = st.columns([3, 1])
                with cart_c1:
                    st.markdown(f"**{prod['name']}**")
                    st.caption(f"{qty}x {format_currency(price)} = **{format_currency(subtotal)}**")
                with cart_c2:
                    if st.button("❌", key=f"del_cart_{cart_p_id}"):
                        st.session_state.store.adjust_product_stock(cart_p_id, qty)
                        del st.session_state.cart[cart_p_id]
                        st.rerun()
                st.divider()

        st.markdown(f"**Total: {format_currency(total_order_val)}**")
        st.caption(f"À vista no PIX (5% off): **{format_currency(total_order_val * 0.95)}**")

        if st.button("Finalizar Pedido Simulado", use_container_width=True, type="primary"):
            st.session_state.cart = {}
            st.success("Pedido concluído! Estoque reduzido na sessão.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🔧 Teste de Estoque ao Vivo")
    st.caption("Altere o estoque de qualquer instrumento e pergunte para o chatbot:")

    all_names = st.session_state.store.products["name"].tolist()
    test_product_name = st.selectbox("Selecione um instrumento:", options=all_names, key="stock_test_select")
    p_row = st.session_state.store.products[st.session_state.store.products["name"] == test_product_name].iloc[0]
    curr_qty = int(p_row["stock_quantity"])

    stock_col1, stock_col2 = st.columns([1, 1])
    with stock_col1:
        new_stock_val = st.number_input("Estoque:", min_value=0, max_value=999, value=curr_qty, key=f"num_stock_{p_row['product_id']}")
    with stock_col2:
        st.write("")
        st.write("")
        if st.button("Atualizar", key="btn_apply_stock", use_container_width=True):
            st.session_state.store.update_product_stock(int(p_row["product_id"]), int(new_stock_val))
            st.session_state.toast_msg = f"Estoque de '{test_product_name}' alterado para {new_stock_val}!"
            st.rerun()


# =========================================================
# FLOATING WIDGET AT BOTTOM-RIGHT: ATENDENTE VIRTUAL POPUP
# =========================================================
with st.popover("🤖", use_container_width=False):
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
        <div>
            <h4 style="margin: 0; color: {t['text_primary']};">🎸 Empório da Música</h4>
            <span style="font-size: 0.8rem; color: {t['text_secondary']};">Assistente Virtual Inteligente (conectado ao estoque)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chatbot_ready:
        st.error(f"Erro ao inicializar IA: {st.session_state.get('chatbot_error', 'Verifique a GEMINI_API_KEY')}")
    else:
        top_btn1, top_btn2 = st.columns([2, 1])
        with top_btn2:
            if st.button("🧹 Limpar", key="clear_popover_chat"):
                st.session_state.messages = []
                st.session_state.chatbot.reset_history()
                st.rerun()

        # Conversation Box
        chat_box = st.container(height=380)

        with chat_box:
            # Welcoming message
            if not st.session_state.messages:
                welcome_text = (
                    "Olá! 👋 Bem-vindo(a) à **Empório da Música**! Sou o seu assistente virtual.\n\n"
                    "Posso te ajudar com dúvidas sobre instrumentos, checar **preços e estoques em tempo real**, "
                    "consultar **pedidos e rastreamento**, ou informar sobre nossas **políticas de garantia e devolução**.\n\n"
                    "Como posso te ajudar agora? 🎵"
                )
                with st.chat_message("assistant", avatar="🎸"):
                    st.markdown(welcome_text)

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🎸" if msg["role"] == "assistant" else None):
                    st.markdown(msg["content"])

        # Auto-fill from catalog 'Perguntar' button
        pre_prompt = None
        if "active_chat_prompt" in st.session_state and st.session_state.active_chat_prompt:
            pre_prompt = st.session_state.active_chat_prompt
            del st.session_state.active_chat_prompt

        chat_input_val = st.chat_input("Digite sua dúvida aqui...")

        prompt_to_send = chat_input_val or pre_prompt

        if prompt_to_send:
            st.session_state.messages.append({"role": "user", "content": prompt_to_send})

            with chat_box:
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
