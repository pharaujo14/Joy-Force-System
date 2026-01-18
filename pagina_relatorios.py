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

    def troop_rank(val):
        if isinstance(val, str) and val.upper().startswith("T"):
            try:
                return int(val.replace("T", ""))
            except:
                return 0
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

    # =========================
    # Dados
    # =========================
    data = list(db["data"].find())
    if not data:
        st.warning("Nenhum dado encontrado.")
        return

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df["power_total"] = pd.to_numeric(df["power_total"], errors="coerce")

    # User comum vê apenas seus dados
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

        metric_rank = st.selectbox(
            "Métrica do ranking",
            [
                "Poder Total",
                "Drone",
                "Squads (Total)",
                "Squad 1",
                "Squad 2",
                "Squad 3",
                "Squad 4",
            ],
            key="metric_rank"
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

        metric_col = metric_map[metric_rank]
        latest = latest.sort_values(metric_col, ascending=False)

        max_players = len(latest)
        qtde = (
            max_players if max_players <= 1
            else st.slider(
                "Quantidade de jogadores",
                min_value=1,
                max_value=max_players,
                value=min(10, max_players),
                step=1
            )
        )

        latest_plot = latest.head(qtde)

        fig, ax = plt.subplots(figsize=(14, 6))
        players = latest_plot["player_name"]

        if metric_rank == "Squads (Total)":
            bottom = np.zeros(len(players))
            colors = ["#4285F4", "#EA4335", "#FBBC05", "#34A853"]

            for i, color in zip(range(1, 5), colors):
                values = latest_plot[f"squad_{i}"].to_numpy()
                ax.bar(players, values, bottom=bottom, label=f"SQUAD {i}", color=color)
                bottom += values

            totals = latest_plot["squad_total"].to_numpy()
            for i, total in enumerate(totals):
                ax.text(i, total + 0.8, f"{total:.2f}", ha="center", fontweight="bold")

            ax.legend(ncol=4)
        else:
            values = latest_plot[metric_col].to_numpy()
            bars = ax.bar(players, values)
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val,
                    f"{val:.2f}" if metric_rank != "Drone" else f"{int(val)}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                )

        ax.set_title(f"JOY BRASIL – Ranking por {metric_rank}")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)

        # =========================
        # TABELA RANKING
        # =========================
        st.markdown("### 📋 Ranking Detalhado")

        ranking_df = latest[[
            "player_name",
            "power_total",
            "drone_level",
            "squad_1",
            "squad_2",
            "squad_3",
            "squad_4",
            "squad_total",
            "troop_level_max"
        ]].rename(columns={
            "player_name": "Jogador",
            "power_total": "Poder Total",
            "drone_level": "Drone",
            "squad_1": "Squad 1",
            "squad_2": "Squad 2",
            "squad_3": "Squad 3",
            "squad_4": "Squad 4",
            "squad_total": "Squads (Total)",
            "troop_level_max": "Tropa Máx"
        })

        order_table = st.selectbox(
            "Ordenar tabela por",
            [
                "Poder Total",
                "Drone",
                "Squads (Total)",
                "Squad 1",
                "Squad 2",
                "Squad 3",
                "Squad 4",
                "Tropa Máx",
                "Jogador",
            ],
            key="order_table"
        )

        ranking_df["_tropa_rank"] = ranking_df["Tropa Máx"].apply(troop_rank)

        if order_table == "Tropa Máx":
            ranking_df = ranking_df.sort_values("_tropa_rank", ascending=False)
        elif order_table == "Jogador":
            ranking_df = ranking_df.sort_values("Jogador")
        else:
            ranking_df = ranking_df.sort_values(order_table, ascending=False)

        ranking_df = ranking_df.drop(columns=["_tropa_rank"])

        st.dataframe(
            ranking_df.reset_index(drop=True),
            use_container_width=True
        )

        st.markdown("---")

        # =========================
        # MONITORAMENTO
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

        hoje = pd.Timestamp.now().tz_localize(None).normalize()
        last_update_df["Dias sem atualizar"] = (
            hoje - last_update_df["Última Atualização"]
        ).dt.days

        atrasados = last_update_df[last_update_df["Dias sem atualizar"] >= 14]

        if not atrasados.empty:
            st.error(
                f"🚨 {len(atrasados)} jogador(es) sem atualizar há 14 dias ou mais"
            )
        else:
            st.success("✅ Todos os jogadores estão atualizados")

        st.dataframe(
            last_update_df.sort_values("Dias sem atualizar", ascending=False),
            use_container_width=True
        )

    # ======================================================
    # ============ EVOLUÇÃO INDIVIDUAL =====================
    # ======================================================
    st.markdown("### 📈 Evolução do Jogador ao Longo do Tempo")

    if is_admin:
        jogadores = sorted(df["player_name"].unique())
        selected_player = st.selectbox("Selecionar jogador", jogadores, key="player_sel")
    else:
        selected_player = user_nickname
        st.info(f"Exibindo dados do jogador: **{selected_player}**")

    player_df = df[df["player_name"] == selected_player].sort_values("timestamp")

    for i in range(1, 5):
        player_df[f"Squad {i}"] = player_df["squads"].apply(
            lambda x: get_squad_power(x, i)
        )

    player_df["Squads (Total)"] = sum(
        player_df[f"Squad {i}"] for i in range(1, 5)
    )

    metric_player = st.selectbox(
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
        key="metric_player"
    )

    metric_map_player = {
        "Poder Total": "power_total",
        "Drone": "drone_level",
        "Squads (Total)": "Squads (Total)",
        "Squad 1": "Squad 1",
        "Squad 2": "Squad 2",
        "Squad 3": "Squad 3",
        "Squad 4": "Squad 4",
    }

    fig, ax = plt.subplots(figsize=(12, 5))

    x_vals = player_df["timestamp"].to_numpy()
    y_vals = player_df[metric_map_player[metric_player]].to_numpy()

    ax.plot(
        x_vals,
        y_vals,
        marker="o",
        linewidth=2
    )

    # === VALORES SOBRE OS PONTOS ===
    for x, y in zip(x_vals, y_vals):
        ax.text(
            x,
            y,
            f"{y:.2f}" if metric_player != "Drone" else f"{int(y)}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_title(f"Evolução de {metric_player} – {selected_player}")
    ax.set_xlabel("Data")
    ax.set_ylabel(metric_player)
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
