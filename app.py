"""
Empório da Música — Boutique Digital de Instrumentos Musicais Nobres.
Identidade: Dark Luxury Atelier (Preto Profundo #0b0d12, Grafite #11141c, Nogueira #1b1712, Ouro Envelhecido/Bronze #d1b48c).
Estrutura:
1. Faixa Superior Fina de Informações (endereço, horário, pagamento, garantia, WhatsApp).
2. Cabeçalho de Marca Refinado + Apresentação Editorial com Hero Banner de Luthieria.
3. Barra de Busca e Filtro de Famílias.
4. Catálogo em Carrosséis Horizontais por Família (Violões [35], Ukuleles [15], Guitarras [5], Baixos [4], Baterias [3], Teclados [3]).
5. Cards com Imagens Autênticas (WebP e Silhuetas Vetoriais Nobres), Preços, Promoções e Botões de Ação Direta.
6. Consultor Virtual Especializado (Concierge de IA) Flutuante no Canto Inferior Esquerdo (🤖).
7. Sacola de Compras Flutuante no Canto Inferior Direito (👜).
"""

import streamlit as st
import html
from typing import Optional
from src.agent import EmporioChatbot
from src.data_loader import DataStore
from src.config import get_reference_date
from src.image_resolver import get_product_image_src, get_hero_banner_base64

