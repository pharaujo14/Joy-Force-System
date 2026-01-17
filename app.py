import streamlit as st
import pytz
from PIL import Image
from streamlit_option_menu import option_menu

from utils.conectaBanco import conectaBanco
from pagina_login import login, is_authenticated
from pagina_usuarios import gerenciar_usuarios

from pagina_trocarSenha import trocar_senha
from pagina_atualizar_forca import pagina_atualizar_forca
from pagina_relatorios import pagina_relatorios

# =========================
# Configuração inicial
# =========================
st.set_page_config(
    page_title="Joy Brasil",
    page_icon="⚔️",
    layout="wide"
)

timezone_brasil = pytz.timezone("America/Sao_Paulo")

# =========================
# Sessão do usuário
# =========================
user_role = st.session_state.get("role", "")
user_nickname = st.session_state.get("nickname", "")

# =========================
# Banco de dados
# =========================
db_password = st.secrets["database"]["password"]
db = conectaBanco(db_password)

# =========================
# Autenticação
# =========================
if not is_authenticated():
    login(db)
    st.stop()

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.image("logo.png", width=160)
    st.markdown(f"**👤 {user_nickname}**")

    menu_options = [
        "Upload de Informações",
        "Relatórios",
        "Trocar Senha"
    ]

    menu_icons = [
        "upload",
        "bar-chart",
        "key"
    ]

    if user_role == "admin":
        menu_options.extend([
            "Gestão de Usuários",
            "Controle de Ferramentas"
        ])
        menu_icons.extend([
            "people",
            "tools"
        ])

    selected_tab = option_menu(
        menu_title="Menu Principal",
        options=menu_options,
        icons=menu_icons,
        menu_icon="list",
        default_index=0
    )

# =========================
# Páginas
# =========================
if selected_tab == "Upload de Informações":
    pagina_atualizar_forca(db)

elif selected_tab == "Relatórios":
    pagina_relatorios(db)

elif selected_tab == "Trocar Senha":
    trocar_senha(db)

elif selected_tab == "Gestão de Usuários":
    if user_role == "admin":
        gerenciar_usuarios(db)
    else:
        st.warning("Você não tem permissão para acessar esta página.")