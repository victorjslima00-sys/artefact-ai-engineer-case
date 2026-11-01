"""
Streamlit UI for the Empório da Música chatbot.
"""

import streamlit as st
from src.agent import EmporioChatbot
from src.config import get_reference_date


# --- Page Configuration ---
st.set_page_config(
    page_title="Empório da Música — Atendimento",
    page_icon="🎸",
    layout="centered",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Header styling */
    .store-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .store-header h1 {
        color: #1a1a2e;
        font-size: 1.8rem;
        margin-bottom: 0.2rem;
    }
    .store-header p {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-open {
        background-color: #d4edda;
        color: #155724;
    }
    .status-closed {
        background-color: #f8d7da;
        color: #721c24;
    }

    /* Info bar */
    .info-bar {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-bottom: 1rem;
        font-size: 0.82rem;
        color: #555;
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    /* Chat message styling */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper: Check if store is open ---
def _is_store_open() -> bool:
    """Check if the store is currently open based on reference date."""
    from datetime import datetime
    ref = get_reference_date()
    now = datetime.now()
    weekday = ref.weekday()  # 0=Monday, 6=Sunday

    if weekday == 6:  # Sunday
        return False
    if weekday == 5:  # Saturday
        return 9 <= now.hour < 13
    return 9 <= now.hour < 18  # Mon-Fri


# --- Header ---
st.markdown("""
<div class="store-header">
    <h1>🎸 Empório da Música</h1>
    <p>Sua música começa aqui.</p>
</div>
""", unsafe_allow_html=True)

# --- Info Bar ---
ref_date = get_reference_date()
is_open = _is_store_open()
status_class = "status-open" if is_open else "status-closed"
status_text = "🟢 Aberto" if is_open else "🔴 Fechado"

col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📅 {ref_date.strftime('%d/%m/%Y')}")
with col2:
    st.caption(f"📍 Campo Grande/MS")
with col3:
    st.caption(f"{status_text}")

st.divider()

# --- Initialize Session State ---
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = EmporioChatbot()
        st.session_state.ready = True
    except Exception as e:
        st.session_state.ready = False
        st.session_state.error = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Check if ready ---
if not st.session_state.get("ready", False):
    st.error(f"⚠️ Erro ao inicializar o chatbot: {st.session_state.get('error', 'Verifique a API key.')}")
    st.info("Configure a variável `GEMINI_API_KEY` no arquivo `.env` e reinicie a aplicação.")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ℹ️ Sobre")
    st.markdown(
        "Assistente virtual da **Empório da Música**, "
        "loja de instrumentos musicais em Campo Grande/MS."
    )

    st.markdown("### 🕐 Horário")
    st.markdown(
        "- Seg–Sex: 09h–18h\n"
        "- Sáb: 09h–13h\n"
        "- Dom/Feriados: Fechado"
    )

    st.markdown("### 📞 Contato")
    st.markdown(
        "- Tel: (67) 3341-4444\n"
        "- WhatsApp: (67) 3321-4500\n"
        "- contato@emporiodamusica.com.br"
    )

    st.divider()

    if st.button("🔄 Nova conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chatbot.reset_history()
        st.rerun()

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🎸" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# --- Welcome Message ---
if not st.session_state.messages:
    welcome = (
        "Olá! 👋 Bem-vindo(a) à **Empório da Música**! Sou o assistente virtual da loja. "
        "Posso te ajudar com informações sobre nossos instrumentos, preços, promoções, "
        "status de pedidos e muito mais. Como posso te ajudar hoje? 🎵"
    )
    with st.chat_message("assistant", avatar="🎸"):
        st.markdown(welcome)
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# --- Chat Input ---
if prompt := st.chat_input("Digite sua mensagem..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get bot response
    with st.chat_message("assistant", avatar="🎸"):
        with st.spinner("Consultando..."):
            try:
                response = st.session_state.chatbot.send_message(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"Desculpe, ocorreu um erro: {str(e)}"
                st.error(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