# --- Page Configuration ---
st.set_page_config(
    page_title="Empório da Música — Boutique de Instrumentos Nobres",
    page_icon="🎻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Session State Setup ---
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

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Todas"

if "max_price" not in st.session_state:
    st.session_state.max_price = 25000.0

if "toast_msg" not in st.session_state:
    st.session_state.toast_msg = None


# --- Format Helpers ---
def fmt_price(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Handle Direct Card Clicks via Query Parameters ---
if "add_to_cart" in st.query_params:
    try:
        p_to_buy = int(st.query_params["add_to_cart"])
        prod = st.session_state.store.get_product_by_id(p_to_buy)
        if prod and prod["status"] == "active" and prod["stock_quantity"] > 0:
            st.session_state.cart[p_to_buy] = st.session_state.cart.get(p_to_buy, 0) + 1
            st.session_state.store.adjust_product_stock(p_to_buy, -1)
            st.session_state.toast_msg = f"{prod['name']} adicionado à sua sacola!"
        elif prod and prod["stock_quantity"] <= 0:
            st.session_state.toast_msg = f"Instrumento {prod['name']} está esgotado no momento."
    except Exception:
        pass
    del st.query_params["add_to_cart"]

if "consult_prod" in st.query_params:
    try:
        p_to_consult = int(st.query_params["consult_prod"])
        prod = st.session_state.store.get_product_by_id(p_to_consult)
        if prod:
            st.session_state.active_chat_prompt = (
                f"Gostaria de uma consultoria sobre o instrumento '{prod['name']}'. "
                f"Qual o valor, especificações e disponibilidade em acervo?"
            )
            st.session_state.toast_msg = "Consultoria iniciada! Abra o Concierge no canto inferior esquerdo."
    except Exception:
        pass
    del st.query_params["consult_prod"]


# --- Dark Boutique Atelier CSS Stylesheet ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Foundation */
    .stApp {
        background-color: #0b0d12 !important;
        color: #e8dfd5 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Top Ribbon Info Bar */
    .boutique-top-ribbon {
        background-color: #06070a;
        border-bottom: 1px solid #1a1e28;
        padding: 0.6rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        font-size: 0.77rem;
        color: #9aa2b5;
        letter-spacing: 0.04em;
    }
    .ribbon-group {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        flex-wrap: wrap;
    }
    .ribbon-item {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }
    .ribbon-item strong {
        color: #d1b48c;
        font-weight: 600;
    }
    .ribbon-sep {
        color: #2b303e;
    }

    /* Main Brand Header */
    .brand-header {
        padding: 1.8rem 1.5rem 1.2rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid #161a24;
        margin-bottom: 1.8rem;
    }
    .brand-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #f7efe6;
        margin: 0;
        line-height: 1;
    }
    .brand-tagline {
        font-size: 0.78rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #a68a68;
        margin-top: 0.4rem;
    }

    /* Editorial Hero Presentation */
    .hero-editorial {
        background: radial-gradient(circle at 60% 40%, #161b26 0%, #0c0f16 100%);
        border: 1px solid #202636;
        border-radius: 4px;
        display: grid;
        grid-template-columns: 1.25fr 0.75fr;
        overflow: hidden;
        margin: 0 1.5rem 2.5rem 1.5rem;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.45);
    }
    @media (max-width: 900px) {
        .hero-editorial { grid-template-columns: 1fr; }
    }
    .hero-content {
        padding: 3rem 2.8rem 2.6rem 2.8rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-badge {
        font-size: 0.74rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #d1b48c;
        font-weight: 600;
        margin-bottom: 0.7rem;
    }
    .hero-heading {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.8rem;
        line-height: 1.12;
        font-weight: 600;
        color: #f7efe6;
        margin: 0 0 1rem 0;
    }
    .hero-heading em {
        font-style: italic;
        color: #e2c196;
        font-weight: 400;
    }
    .hero-text {
        font-size: 0.92rem;
        line-height: 1.65;
        color: #a4adbd;
        max-width: 520px;
        margin-bottom: 1.4rem;
    }
    .hero-bg-img {
        height: 100%;
        min-height: 350px;
        background-size: cover;
        background-position: center;
        border-left: 1px solid #202636;
    }

    /* Carousel Categories Header */
    .section-editorial-header {
        margin: 2.5rem 1.5rem 0.8rem 1.5rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #1a1e28;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .section-editorial-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: #f7efe6;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-item-count {
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #a68a68;
    }

    /* Horizontal Carousel Track */
    .carousel-track {
        display: flex;
        gap: 1.25rem;
        overflow-x: auto;
        padding: 0.6rem 1.5rem 1.5rem 1.5rem;
        scroll-snap-type: x mandatory;
        scrollbar-width: thin;
        scrollbar-color: #2b3140 transparent;
    }
    .carousel-track::-webkit-scrollbar {
        height: 6px;
    }
    .carousel-track::-webkit-scrollbar-thumb {
        background: #2b3140;
        border-radius: 3px;
    }
    .carousel-track::-webkit-scrollbar-track {
        background: transparent;
    }

    /* Product Card in Dark Luxury Atelier */
    .boutique-card {
        flex: 0 0 280px;
        scroll-snap-align: start;
        background: #11141c;
        border: 1px solid #1f2533;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
        position: relative;
    }
    .boutique-card:hover {
        transform: translateY(-5px);
        border-color: #8c704f;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55);
    }
    .card-img-container {
        width: 100%;
        height: 230px;
        background-color: #090b0f;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-bottom: 1px solid #1a202c;
    }
    .card-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        transition: transform 0.35s ease;
    }
    .boutique-card:hover .card-img {
        transform: scale(1.05);
    }
    .card-body {
        padding: 1.15rem 1.15rem 0.6rem 1.15rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .card-category {
        font-size: 0.68rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 600;
        color: #bfa17c;
        margin-bottom: 0.25rem;
    }
    .card-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #f7efe6;
        line-height: 1.25;
        margin: 0 0 0.5rem 0;
        min-height: 3.2rem;
    }
    .card-desc {
        font-size: 0.79rem;
        line-height: 1.45;
        color: #8e97a8;
        margin-bottom: 0.8rem;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .card-price-row {
        margin-top: auto;
        padding-top: 0.75rem;
        border-top: 1px solid #1a202c;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .card-price {
        font-size: 1.15rem;
        font-weight: 700;
        color: #f7efe6;
    }
    .card-price-old {
        font-size: 0.8rem;
        text-decoration: line-through;
        color: #636b7b;
        margin-right: 0.35rem;
    }
    .card-badge-promo {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #2b1f13;
        border: 1px solid #73532c;
        color: #f0caa3;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.25rem 0.6rem;
        border-radius: 2px;
        z-index: 2;
    }
    .card-stock-label {
        font-size: 0.72rem;
        font-weight: 500;
    }

    /* Embedded Card Action Buttons */
    .card-actions {
        padding: 0.6rem 1.15rem 1.15rem 1.15rem;
        display: flex;
        gap: 0.5rem;
    }
    .btn-boutique-add {
        flex: 1.2;
        background: #1b1712;
        color: #e5cfab !important;
        border: 1px solid #73532c;
        border-radius: 3px;
        padding: 0.5rem 0.6rem;
        font-size: 0.76rem;
        font-weight: 600;
        text-align: center;
        text-decoration: none !important;
        letter-spacing: 0.04em;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    .btn-boutique-add:hover {
        background: #2f2317;
        border-color: #d1b48c;
        color: #ffffff !important;
    }
    .btn-boutique-consult {
        flex: 0.9;
        background: #12151e;
        color: #9aa2b5 !important;
        border: 1px solid #232b3d;
        border-radius: 3px;
        padding: 0.5rem 0.6rem;
        font-size: 0.74rem;
        font-weight: 500;
        text-align: center;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
    }
    .btn-boutique-consult:hover {
        background: #1a202c;
        border-color: #4a5568;
        color: #e8dfd5 !important;
    }
    .btn-boutique-disabled {
        flex: 1.2;
        background: #151821;
        color: #555e70;
        border: 1px solid #202636;
        border-radius: 3px;
        padding: 0.5rem 0.6rem;
        font-size: 0.74rem;
        text-align: center;
        cursor: not-allowed;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    /* Floating Anchors */
    #concierge-anchor, #cart-anchor {
        display: none;
    }

    /* Floating Concierge Popover (Bottom Left) */
    div[data-testid="stElementContainer"]:has(#concierge-anchor) + div[data-testid="stElementContainer"] {
        position: fixed !important;
        bottom: 24px !important;
        left: 24px !important;
        z-index: 999999 !important;
        width: auto !important;
        height: auto !important;
    }
    div[data-testid="stElementContainer"]:has(#concierge-anchor) + div[data-testid="stElementContainer"] div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #1d1813 0%, #0d0f15 100%) !important;
        color: #e5cfab !important;
        border: 2px solid #8c704f !important;
        border-radius: 50% !important;
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        max-width: 62px !important;
        min-height: 62px !important;
        max-height: 62px !important;
        padding: 0 !important;
        font-size: 1.85rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.75), 0 0 18px rgba(209, 180, 140, 0.3) !important;
        cursor: pointer !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stElementContainer"]:has(#concierge-anchor) + div[data-testid="stElementContainer"] div[data-testid="stPopover"] > button:hover {
        transform: scale(1.1) !important;
        border-color: #d1b48c !important;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.9), 0 0 25px rgba(209, 180, 140, 0.55) !important;
    }

    /* Floating Cart Popover (Bottom Right) */
    div[data-testid="stElementContainer"]:has(#cart-anchor) + div[data-testid="stElementContainer"] {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 999999 !important;
        width: auto !important;
        height: auto !important;
    }
    div[data-testid="stElementContainer"]:has(#cart-anchor) + div[data-testid="stElementContainer"] div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #1d1813 0%, #0d0f15 100%) !important;
        color: #e5cfab !important;
        border: 2px solid #8c704f !important;
        border-radius: 50% !important;
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        max-width: 62px !important;
        min-height: 62px !important;
        max-height: 62px !important;
        padding: 0 !important;
        font-size: 1.35rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.75), 0 0 18px rgba(209, 180, 140, 0.3) !important;
        cursor: pointer !important;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stElementContainer"]:has(#cart-anchor) + div[data-testid="stElementContainer"] div[data-testid="stPopover"] > button:hover {
        transform: scale(1.1) !important;
        border-color: #d1b48c !important;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.9), 0 0 25px rgba(209, 180, 140, 0.55) !important;
    }

    /* Popover Dialog Surfaces */
    div[data-testid="stPopoverBody"] {
        background-color: #0e1118 !important;
        border: 1px solid #33271a !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.85), 0 0 20px rgba(209, 180, 140, 0.15) !important;
        border-radius: 8px !important;
        color: #e8dfd5 !important;
        width: 440px !important;
        max-width: 92vw !important;
    }

    /* Dark Chat Styling inside Popover */
    [data-testid="stChatMessage"] {
        background-color: #121620 !important;
        border: 1px solid #1c2230 !important;
        border-radius: 6px !important;
        margin-bottom: 0.5rem !important;
    }

    /* Custom Form & Input Dark Theming */
    .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #11141c !important;
        border-color: #202636 !important;
        color: #e8dfd5 !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
        border-color: #8c704f !important;
    }
</style>
""", unsafe_allow_html=True)




# --- 1. Top Ribbon Information Bar ---
ref_date = get_reference_date()
cart_qty_total = sum(st.session_state.cart.values())

st.markdown(f"""
<div class="boutique-top-ribbon">
    <div class="ribbon-group">
        <span class="ribbon-item">📍 <strong>Rua 14 de Maio, 3200 &bull; Centro, Campo Grande/MS</strong></span>
        <span class="ribbon-sep">|</span>
        <span class="ribbon-item">🕒 Atendimento: <strong>Seg–Sex 09h às 18h &bull; Sáb 09h às 13h</strong></span>
    </div>
    <div class="ribbon-group">
        <span class="ribbon-item">💳 <strong>5% OFF no PIX ou até 12x s/ juros</strong></span>
        <span class="ribbon-sep">|</span>
        <span class="ribbon-item">🛡️ Garantia: <strong>90 dias legal + Fabricante</strong></span>
        <span class="ribbon-sep">|</span>
        <span class="ribbon-item">📞 WhatsApp: <strong>(67) 3321-4500</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 2. Brand Header ---
st.markdown("""
<div class="brand-header">
    <div>
        <h1 class="brand-title">Empório da Música</h1>
        <div class="brand-tagline">Atelier & Acervo de Instrumentos Musicais Nobres &bull; Desde 2008</div>
    </div>
    <div style="font-size: 0.82rem; color: #a4adbd; letter-spacing: 0.06em;">
        Atendimento e Luthieria Especializada em Campo Grande
    </div>
</div>
""", unsafe_allow_html=True)


# --- 3. Editorial Hero Presentation ---
hero_base64 = get_hero_banner_base64()
st.markdown(f"""
<div class="hero-editorial">
    <div class="hero-content">
        <div class="hero-badge">Coleção Exclusiva de Luthieria</div>
        <h2 class="hero-heading">A nobreza sonora talhada em <em>madeiras nobres</em>.</h2>
        <p class="hero-text">
            Do som cristalino dos violões dreadnought e clássicos concertistas às lendas elétricas e percussão de estúdio. Cada peça de nosso acervo passa por rigorosa calibragem técnica.
        </p>
        <div style="font-size: 0.8rem; color: #d1b48c; letter-spacing: 0.08em; text-transform: uppercase;">
            Utilize os controles flutuantes no rodapé para consultar nosso Concierge de IA (🤖) ou acessar sua sacola (👜).
        </div>
    </div>
    <div class="hero-bg-img" style="background-image: url('{hero_base64}');"></div>
</div>
""", unsafe_allow_html=True)


# --- Toast Notification ---
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="✨")
    st.session_state.toast_msg = None


