import streamlit as st
import bcrypt

from utils.auxiliar import validar_email, gerar_senha_automatica
from utils.email_utils import gerar_email_institucional, enviar_resultado


def badge(text, color):
    return f"<span style='background:{color}; color:white; padding:3px 8px; border-radius:8px; font-size:11px;'>{text}</span>"


def gerenciar_usuarios(db):
    users_collection = db["users"]

    criar_usuario(db)

    if "usuario_a_editar" not in st.session_state:
        st.session_state.usuario_a_editar = None

    st.markdown("<h2 style='text-align:center;'>👥 Gestão de Usuários</h2>", unsafe_allow_html=True)

    busca = st.text_input("🔎 Buscar usuário por nickname ou e-mail").strip().lower()

    usuarios = list(users_collection.find())

    if busca:
        usuarios = [
            u for u in usuarios
            if busca in u.get("nickname", "").lower()
            or busca in u.get("username", "").lower()
        ]

    st.markdown(f"**Total encontrados:** {len(usuarios)}")
    st.markdown("---")

    st.subheader("📑 Lista de Usuários")

    if usuarios:
        for usuario in usuarios:
            ativo = usuario.get("ativo", True)

            badge_status = badge("Ativo", "#28a745") if ativo else badge("Inativo", "#dc3545")
            badge_role = badge(usuario.get("role", "user").capitalize(), "#007bff")

            with st.container():
                st.markdown(
                    f"""
                    <div style='border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;'>
                        <b>Nickname:</b> {usuario.get('nickname', '')}<br>
                        <b>E-mail:</b> {usuario.get('username', '')}<br>
                        {badge_status} {badge_role}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("✏️ Editar", key=f"editar_{usuario['_id']}"):
                        st.session_state.usuario_a_editar = usuario

                with col2:
                    if st.button("🚩 Inativar" if ativo else "✅ Reativar", key=f"toggle_{usuario['_id']}"):
                        users_collection.update_one(
                            {"_id": usuario["_id"]},
                            {"$set": {"ativo": not ativo}}
                        )
                        st.experimental_rerun()

                with col3:
                    if st.button("🔑 Resetar Senha", key=f"reset_{usuario['_id']}"):
                        nova_senha = gerar_senha_automatica()
                        hashed_password = bcrypt.hashpw(
                            nova_senha.encode("utf-8"),
                            bcrypt.gensalt()
                        )

                        users_collection.update_one(
                            {"_id": usuario["_id"]},
                            {"$set": {"password": hashed_password}}
                        )

                        body = gerar_email_institucional(
                            "redefinir_senha",
                            {
                                "nickname": usuario.get("nickname", ""),
                                "senha": nova_senha,
                                "link_sistema": "https://joy-force-system.streamlit.app/"
                            }
                        )

                        enviar_resultado(
                            subject="🔑 Redefinição de senha - Joy Force",
                            body=body,
                            recipients=[usuario.get("username")],
                            html=True
                        )

                        st.success("Senha redefinida e enviada por e-mail.")
    else:
        st.info("Nenhum usuário encontrado.")

    # =========================
    # EDIÇÃO DE USUÁRIO
    # =========================
    if st.session_state.usuario_a_editar:
        usuario = st.session_state.usuario_a_editar

        with st.expander(f"✏️ Editar usuário: {usuario.get('username')}", expanded=True):
            novo_nickname = st.text_input("Nickname", value=usuario.get("nickname", ""))
            novo_email = st.text_input("E-mail", value=usuario.get("username", ""))
            nova_role = st.selectbox(
                "Função",
                ["user", "admin"],
                index=["user", "admin"].index(usuario.get("role", "user"))
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Salvar alterações"):
                    if not validar_email(novo_email):
                        st.warning("E-mail inválido.")
                    elif novo_email != usuario.get("username") and users_collection.find_one({"username": novo_email}):
                        st.warning("Este e-mail já está em uso.")
                    else:
                        users_collection.update_one(
                            {"_id": usuario["_id"]},
                            {"$set": {
                                "nickname": novo_nickname.strip(),
                                "username": novo_email.strip(),
                                "role": nova_role
                            }}
                        )
                        st.session_state.usuario_a_editar = None
                        st.experimental_rerun()

            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.usuario_a_editar = None

    st.markdown("---")


def criar_usuario(db):
    users_collection = db["users"]

    st.subheader("➕ Adicionar Novo Usuário")

    with st.form("form_novo_usuario"):
        username = st.text_input("E-mail do Usuário")
        nickname = st.text_input("Nickname")
        role = st.selectbox("Função", ["user", "admin"])
        adicionar = st.form_submit_button("Adicionar Usuário")

    if adicionar:
        if not validar_email(username):
            st.warning("E-mail inválido.")
        elif users_collection.find_one({"username": username}):
            st.warning("E-mail já está em uso.")
        else:
            senha_gerada = gerar_senha_automatica()
            hashed_password = bcrypt.hashpw(
                senha_gerada.encode("utf-8"),
                bcrypt.gensalt()
            )

            users_collection.insert_one({
                "username": username,
                "nickname": nickname.strip(),
                "password": hashed_password,
                "role": role,
                "ativo": True
            })

            body = gerar_email_institucional(
                "criar_usuario",
                {
                    "nickname": nickname,
                    "username": username,
                    "senha": senha_gerada,
                    "link_sistema": "https://joy-force-system.streamlit.app/"
                }
            )
            
            enviar_resultado(
                subject="🎮 Acesso ao Joy Force",
                body=body,
                recipients=[username],
                html=True
            )

            st.success(f"Usuário {username} criado e senha enviada por e-mail.")
