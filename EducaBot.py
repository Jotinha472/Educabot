# EducaBot - Versão estilo ChatGPT com visual aprimorado
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz

# ==== CONFIGURAÇÕES ====
st.set_page_config(page_title="EducaBot", page_icon="🤖", layout="wide")

# ==== CSS GLOBAL E ESTILO DAS MENSAGENS ====
st.markdown("""
    <style>
        button[kind="secondary"] {
            background-color: #00c6ff !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 0.5em 1.2em;
        }
        button[kind="secondary"]:hover {
            background-color: #009ec3 !important;
        }

        .chat-message {
            font-size: 1.05em;
            margin: 0.5em 0;
        }

        .user-message {
            background-color: #A9A9A9;
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 70%;
            margin: 10px 0;
            align-self: flex-end;
            margin-left: auto;
        }

        .bot-message {
            background-color: #708090;
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 70%;
            margin: 10px 0;
            align-self: flex-start;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)

# ==== CONFIGURAÇÃO DO MODELO ====
genai.configure(api_key=st.secrets["api_key"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ==== HISTÓRICO DE CONVERSA ====
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = "Conversa atual"

# ==== SIDEBAR ====
with st.sidebar:
    st.title("📜 Histórico")
    st.markdown("**Conversas anteriores** (não salva ainda)")
    st.markdown("---")
    for i, chat in enumerate(st.session_state.chat_history):
        st.button(f"Conversa {i+1}", key=f"chat_{i}")

    idioma = st.selectbox("🌐 Idioma da resposta", ["Português", "Inglês", "Espanhol"])

    st.markdown("---")
    if st.button("🆕 Nova conversa"):
        st.session_state.chat_history = []
        st.experimental_rerun()

# ==== TÍTULO E SUBTÍTULO ====
st.markdown("""
    <h2 style='text-align: center;'>🤖 <span style='color: #4CAF50;'>EducaBot</span></h2>
    <p style='text-align: center; font-size: 18px; color: gray;'>Seu assistente virtual de estudos com inteligência artificial!</p>
""", unsafe_allow_html=True)

# ==== ENTRADA DO USUÁRIO ====
pergunta = st.text_input("Digite sua pergunta para o EducaBot:")

# ==== DATA ATUAL ====
fuso = pytz.timezone('America/Sao_Paulo')
data_atual = datetime.now(fuso).strftime('%d/%m/%Y')

# ==== MONTAGEM DO PROMPT ====
prompt = f"Estamos no dia {data_atual}. Responda em {idioma} a seguinte pergunta:\n{pergunta}"

# ==== RESPOSTA DO BOT ====
if st.button("Enviar") and pergunta:
    with st.spinner("Pensando... 🤔"):
        resposta = model.generate_content(prompt)
        resposta_texto = resposta.text

        # Salva no histórico
        st.session_state.chat_history.append({
            "user": pergunta,
            "bot": resposta_texto
        })

# ==== EXIBIÇÃO DAS MENSAGENS ====
st.markdown("## 💬 Conversa")
chat_container = st.container()

for troca in reversed (st.session_state.chat_history):
    with chat_container:
        st.markdown(f'<div class="bot-message chat-message"><strong>EducaBot:</strong> {troca["bot"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-message chat-message"><strong>Você:</strong> {troca["user"]}</div>', unsafe_allow_html=True)


# ==== RODAPÉ COM DATA ====
data_hora_atual = datetime.now(fuso).strftime('%d/%m/%Y %H:%M')
st.markdown(f"<p style='text-align:center; color:gray;'>🗓 {data_hora_atual}</p>", unsafe_allow_html=True)
