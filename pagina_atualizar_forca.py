import streamlit as st
from datetime import datetime


def pagina_atualizar_forca(db):
    user_nickname = st.session_state.get("nickname")

    st.markdown("## 📝 Atualizar Força do Jogador")
    st.info(f"Jogador logado: **{user_nickname}**")

    collection = db["data"]

    # =========================
    # Último registro (snapshot)
    # =========================
    ultimo = (
        collection.find({"player_name": user_nickname})
        .sort("timestamp", -1)
        .limit(1)
    )

    ultimo = list(ultimo)
    ultimo = ultimo[0] if ultimo else {}

    # =========================
    # FORMULÁRIO
    # =========================
    with st.form("form_atualizar_forca"):

        power_total = st.number_input(
            "Poder Total",
            min_value=0.0,
            value=float(ultimo.get("power_total") or 0),
            step=1.0
        )

        level = st.number_input(
            "Level do Jogador",
            min_value=1,
            max_value=30,
            value=int(ultimo.get("level") or 1)
        )

        drone_level = st.number_input(
            "Level do Drone",
            min_value=0,
            value=int(ultimo.get("drone_level") or 0)
        )

        troop_level_max = st.selectbox(
            "Nível máximo de tropa",
            ["T7", "T8", "T9", "T10"],
            index=["T7", "T8", "T9", "T10"].index(
                ultimo.get("troop_level_max", "T7")
            )
        )

        st.markdown("### ⚔️ Squads")

        squads = []

        for i in range(1, 5):
            default_power = 0

            for s in ultimo.get("squads", []):
                if s.get("slot") == i:
                    default_power = s.get("power") or 0

            squad_power = st.number_input(
                f"Squad {i} – Poder",
                min_value=0.0,
                value=float(default_power),
                step=0.1,
                key=f"squad_{i}"
            )

            squads.append({
                "slot": i,
                "power": squad_power
            })

        submit = st.form_submit_button("💾 Salvar Atualização")

    # =========================
    # SALVAR NO BANCO
    # =========================
    if submit:
        doc = {
            "player_name": user_nickname,
            "timestamp": datetime.utcnow(),
            "power_total": power_total,
            "level": level,
            "drone_level": drone_level,
            "troop_level_max": troop_level_max,
            "squads": squads,
            "source": "form_usuario"
        }

        collection.insert_one(doc)
        st.success("Atualização registrada com sucesso! ✅")