# --- 4. Search and Filter Bar ---
filter_col1, filter_col2, filter_col3 = st.columns([2.4, 1.3, 1.3])
categories_all = ["Todas"] + sorted(st.session_state.store.categories["name"].tolist())

with filter_col1:
    search_text = st.text_input(
        "Buscar no acervo",
        value=st.session_state.search_query,
        placeholder="Ex: Takamine GD20, Martin D-28, Fender, Nylon, Cedro...",
        label_visibility="collapsed",
    )
    st.session_state.search_query = search_text

with filter_col2:
    cat_chosen = st.selectbox(
        "Família",
        categories_all,
        index=categories_all.index(st.session_state.selected_category) if st.session_state.selected_category in categories_all else 0,
        label_visibility="collapsed",
    )
    st.session_state.selected_category = cat_chosen

with filter_col3:
    max_p = st.slider(
        "Preço limite",
        min_value=150.0,
        max_value=25000.0,
        value=float(st.session_state.max_price),
        step=100.0,
        label_visibility="collapsed",
    )
    st.session_state.max_price = max_p


# --- 5. Catalog Grouped by Family Carousels ---
# Filter products
df_filtered = st.session_state.store.products.copy()

if cat_chosen != "Todas":
    cat_rec = st.session_state.store.categories[st.session_state.store.categories["name"] == cat_chosen]
    if not cat_rec.empty:
        df_filtered = df_filtered[df_filtered["category_id"] == cat_rec.iloc[0]["category_id"]]

