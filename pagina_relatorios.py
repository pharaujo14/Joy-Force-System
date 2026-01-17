import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

logo = Image.open("logo.png")


def pagina_relatorios(db):
    # =========================
    # Sessão
    # =========================
    user_role = st.session_state.get("role")
    user_nickname = st.session_state.get("nickname")
    is_admin = user_role == "admin"

    # =========================
    # Função utilitária
    # =========================
    def get_squad_power(squads, slot):
        if not isinstance(squads, list):
            return 0
        for s in squads:
            if s.get("slot") == slot:
                return s.get("power", 0) or 0
        return 0

    # =========================
    # Header
    # =========================
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.image(logo, width=120)
    with col2:
        st.markdown(
            "<h1 style='text-align:center;'>📊 Relatórios de Força</h1>",
            unsafe_allow_html=True
        )
    with col3:
        st.write("")

    # =========================
    # Dados
    # =========================
    data = list(db["data"].find())
    if not data:
        st.warning("Nenhum dado encontrado.")
        return

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    # Remove timezone do timestamp (MongoDB vem com UTC)
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)  

    df["power_total"] = pd.to_numeric(df["power_total"], errors="coerce")

    # =========================
    # User só vê o próprio
    # =========================
    if not is_admin:
        df = df[df["player_name"] == user_nickname]

    # ======================================================
    # ========================= ADMIN ======================
    # ======================================================
    if is_admin:
        # =========================
        # KPIs
        # =========================
        st.markdown("### 📌 Indicadores")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Jogadores", df["player_name"].nunique())
        c2.metric("Registros", len(df))
        c3.metric("Poder Médio", f"{df['power_total'].mean():.2f}")
        c4.metric("Poder Máximo", f"{df['power_total'].max():.2f}")

        st.markdown("---")

        # =========================
        # Último snapshot por jogador
        # =========================
        latest = (
            df.sort_values("timestamp")
            .groupby("player_name", as_index=False)
            .tail(1)
        )

        for i in range(1, 5):
            latest[f"squad_{i}"] = latest["squads"].apply(
                lambda x: get_squad_power(x, i)
            )

        latest["squad_total"] = sum(latest[f"squad_{i}"] for i in range(1, 5))

        # =========================
        # Ranking gráfico
        # =========================
        st.markdown("### 🏆 Ranking de Força – Última Atualização")

        metric = st.selectbox(
            "Métrica para ranking",
            [
                "Poder Total",
                "Drone",
                "Squads (Total)",
                "Squad 1",
                "Squad 2",
                "Squad 3",
                "Squad 4",
            ],
        )

        metric_map = {
            "Poder Total": "power_total",
            "Drone": "drone_level",
            "Squads (Total)": "squad_total",
            "Squad 1": "squad_1",
            "Squad 2": "squad_2",
            "Squad 3": "squad_3",
            "Squad 4": "squad_4",
        }

        metric_col = metric_map[metric]
        latest = latest.sort_values(metric_col, ascending=False)

        fig, ax = plt.subplots(figsize=(14, 6))
        players = latest["player_name"]

        if metric == "Squads (Total)":
            bottom = np.zeros(len(players))
            colors = ["#4285F4", "#EA4335", "#FBBC05", "#34A853"]

            for i, color in zip(range(1, 5), colors):
                values = latest[f"squad_{i}"].to_numpy()
                ax.bar(players, values, bottom=bottom, label=f"SQUAD {i}", color=color)
                bottom += values

            totals = latest["squad_total"].to_numpy()
            for i, total in enumerate(totals):
                ax.text(i, total + 0.8, f"{total:.2f}", ha="center", fontweight="bold")

            ax.legend(ncol=4)
        else:
            values = latest[metric_col].to_numpy()
            bars = ax.bar(players, values)
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val,
                    f"{val:.2f}" if metric != "Drone" else f"{int(val)}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

        ax.set_title(f"JOY BRASIL – Ranking por {metric}")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # =========================
        # ALERTA DE ATUALIZAÇÃO
        # =========================
        st.markdown("### ⏱️ Monitoramento de Atualizações")

        last_update_df = (
            df.groupby("player_name")["timestamp"]
            .max()
            .reset_index()
            .rename(columns={
                "player_name": "Jogador",
                "timestamp": "Última Atualização"
            })
        )

        hoje = pd.Timestamp.now().normalize()

        last_update_df["Dias sem atualizar"] = (
            hoje - last_update_df["Última Atualização"]
        ).dt.days

        atrasados = last_update_df[last_update_df["Dias sem atualizar"] >= 14]

        if len(atrasados) > 0:
            st.error(
                f"🚨 **{len(atrasados)} jogador(es)** estão há **14 dias ou mais sem atualizar**!"
            )
        else:
            st.success("✅ Todos os jogadores atualizaram nos últimos 14 dias.")

        order = st.selectbox(
            "Ordenar por",
            [
                "Mais tempo sem atualizar",
                "Atualizações mais recentes",
                "Ordem alfabética",
            ],
        )

        if order == "Mais tempo sem atualizar":
            last_update_df = last_update_df.sort_values("Dias sem atualizar", ascending=False)
        elif order == "Atualizações mais recentes":
            last_update_df = last_update_df.sort_values("Última Atualização", ascending=False)
        else:
            last_update_df = last_update_df.sort_values("Jogador")

        def highlight(val):
            if val >= 14:
                return "background-color: #f8d7da; font-weight: bold"
            elif val >= 7:
                return "background-color: #fff3cd"
            return ""

        st.dataframe(
            last_update_df.style.applymap(
                highlight, subset=["Dias sem atualizar"]
            ),
            use_container_width=True,
        )

        st.markdown("---")

    # ======================================================
    # ============ TODOS: EVOLUÇÃO INDIVIDUAL ==============
    # ======================================================
    st.markdown("### 📈 Evolução do Jogador ao Longo do Tempo")

    if is_admin:
        jogadores = sorted(df["player_name"].unique())
        selected_player = st.selectbox("Selecionar jogador", jogadores)
    else:
        selected_player = user_nickname
        st.info(f"Exibindo dados do jogador: **{selected_player}**")

    player_df = (
        df[df["player_name"] == selected_player]
        .sort_values("timestamp")
        .copy()
    )

    for i in range(1, 5):
        player_df[f"Squad {i}"] = player_df["squads"].apply(
            lambda x: get_squad_power(x, i)
        )

    player_df["Squads (Total)"] = sum(
        player_df[f"Squad {i}"] for i in range(1, 5)
    )

    metric = st.selectbox(
        "Métrica para visualização",
        [
            "Poder Total",
            "Drone",
            "Squads (Total)",
            "Squad 1",
            "Squad 2",
            "Squad 3",
            "Squad 4",
        ],
        key="player_metric",
    )

    metric_map = {
        "Poder Total": "power_total",
        "Drone": "drone_level",
        "Squads (Total)": "Squads (Total)",
        "Squad 1": "Squad 1",
        "Squad 2": "Squad 2",
        "Squad 3": "Squad 3",
        "Squad 4": "Squad 4",
    }

    metric_col = metric_map[metric]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        player_df["timestamp"].to_numpy(),
        player_df[metric_col].to_numpy(),
        marker="o",
        linewidth=2,
    )

    for x, y in zip(
        player_df["timestamp"].to_numpy(),
        player_df[metric_col].to_numpy(),
    ):
        ax.text(
            x,
            y,
            f"{y:.2f}" if metric != "Drone" else f"{int(y)}",
            ha="center",
            fontsize=9,
        )

    ax.set_title(f"Evolução de {metric} – {selected_player}")
    ax.set_xlabel("Data")
    ax.set_ylabel(metric)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
