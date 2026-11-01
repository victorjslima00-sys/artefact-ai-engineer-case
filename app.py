"""
Empório da Música — Loja Virtual & Atendimento Especializado
High-End Luxury Musical Instruments Storefront & Concierge AI Consultant.
Crafted with bespoke typography, warm ivory/sand palette, polished brass accents,
and a floating dedicated AI Concierge.
"""

import streamlit as st
import html
from typing import Optional
from src.agent import EmporioChatbot
from src.data_loader import DataStore
from src.config import get_reference_date
from src.image_helper import get_product_image_data_uri, get_image_base64, HERO_IMG_PATH, ACOUSTIC_IMG_PATH

# --- Page Configuration ---
st.set_page_config(
    page_title="Empório da Música — Instrumentos Musicais Nobres",
    page_icon="🎻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- State Management ---
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
    st.session_state.cart = {}

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Todas"

if "max_price" not in st.session_state:
    st.session_state.max_price = 25000.0

if "toast_msg" not in st.session_state:
    st.session_state.toast_msg = None

if "sound_played" not in st.session_state:
    st.session_state.sound_played = False


# --- Elegant Luxury CSS Stylesheet ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Foundation */
    .stApp {
        background-color: #fcfbf9 !important;
        color: #1a1612 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Luxury Header Topbar */
    .top-announcement {
        background-color: #1a1612;
        color: #d8c29d;
        text-align: center;
        padding: 0.45rem 1rem;
        font-size: 0.76rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 500;
        border-bottom: 1px solid #332b24;
    }

    .boutique-header {
        padding: 1.6rem 0 1.2rem 0;
        border-bottom: 1px solid #eae5dc;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 2rem;
    }
    .brand-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #1a1612;
        margin: 0;
        line-height: 1;
    }
    .brand-subtitle {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #8a7a68;
        margin-top: 0.35rem;
    }

    /* Hero Presentation */
    .hero-editorial {
        background-color: #f4efe6;
        border: 1px solid #e5ded3;
        border-radius: 4px;
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        overflow: hidden;
        margin-bottom: 2.8rem;
        box-shadow: 0 12px 30px -10px rgba(38, 28, 20, 0.06);
    }
    @media (max-width: 900px) {
        .hero-editorial { grid-template-columns: 1fr; }
    }
    .hero-content {
        padding: 3.5rem 3.5rem 3rem 3.5rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-tagline {
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #9e7d56;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .hero-headline {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 3rem;
        line-height: 1.08;
        font-weight: 600;
        color: #1a1612;
        margin: 0 0 1.2rem 0;
    }
    .hero-headline em {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-style: italic;
        font-weight: 400;
        color: #8c6843;
    }
    .hero-copy {
        font-size: 0.95rem;
        line-height: 1.65;
        color: #5a4f43;
        max-width: 480px;
        margin-bottom: 1.8rem;
    }
    .hero-image-wrap {
        height: 100%;
        min-height: 380px;
        background-size: cover;
        background-position: center;
    }

    /* Minimal Floating Info Ribbon */
    .luxury-ribbon {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.4rem;
        background: #ffffff;
        border: 1px solid #eae5dc;
        border-radius: 3px;
        margin-bottom: 2.2rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .ribbon-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.82rem;
        color: #6a5e52;
    }
    .ribbon-item strong {
        color: #1a1612;
        font-weight: 600;
    }
    .ribbon-sep {
        color: #dcd4c7;
    }

    /* Product Cards - Boutique Atelier Look */
    .atelier-card {
        background: #ffffff;
        border: 1px solid #eae5dc;
        border-radius: 2px;
        padding: 0;
        margin-bottom: 1.6rem;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.28s ease, border-color 0.28s ease;
        position: relative;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .atelier-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 32px -8px rgba(35, 25, 15, 0.08);
        border-color: #c9b497;
    }
    .atelier-img-container {
        width: 100%;
        height: 240px;
        background-color: #f7f4ed;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #f1ece4;
    }
    .atelier-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        transition: transform 0.4s ease;
    }
    .atelier-card:hover .atelier-img {
        transform: scale(1.04);
    }
    .atelier-body {
        padding: 1.3rem 1.4rem 1.1rem 1.4rem;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .atelier-cat {
        font-size: 0.68rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        font-weight: 600;
        color: #9e7d56;
        margin-bottom: 0.35rem;
    }
    .atelier-name {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #1a1612;
        margin-bottom: 0.45rem;
        line-height: 1.22;
        min-height: 3.2rem;
    }
    .atelier-desc {
        font-size: 0.81rem;
        line-height: 1.5;
        color: #6a5e52;
        margin-bottom: 1rem;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .atelier-footer {
        padding-top: 0.8rem;
        border-top: 1px solid #f2ede5;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .atelier-price {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a1612;
    }
    .atelier-price-old {
        font-size: 0.8rem;
        color: #9c8e7f;
        text-decoration: line-through;
        margin-right: 0.4rem;
    }
    .atelier-badge-promo {
        position: absolute;
        top: 10px;
        left: 10px;
        background: #1a1612;
        color: #e5cfab;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.3rem 0.65rem;
        border-radius: 1px;
        z-index: 2;
    }
    .atelier-stock {
        font-size: 0.72rem;
        font-weight: 500;
        color: #706254;
    }

    /* Floating Circle AI Concierge Trigger Button (Bottom Right) */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 32px !important;
        z-index: 999999 !important;
    }
    div[data-testid="stPopover"] > button {
        background: #1a1612 !important;
        color: #d8c29d !important;
        border: 1px solid #4a3c30 !important;
        border-radius: 50% !important;
        width: 64px !important;
        height: 64px !important;
        min-width: 64px !important;
        max-width: 64px !important;
        padding: 0 !important;
        font-size: 1.7rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 14px 28px rgba(26, 22, 18, 0.28) !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    }
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.08) !important;
        background: #28211b !important;
        border-color: #d8c29d !important;
        box-shadow: 0 18px 36px rgba(26, 22, 18, 0.4) !important;
    }

    /* Clean Streamlit Chat Elements */
    [data-testid="stChatMessage"] {
        background-color: #f7f4ed !important;
        border: 1px solid #eae5dc !important;
        border-radius: 3px !important;
        margin-bottom: 0.7rem !important;
    }
    [data-testid="stChatMessage"] p {
        color: #1a1612 !important;
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
    }

    /* Cart & Checkout Drawer */
    .cart-box {
        background: #ffffff;
        border: 1px solid #eae5dc;
        border-radius: 2px;
        padding: 1.4rem;
        margin-bottom: 1.8rem;
    }
    .cart-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1a1612;
        margin: 0 0 0.8rem 0;
        border-bottom: 1px solid #f0eae1;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Pleasant Ambient Chime (Native Web Audio) ---
