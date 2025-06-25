import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
import hashlib

# ==== CONFIGURAÇÕES ==== 
st.set_page_config(page_title="EducaBot", page_icon="🤖", layout="centered")

# ==== CSS CUSTOMIZADO - ESTILO CHATGPT ====
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            background-color: #202123;
            border-bottom: 1px solid #444;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        .header-title {
            font-size: 1.6rem;
            font-weight: bold;
            color: #10a37f;
        }
        .avatar {
            background-color: #10a37f;
            color: white;
            font-weight: bold;
            padding: 0.5rem 0.75rem;
            border-radius: 50%;
            cursor: pointer;
        }
        .main-content {
            margin-top: 90px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
        .chat-message {
            font-size: 1rem;
            margin: 0.5em 0;
        }
        .user-message {
            background-color: #343541;
            color: #fff;
            padding: 14px 18px;
            border-radius: 12px;
            max-width: 80%;
            margin: 10px 0;
            align-self: flex-end;
            margin-left: auto;
        }
        .bot-message {
            background-color: #444654;
            color: #fff;
            padding: 14px 18px;
            border-radius: 12px;
            max-width: 80%;
            margin: 10px 0;
            align-self: flex-start;
            margin-right: auto;
        }
        input, textarea {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        .stButton > button {
            background-color: #10a37f !important;
            color: white !important;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ==== API Key do Gemini ==== 
genai.configure(api_key=st.secrets["api_key"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ==== USUÁRIOS VÁLIDOS ==== 
usuarios_validos = {
    "joao": hashlib.sha256("senha123".encode()).hexdigest(),
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ==== LOGIN ==== 
def exibir_login():
    with st.expander("🔐 Fazer login", expanded=True):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            senha_hash = hashlib.sha256(senha_input.encode()).hexdigest()
            if usuario_input in usuarios_validos and usuarios_validos[usuario_input] == senha_hash:
                st.success("Login bem-sucedido! ✅")
                st.session_state.logado = True
                st.session_state.usuario = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

if not st.session_state.logado:
    st.markdown("""
        <div class="header-container">
            <div class="header-title">EducaBot</div>
            <div class="avatar">🔐</div>
        </div>
    """, unsafe_allow_html=True)
    exibir_login()
    st.stop()

# ==== HEADER COM AVATAR ==== 
st.markdown(f"""
    <div class='header-container'>
        <div class='header-title'>EducaBot</div>
        <div class='avatar' title='Usuário logado: {st.session_state.usuario}'>👤</div>
    </div>
""", unsafe_allow_html=True)

# ==== CONTEÚDO PRINCIPAL ==== 
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# ==== GERENCIAMENTO DE CONVERSAS ==== 
if "conversas_salvas" not in st.session_state:
    st.session_state.conversas_salvas = {"Conversa atual": []}

if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = "Conversa atual"

# ==== SIDEBAR ==== 
with st.sidebar:
    st.title("📜 Histórico")
    st.markdown("**Conversas anteriores** (não salva ainda)")
    st.markdown("---")

    for nome in st.session_state.conversas_salvas:
        if st.button(nome):
            st.session_state.selected_conversation = nome
            st.rerun()

    idioma = st.selectbox("🌐 Idioma da resposta", ["Português", "Inglês", "Espanhol"])

    if st.button("🆕 Nova conversa"):
        novo_nome = f"Conversa {len(st.session_state.conversas_salvas)}"
        st.session_state.conversas_salvas[novo_nome] = []
        st.session_state.selected_conversation = novo_nome
        st.rerun()

# ==== EXIBIÇÃO DAS MENSAGENS ==== 
st.markdown("## 💬 Conversa")
conversa_atual = st.session_state.conversas_salvas[st.session_state.selected_conversation]
chat_container = st.container()

for troca in conversa_atual:
    with chat_container:
        st.markdown(f'<div class="user-message chat-message"><strong>Você:</strong> {troca["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-message chat-message"><strong>EducaBot:</strong> {troca["bot"]}</div>', unsafe_allow_html=True)

# ==== PERGUNTA ==== 
fuso = pytz.timezone('America/Sao_Paulo')
data_atual = datetime.now(fuso).strftime('%d/%m/%Y')

with st.form("form_pergunta", clear_on_submit=True):
    pergunta = st.text_input("Digite sua pergunta:", label_visibility="collapsed")
    enviar = st.form_submit_button("Enviar")

    if enviar and pergunta:
        prompt = f"Estamos no dia {data_atual}. Responda em {idioma} a seguinte pergunta:\n{pergunta}"
        with st.spinner("Pensando... 🤔"):
            resposta = model.generate_content(prompt)
            conversa_atual.append({"user": pergunta, "bot": resposta.text})
        st.rerun()

# ==== RODAPÉ ==== 
data_hora_atual = datetime.now(fuso).strftime('%d/%m/%Y %H:%M')
st.markdown(f"<p style='text-align:center; color:gray;'>🗓 {data_hora_atual}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
