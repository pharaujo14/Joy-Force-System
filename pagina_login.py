import streamlit as st
import bcrypt

def login(db):
    # CSS que você já validou
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 0.5rem !important;
            }

            div[data-testid="stImage"] {
                margin-top: -40px !important;
                margin-bottom: -120px !important;
            }

            h1 {
                margin-top: 0 !important;
                margin-bottom: 1rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 🔹 SOMENTE o logo centralizado
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=400)

    # Todo o resto permanece igual
    st.title("Login")

    with st.form(key="login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        login_button = st.form_submit_button("Entrar")

    if login_button:
        users_collection = db["users"]
        user_data = users_collection.find_one({"username": username})

        if not user_data:
            st.error("Usuário ou senha incorretos.")
            return

        if not user_data.get("ativo", True):
            st.error("Usuário inativado. Contate o administrador.")
            return

        if bcrypt.checkpw(
            password.encode("utf-8"),
            user_data["password"]
        ):
            st.session_state["logged_in"] = True
            st.session_state["username"] = user_data["username"]
            st.session_state["role"] = user_data.get("role")
            st.session_state["nickname"] = user_data.get("nickname")

            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")


def is_authenticated():
    return st.session_state.get("logged_in", False)