if not st.session_state.sound_played:
    st.markdown("""
    <script>
    (function() {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {
                const ctx = new AudioCtx();
                const now = ctx.currentTime;
                // Soft acoustic guitar harmonics chord (A major 432Hz inspired warm chime)
                [440, 554.37, 659.25].forEach((freq, idx) => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(freq, now + (idx * 0.08));
                    gain.gain.setValueAtTime(0.12, now + (idx * 0.08));
                    gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(now + (idx * 0.08));
                    osc.stop(now + 1.2);
                });
            }
        } catch(e) {}
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state.sound_played = True


# --- Format Helpers ---
def fmt_price(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Top Bar ---
ref_date = get_reference_date()
st.markdown(f"""
<div class="top-announcement">
    <span>Empório da Música &bull; Campo Grande, MS &bull; Instrumentos Autênticos com Garantia e Atendimento Especializado</span>
</div>
""", unsafe_allow_html=True)

# --- Header ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.markdown("""
    <div class="boutique-header" style="border:none; margin:0; padding:1.2rem 0 0.5rem 0;">
        <div>
            <h1 class="brand-title">Empório da Música</h1>
            <div class="brand-subtitle">Atelier & Instrumentos Musicais Nobres &bull; Desde 2008</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with h_col2:
    cart_count = sum(st.session_state.cart.values())
    st.markdown(f"""
    <div style="text-align: right; padding-top: 1.5rem;">
        <span style="font-size: 0.85rem; color: #706254; font-weight: 500;">
            👜 <strong>Sua Sacola:</strong> {cart_count} {('item' if cart_count == 1 else 'itens')}
        </span>
    </div>
    """, unsafe_allow_html=True)


# --- Hero Editorial Banner ---
hero_base64 = get_image_base64(HERO_IMG_PATH)
st.markdown(f"""
<div class="hero-editorial">
    <div class="hero-content">
        <div class="hero-tagline">Coleção Acústica &bull; Safra Exclusiva</div>
        <h2 class="hero-headline">Onde a <em>tradição sonora</em> encontra a perfeição artesanal.</h2>
        <p class="hero-copy">
            Cada instrumento é minuciosamente inspecionado por nossa luthieria em Campo Grande. Madeiras nobres, timbres aveludados e a garantia de quem compreende a paixão de tocar.
        </p>
        <div style="font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; color: #8a7a68;">
            Consulte nosso Concierge Virtual no canto inferior para recomendações sob medida.
        </div>
    </div>
    <div class="hero-image-wrap" style="background-image: url('{hero_base64}');"></div>
</div>
""", unsafe_allow_html=True)


# --- Luxury Ribbon Info Bar ---
st.markdown(f"""
<div class="luxury-ribbon">
    <div class="ribbon-item">
        <span>📍</span>
        <span>Atelier: <strong>Rua 14 de Maio, 3200 &bull; Campo Grande, MS</strong></span>
    </div>
    <span class="ribbon-sep">|</span>
    <div class="ribbon-item">
        <span>🕒</span>
        <span>Horário: <strong>Seg–Sex 09h–18h &bull; Sáb 09h–13h</strong></span>
    </div>
    <span class="ribbon-sep">|</span>
    <div class="ribbon-item">
        <span>💳</span>
        <span>Condições: <strong>5% OFF no PIX ou até 12x s/ juros</strong></span>
    </div>
    <span class="ribbon-sep">|</span>
    <div class="ribbon-item">
        <span>🛡️</span>
        <span>Garantia: <strong>90 dias CDC + Fabricante</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Toast Alert ---
if st.session_state.toast_msg:
    st.toast(st.session_state.toast_msg, icon="✨")
    st.session_state.toast_msg = None


# --- Filters & Search Bar ---
filter_col1, filter_col2, filter_col3 = st.columns([2.2, 1.4, 1.4])
categories = ["Todas"] + sorted(st.session_state.store.categories["name"].tolist())

with filter_col1:
    search_input = st.text_input("Buscar no catálogo", value=st.session_state.search_query, placeholder="Ex: Martin, Takamine GD20, Spruce, Violão Clássico...", label_visibility="collapsed")
    st.session_state.search_query = search_input

with filter_col2:
    cat_selected = st.selectbox("Categoria", categories, index=categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0, label_visibility="collapsed")
    st.session_state.selected_category = cat_selected

with filter_col3:
    price_val = st.slider("Preço até", min_value=150.0, max_value=25000.0, value=float(st.session_state.max_price), step=100.0, label_visibility="collapsed")
    st.session_state.max_price = price_val


# --- Filter Products Dataset ---
df_prods = st.session_state.store.products.copy()

if cat_selected != "Todas":
    cat_match = st.session_state.store.categories[st.session_state.store.categories["name"] == cat_selected]
    if not cat_match.empty:
        df_prods = df_prods[df_prods["category_id"] == cat_match.iloc[0]["category_id"]]

if search_input:
    s_term = search_input.strip().lower()
    df_prods = df_prods[
        df_prods["name"].str.lower().str.contains(s_term, na=False) |
        df_prods["description"].str.lower().str.contains(s_term, na=False)
    ]

df_prods = df_prods[df_prods["price_brl"] <= price_val]
df_prods = df_prods.sort_values(by="price_brl")


# --- Main Area: Product Grid (3 cols) & Right Atelier Drawer ---
grid_col, drawer_col = st.columns([2.85, 1.15])

with grid_col:
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.2rem; border-bottom: 1px solid #eae5dc; padding-bottom: 0.6rem;">
        <h3 style="font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.8rem; margin:0; color: #1a1612;">
            Acervo de Instrumentos
        </h3>
        <span style="font-size: 0.8rem; color: #8a7a68; letter-spacing: 0.05em;">
            {len(df_prods)} instrumentos disponíveis
        </span>
    </div>
    """, unsafe_allow_html=True)

    if df_prods.empty:
        st.info("Nenhum instrumento encontrado com os critérios selecionados.")
    else:
        grid_rows = st.columns(3)
        for idx, (_, row) in enumerate(df_prods.iterrows()):
            p_id = int(row["product_id"])
            p_name = html.escape(str(row["name"]))
            p_price = float(row["price_brl"])
            p_stock = int(row["stock_quantity"])
            p_desc = html.escape(str(row["description"]))
            p_cat = html.escape(str(st.session_state.store.get_category_name(int(row["category_id"]))))
            p_promo = st.session_state.store.get_active_promotion(p_id)
            p_status = str(row["status"])
            p_specs = row.get("specs_parsed", {})

            # Clean base64 image data URI
            img_data_uri = get_product_image_data_uri(row["name"], st.session_state.store.get_category_name(int(row["category_id"])), p_specs)

            with grid_rows[idx % 3]:
                promo_badge = ""
                price_render = f'<span class="atelier-price">{fmt_price(p_price)}</span>'

                if p_promo:
                    pct = p_promo["discount_percent"]
                    final_val = p_price * (1 - pct / 100)
                    promo_badge = f'<div class="atelier-badge-promo">{pct:.0f}% OFF &bull; {html.escape(p_promo["description"])}</div>'
                    price_render = f'<div><span class="atelier-price-old">{fmt_price(p_price)}</span><span class="atelier-price" style="color: #9e2a2b;">{fmt_price(final_val)}</span></div>'

                if p_status == "discontinued":
                    stock_label = '<span class="atelier-stock" style="color:#b91c1c;">Peça fora de linha</span>'
                elif p_status == "coming_soon":
                    stock_label = '<span class="atelier-stock" style="color:#b45309;">Em preparação</span>'
                elif p_stock <= 0:
                    stock_label = '<span class="atelier-stock" style="color:#b91c1c;">Esgotado</span>'
                elif p_stock <= 3:
                    stock_label = f'<span class="atelier-stock" style="color:#b45309;">Resta apenas {p_stock}</span>'
                else:
                    stock_label = f'<span class="atelier-stock">{p_stock} disponíveis</span>'

                clean_desc_text = p_desc[:105] + "..." if len(p_desc) > 105 else p_desc

                card_markup = f"""
                <div class="atelier-card">
                    {promo_badge}
                    <div class="atelier-img-container">
                        <img src="{img_data_uri}" class="atelier-img" alt="{p_name}" loading="lazy"/>
                    </div>
                    <div class="atelier-body">
                        <div class="atelier-cat">{p_cat}</div>
                        <div class="atelier-name">{p_name}</div>
                        <div class="atelier-desc">{clean_desc_text}</div>
                        <div class="atelier-footer">
                            {price_render}
                            {stock_label}
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_markup, unsafe_allow_html=True)

                btn1, btn2 = st.columns([1, 1])
                with btn1:
                    can_order = p_stock > 0 and p_status == "active"
                    if st.button("Reservar", key=f"res_{p_id}", disabled=not can_order, use_container_width=True):
                        st.session_state.cart[p_id] = st.session_state.cart.get(p_id, 0) + 1
                        st.session_state.store.adjust_product_stock(p_id, -1)
                        st.session_state.toast_msg = f"{p_name} adicionado à sua sacola!"
                        st.rerun()

                with btn2:
                    if st.button("Consultar Luthier", key=f"ask_{p_id}", use_container_width=True):
                        st.session_state.active_chat_prompt = f"Gostaria de uma consultoria técnica sobre o instrumento '{p_name}'. Qual o preço de tabela, especificações das madeiras e disponibilidade atual?"
                        st.session_state.toast_msg = "Consultoria iniciada! Abra o Concierge no canto inferior direito."
                        st.rerun()

                st.write("")


with drawer_col:
    # --- Luxury Atelier Cart Simulation ---
    st.markdown("""
    <div class="cart-box">
        <h4 class="cart-title">👜 Sacola de Compras</h4>
    """, unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("<p style='font-size:0.83rem; color:#8a7a68; margin:0;'>Sua sacola de compras está vazia.</p>", unsafe_allow_html=True)
    else:
        subtotal_acc = 0.0
        for c_id, qty in list(st.session_state.cart.items()):
            item_prod = st.session_state.store.get_product_by_id(c_id)
            if item_prod:
                it_price = float(item_prod["price_brl"])
                it_promo = st.session_state.store.get_active_promotion(c_id)
                if it_promo:
                    it_price = it_price * (1 - it_promo["discount_percent"] / 100)
                it_sub = it_price * qty
                subtotal_acc += it_sub

                c_row1, c_row2 = st.columns([3, 1])
                with c_row1:
                    st.markdown(f"<span style='font-size:0.85rem; font-weight:600; color:#1a1612;'>{html.escape(item_prod['name'])}</span><br><span style='font-size:0.75rem; color:#8a7a68;'>{qty}x {fmt_price(it_price)}</span>", unsafe_allow_html=True)
                with c_row2:
                    if st.button("✕", key=f"del_it_{c_id}"):
                        st.session_state.store.adjust_product_stock(c_id, qty)
                        del st.session_state.cart[c_id]
                        st.rerun()
                st.write("")

        st.markdown(f"""
        <div style="border-top: 1px solid #f0eae1; padding-top: 0.8rem; margin-top: 0.5rem;">
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:1.05rem; color:#1a1612;">
                <span>Total:</span>
                <span>{fmt_price(subtotal_acc)}</span>
            </div>
            <div style="font-size:0.76rem; color:#8a7a68; margin-top:0.2rem;">
                À vista no PIX (5% desc.): <strong>{fmt_price(subtotal_acc * 0.95)}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Concluir Pedido", use_container_width=True, type="primary"):
            st.session_state.cart = {}
            st.success("Pedido concluído! O estoque foi reservado na sessão.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Live Inventory Lab (Auditing & Testing) ---
    st.markdown("""
    <div class="cart-box" style="margin-top: 1.2rem;">
        <h4 class="cart-title">⚙️ Painel de Luthieria / Estoque</h4>
        <p style="font-size:0.78rem; color:#8a7a68; margin-bottom: 0.8rem;">
            Ajuste a quantidade em estoque para testar a reatividade imediata do Concierge de IA:
        </p>
    """, unsafe_allow_html=True)

    all_item_names = st.session_state.store.products["name"].tolist()
    sel_inst = st.selectbox("Selecione o instrumento:", all_item_names, key="sel_stock_inst", label_visibility="collapsed")
    p_matched = st.session_state.store.products[st.session_state.store.products["name"] == sel_inst].iloc[0]
    p_cur_stock = int(p_matched["stock_quantity"])

    st_col1, st_col2 = st.columns([1.2, 1])
    with st_col1:
        new_qty = st.number_input("Qtd:", min_value=0, max_value=999, value=p_cur_stock, key=f"q_{p_matched['product_id']}", label_visibility="collapsed")
    with st_col2:
        if st.button("Atualizar", key="btn_update_stock", use_container_width=True):
            st.session_state.store.update_product_stock(int(p_matched["product_id"]), int(new_qty))
            st.session_state.toast_msg = f"Estoque de '{sel_inst}' atualizado para {new_qty}!"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FLOATING CONCIERGE ATELIER POPUP (BOTÃO CIRCULAR DE LUXO)
# =========================================================
with st.popover("🎻", use_container_width=False):
    st.markdown("""
    <div style="border-bottom: 1px solid #eae5dc; padding-bottom: 0.8rem; margin-bottom: 0.8rem;">
        <div style="font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase; color: #9e7d56; font-weight: 600;">
            Atendimento Especializado
        </div>
        <h4 style="font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.5rem; margin: 0.2rem 0 0 0; color: #1a1612;">
            Consultor Empório da Música
        </h4>
        <div style="font-size: 0.78rem; color: #706254; margin-top: 0.2rem;">
            Consultoria de timbres, madeiras nobres, disponibilidade em tempo real e políticas.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chatbot_ready:
        st.error(f"Sistema de consultoria temporariamente indisponível: {st.session_state.get('chatbot_error', 'Verifique a chave de API.')}")
    else:
        # Quick prompts
        st.markdown("<div style='font-size:0.75rem; color:#8a7a68; margin-bottom:0.4rem;'>Sugestões de consulta:</div>", unsafe_allow_html=True)
        q_cols = st.columns(2)
        with q_cols[0]:
            if st.button("🎻 Violões até R$ 1.000", key="sug_violao", use_container_width=True):
                st.session_state.active_chat_prompt = "Quais opções de violões disponíveis vocês têm custando até R$ 1.000?"
                st.rerun()
        with q_cols[1]:
            if st.button("🏷️ Promoções ativas", key="sug_promos", use_container_width=True):
                st.session_state.active_chat_prompt = "Quais instrumentos estão com promoção ativa no momento?"
                st.rerun()

        # Chat Conversation Window
        chat_flow = st.container(height=360)

        with chat_flow:
            if not st.session_state.messages:
                welcome_editorial = (
                    "Olá! Seja muito bem-vindo(a) ao **Empório da Música**.\n\n"
                    "Sou o consultor virtual da loja. Posso auxiliá-lo(a) a encontrar o instrumento ideal para o seu perfil musical, "
                    "verificar especificações de madeiras e timbres, consultar nosso estoque em tempo real ou esclarecer dúvidas "
                    "sobre condições de pagamento e políticas de garantia.\n\n"
                    "Em que posso servi-lo(a) hoje?"
                )
                with st.chat_message("assistant", avatar="🎻"):
                    st.markdown(welcome_editorial)

            for m in st.session_state.messages:
                with st.chat_message(m["role"], avatar="🎻" if m["role"] == "assistant" else None):
                    st.markdown(m["content"])

        # Input Handling
        pre_input = None
        if "active_chat_prompt" in st.session_state and st.session_state.active_chat_prompt:
            pre_input = st.session_state.active_chat_prompt
            del st.session_state.active_chat_prompt

        typed_query = st.chat_input("Pergunte ao consultor de luthieria...", key="chat_concierge_input")

        action_query = typed_query or pre_input

        if action_query:
            st.session_state.messages.append({"role": "user", "content": action_query})

            with chat_flow:
                with st.chat_message("user"):
                    st.markdown(action_query)

                with st.chat_message("assistant", avatar="🎻"):
                    with st.spinner("Consultando acervo e luthieria..."):
                        try:
                            response_text = st.session_state.chatbot.send_message(action_query)
                            st.markdown(response_text)
                            st.session_state.messages.append({"role": "assistant", "content": response_text})
                        except Exception as ex:
                            err_txt = f"Desculpe, ocorreu uma instabilidade na consulta: {str(ex)}"
                            st.error(err_txt)
                            st.session_state.messages.append({"role": "assistant", "content": err_txt})
            st.rerun()
