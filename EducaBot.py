import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
import hashlib

# ========== CONFIGURAÇÕES ==========
st.set_page_config(page_title="EducaBot", page_icon="🤖", layout="wide")

# ========== CSS PERSONALIZADO ==========
st.markdown("""
    <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 30px;
            background-color: #0e1117;
            border-bottom: 1px solid #333;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        .header-title {
            font-size: 1.8em;
            font-weight: bold;
            color: #4CAF50;
        }
        .avatar {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
        }
        .main-content {
            margin-top: 80px;
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

# ========== API Key ==========
genai.configure(api_key=st.secrets["api_key"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ========== USUÁRIOS AUTORIZADOS ==========
usuarios_validos = {
    "joao": hashlib.sha256("senha123".encode()).hexdigest(),
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

# ========== ESTADO INICIAL ==========
st.session_state.setdefault("logado", False)
st.session_state.setdefault("usuario", "")
st.session_state.setdefault("conversas_salvas", {"Conversa atual": []})
st.session_state.setdefault("selected_conversation", "Conversa atual")

# ========== LOGIN ==========
def exibir_login():
    with st.expander("🔐 Fazer login", expanded=True):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if usuario in usuarios_validos and usuarios_validos[usuario] == senha_hash:
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.success("Login bem-sucedido! ✅")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

# ========== SE NÃO ESTIVER LOGADO ==========
if not st.session_state.logado:
    st.markdown("""
        <div class="header-container">
            <div class="header-title">EducaBot</div>
            <div class="avatar">🔐</div>
        </div>
    """, unsafe_allow_html=True)
    exibir_login()
    st.stop()

# ========== HEADER LOGADO ==========
st.markdown(f"""
    <div class="header-container">
        <div class="header-title">EducaBot</div>
        <div class="avatar" title="Usuário logado: {st.session_state.usuario}">👤</div>
    </div>
""", unsafe_allow_html=True)

# ========== CONTEÚDO PRINCIPAL ==========
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📜 Histórico")
    st.markdown("**Conversas anteriores**")
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

# ========== MENSAGENS ==========
st.markdown("## 💬 Conversa")
conversa_atual = st.session_state.conversas_salvas[st.session_state.selected_conversation]
chat_container = st.container()

for troca in conversa_atual:
    with chat_container:
        st.markdown(f'<div class="user-message chat-message"><strong>Você:</strong> {troca["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-message chat-message"><strong>EducaBot:</strong> {troca["bot"]}</div>', unsafe_allow_html=True)

# ========== PERGUNTA ==========
fuso = pytz.timezone("America/Sao_Paulo")
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

# ========== RODAPÉ ==========
data_hora = datetime.now(fuso).strftime('%d/%m/%Y %H:%M')
st.markdown(f"<p style='text-align:center; color:gray;'>🗓 {data_hora}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
