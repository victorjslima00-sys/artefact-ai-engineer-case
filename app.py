"""
Empório da Música — Interface de Chat
Chatbot de atendimento virtual com IA (Gemini + function calling).
"""

import streamlit as st
from src.agent import EmporioChatbot
from src.data_loader import DataStore

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Empório da Música — Atendimento Virtual",
    page_icon="🎸",
    layout="centered",
)

# ── CSS mínimo ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Remove margem excessiva do topo */
    .block-container { padding-top: 2rem; }
    /* Destaca o nome da loja no cabeçalho */
    .store-header { text-align: center; margin-bottom: 0.25rem; }
    .store-tagline { text-align: center; color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown('<h2 class="store-header">🎸 Empório da Música</h2>', unsafe_allow_html=True)
st.markdown(
    '<p class="store-tagline">Instrumentos musicais autênticos • Campo Grande/MS</p>',
    unsafe_allow_html=True,
)
st.divider()

# ── Inicialização do agente (uma vez por sessão) ───────────────────────────────
if "agent" not in st.session_state:
    try:
        store = DataStore()
        st.session_state.agent = EmporioChatbot(store=store)
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Erro ao inicializar o assistente: {e}")
        st.stop()

# ── Renderiza o histórico de mensagens ────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Saudação inicial (apenas na primeira abertura) ────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        greeting = (
            "Olá! 👋 Bem-vindo ao **Empório da Música**!\n\n"
            "Sou o assistente virtual da loja. Posso te ajudar com:\n"
            "- 🎸 Busca de instrumentos e verificação de estoque\n"
            "- 💰 Preços, promoções e condições de pagamento\n"
            "- 📦 Status de pedidos e política de trocas\n\n"
            "Como posso te ajudar hoje?"
        )
        st.markdown(greeting)
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# ── Campo de entrada ──────────────────────────────────────────────────────────
user_input = st.chat_input("Digite sua mensagem…")

if user_input:
    # Exibe mensagem do usuário
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Obtém resposta do agente
    with st.chat_message("assistant"):
        with st.spinner("Consultando o sistema…"):
            try:
                response = st.session_state.agent.send_message(user_input)
            except Exception as e:
                response = f"Desculpe, ocorreu um erro ao processar sua mensagem: {e}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