if search_text:
    term_l = search_text.strip().lower()
    df_filtered = df_filtered[
        df_filtered["name"].str.lower().str.contains(term_l, na=False) |
        df_filtered["description"].str.lower().str.contains(term_l, na=False)
    ]

df_filtered = df_filtered[df_filtered["price_brl"] <= max_p]

# Family groups according to brief:
# Violões (35), Ukuleles (15), Guitarras (5), Baixos (4), Baterias (3), Teclados (3)
category_order = [
    "Violões",
    "Ukuleles",
    "Guitarras",
    "Baixos",
    "Baterias e Percussão",
    "Teclados e Pianos",
]

total_matching = len(df_filtered)

if total_matching == 0:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 1.5rem; color: #8e97a8;">
        <h4 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:1.8rem; color:#f7efe6;">Nenhum instrumento localizado</h4>
        <p>Ajuste os filtros de busca ou preço para encontrar peças no acervo.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for cat_name in category_order:
        cat_match = st.session_state.store.categories[st.session_state.store.categories["name"] == cat_name]
        if cat_match.empty:
            continue
        c_id = cat_match.iloc[0]["category_id"]
        group_df = df_filtered[df_filtered["category_id"] == c_id].sort_values(by="price_brl")

        if group_df.empty:
            continue

        st.markdown(f"""
        <div class="section-editorial-header">
            <h3 class="section-editorial-title">
                <span>🎻</span> {cat_name}
            </h3>
            <span class="section-item-count">{len(group_df)} {('peça' if len(group_df) == 1 else 'peças')} em exposição &bull; Deslize para navegar &rarr;</span>
        </div>
        """, unsafe_allow_html=True)

        # Build cards HTML for horizontal track
        cards_html = ""
        for _, prod_row in group_df.iterrows():
            prod_id = int(prod_row["product_id"])
            prod_name = html.escape(str(prod_row["name"]))
            prod_price = float(prod_row["price_brl"])
            prod_stock = int(prod_row["stock_quantity"])
            prod_desc = html.escape(str(prod_row["description"]))
            prod_status = str(prod_row["status"])
            prod_promo = st.session_state.store.get_active_promotion(prod_id)

            # Get image (validated webp or bespoke luxury SVG placeholder)
            img_src = get_product_image_src(prod_id, prod_row["name"], cat_name)

            # Price and Promo
            if prod_promo:
                pct = prod_promo["discount_percent"]
                final_val = prod_price * (1 - pct / 100)
                promo_tag = f'<div class="card-badge-promo">{pct:.0f}% OFF &bull; {html.escape(prod_promo["description"])}</div>'
                price_html = f'<div><span class="card-price-old">{fmt_price(prod_price)}</span><span class="card-price" style="color:#d97736;">{fmt_price(final_val)}</span></div>'
            else:
                promo_tag = ""
                price_html = f'<span class="card-price">{fmt_price(prod_price)}</span>'

            # Stock and availability
            if prod_status == "discontinued":
                stock_tag = '<span class="card-stock-label" style="color:#b91c1c;">Fora de Linha</span>'
                action_btn = '<span class="btn-boutique-disabled">Fora de Linha</span>'
            elif prod_status == "coming_soon":
                stock_tag = '<span class="card-stock-label" style="color:#b45309;">Em Breve</span>'
                action_btn = '<span class="btn-boutique-disabled">Em Breve</span>'
            elif prod_stock <= 0:
                stock_tag = '<span class="card-stock-label" style="color:#b91c1c;">Esgotado</span>'
                action_btn = '<span class="btn-boutique-disabled">Esgotado</span>'
            elif prod_stock <= 3:
                stock_tag = f'<span class="card-stock-label" style="color:#b45309;">Resta {prod_stock}</span>'
                action_btn = f'<a href="?add_to_cart={prod_id}" target="_self" class="btn-boutique-add">+ Sacola</a>'
            else:
                stock_tag = f'<span class="card-stock-label" style="color:#637189;">{prod_stock} em acervo</span>'
                action_btn = f'<a href="?add_to_cart={prod_id}" target="_self" class="btn-boutique-add">+ Sacola</a>'

            consult_btn = f'<a href="?consult_prod={prod_id}" target="_self" class="btn-boutique-consult">Consultar</a>'

            # Pure HTML card without unescaped tags
            cards_html += f"""
            <div class="boutique-card">
                {promo_tag}
                <div class="card-img-container">
                    <img src="{img_src}" class="card-img" alt="{prod_name}" loading="lazy"/>
                </div>
                <div class="card-body">
                    <div class="card-category">{cat_name}</div>
                    <div class="card-title">{prod_name}</div>
                    <div class="card-desc">{prod_desc}</div>
                    <div class="card-price-row">
                        {price_html}
                        {stock_tag}
                    </div>
                </div>
                <div class="card-actions">
                    {action_btn}
                    {consult_btn}
                </div>
            </div>
            """

        # Wrap in carousel track
        carousel_markup = f"""
        <div class="carousel-track">
            {cards_html}
        </div>
        """
        st.markdown(carousel_markup, unsafe_allow_html=True)


# =========================================================
# FLOATING WIDGET 1: AGENTE DE IA CONCIERGE (CANTO INFERIOR ESQUERDO)
# =========================================================
st.markdown('<div id="concierge-anchor"></div>', unsafe_allow_html=True)

with st.popover("🤖", use_container_width=False, help="Consultor Virtual Especializado (Concierge de Luthieria)"):
    st.markdown("""
    <div style="border-bottom: 1px solid #232a3b; padding-bottom: 0.8rem; margin-bottom: 0.8rem;">
        <div style="font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase; color: #d1b48c; font-weight: 600;">
            Atendimento Especializado
        </div>
        <h4 style="font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.5rem; margin: 0.2rem 0 0 0; color: #f7efe6;">
            Concierge Empório da Música
        </h4>
        <div style="font-size: 0.78rem; color: #8e97a8; margin-top: 0.2rem;">
            Consultoria sobre madeiras nobres, timbres, estoque e regras de garantia.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chatbot_ready:
        st.error(f"Concierge temporariamente indisponível: {st.session_state.get('chatbot_error', 'Verifique a chave de API.')}")
    else:
        # Quick suggestions
        st.caption("Consultas rápidas recomendadas:")
        q_cols = st.columns(2)
        with q_cols[0]:
            if st.button("🎻 Violões até R$ 1.000", key="quick_violao", use_container_width=True):
                st.session_state.active_chat_prompt = "Quais opções de violões disponíveis vocês têm custando até R$ 1.000?"
                st.rerun()
        with q_cols[1]:
            if st.button("🏷️ Promoções ativas", key="quick_promos", use_container_width=True):
                st.session_state.active_chat_prompt = "Quais instrumentos estão com promoção ativa no momento?"
                st.rerun()

        # Chat container
        chat_box = st.container(height=360)

        with chat_box:
            if not st.session_state.messages:
                welcome_msg = (
                    "Olá! Seja muito bem-vindo(a) ao **Empório da Música**.\n\n"
                    "Sou o consultor virtual da casa. Posso auxiliá-lo(a) a escolher o instrumento ideal, "
                    "verificar características de construção e timbres, consultar a disponibilidade em nosso acervo "
                    "ou esclarecer dúvidas sobre condições de pagamento e garantias.\n\n"
                    "Como posso servi-lo(a) hoje? 🎵"
                )
                with st.chat_message("assistant", avatar="🎻"):
                    st.markdown(welcome_msg)

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🎻" if msg["role"] == "assistant" else None):
                    st.markdown(msg["content"])

        # Input handling
        pre_prompt = None
        if "active_chat_prompt" in st.session_state and st.session_state.active_chat_prompt:
            pre_prompt = st.session_state.active_chat_prompt
            del st.session_state.active_chat_prompt

        chat_input = st.chat_input("Consulte o concierge de luthieria...", key="concierge_chat_input")
        prompt_to_dispatch = chat_input or pre_prompt

        if prompt_to_dispatch:
            st.session_state.messages.append({"role": "user", "content": prompt_to_dispatch})

            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt_to_dispatch)

                with st.chat_message("assistant", avatar="🎻"):
                    with st.spinner("Consultando acervo..."):
                        try:
                            reply = st.session_state.chatbot.send_message(prompt_to_dispatch)
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        except Exception as ex:
                            err_msg = f"Desculpe, ocorreu uma instabilidade: {str(ex)}"
                            st.error(err_msg)
                            st.session_state.messages.append({"role": "assistant", "content": err_msg})
            st.rerun()


# =========================================================
# FLOATING WIDGET 2: SACOLA DE COMPRAS (CANTO INFERIOR DIREITO)
# =========================================================
st.markdown('<div id="cart-anchor"></div>', unsafe_allow_html=True)

with st.popover(f"👜 {cart_qty_total}", use_container_width=False, help="Sacola de Compras e Reserva"):
    st.markdown("""
    <div style="border-bottom: 1px solid #232a3b; padding-bottom: 0.6rem; margin-bottom: 0.8rem;">
        <h4 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:1.5rem; margin:0; color:#f7efe6;">
            👜 Sua Sacola
        </h4>
        <span style="font-size:0.76rem; color:#8e97a8;">Simulação de checkout e reserva de acervo</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("<p style='font-size:0.84rem; color:#8e97a8;'>Sua sacola de compras está vazia.</p>", unsafe_allow_html=True)
    else:
        order_sum = 0.0
        for cart_pid, q_ordered in list(st.session_state.cart.items()):
            p_obj = st.session_state.store.get_product_by_id(cart_pid)
            if p_obj:
                prc = float(p_obj["price_brl"])
                prm = st.session_state.store.get_active_promotion(cart_pid)
                if prm:
                    prc = prc * (1 - prm["discount_percent"] / 100)
                sub_val = prc * q_ordered
                order_sum += sub_val

                row_c1, row_c2 = st.columns([3, 1])
                with row_c1:
                    st.markdown(f"**{html.escape(p_obj['name'])}**<br><small style='color:#8e97a8;'>{q_ordered}x {fmt_price(prc)}</small>", unsafe_allow_html=True)
                with row_c2:
                    if st.button("✕", key=f"cart_del_{cart_pid}"):
                        st.session_state.store.adjust_product_stock(cart_pid, q_ordered)
                        del st.session_state.cart[cart_pid]
                        st.rerun()
                st.write("")

        st.markdown(f"""
        <div style="border-top: 1px solid #232a3b; padding-top: 0.8rem; margin-top: 0.5rem;">
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:1.1rem; color:#f7efe6;">
                <span>Total:</span>
                <span>{fmt_price(order_sum)}</span>
            </div>
            <div style="font-size:0.78rem; color:#d1b48c; margin-top:0.3rem;">
                À vista no PIX (5% desc.): <strong>{fmt_price(order_sum * 0.95)}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Concluir Reserva de Acervo", use_container_width=True, type="primary"):
            st.session_state.cart = {}
            st.success("Reserva confirmada com sucesso! Itens alocados na sessão.")
            st.rerun()
