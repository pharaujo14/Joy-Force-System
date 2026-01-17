# ⚔️ Joy Force System

Sistema web para **gestão, visualização e análise da força dos jogadores**, com foco em:
- Rankings
- Evolução histórica
- Monitoramento de atualizações
- Autonomia do jogador
- Controle administrativo

Desenvolvido com **Streamlit + MongoDB**, com autenticação por usuário e níveis de acesso.

---

## 🚀 Funcionalidades

### 👤 Usuário (Player)
- Login com autenticação segura
- Visualização **exclusiva** da própria evolução
- Gráfico de evolução por métricas:
  - Poder Total
  - Drone
  - Squads (Total)
  - Squad 1 a 4
- Atualização manual das próprias informações de força

---

### 🛡️ Administrador (Admin)
- Visualização global de todos os jogadores
- KPIs gerais do sistema
- Ranking por múltiplas métricas
- Ranking por squads (empilhado)
- Tabela de ranking com ordenação dinâmica
- Monitoramento de atualizações:
  - Última data de atualização por jogador
  - Quantidade de dias sem atualizar
  - 🚨 Alerta visual para jogadores sem atualizar há 14+ dias
- Gráfico de evolução individual (qualquer jogador)

---

## 📊 Métricas Disponíveis

- Poder Total
- Drone
- Squads:
  - Squad 1
  - Squad 2
  - Squad 3
  - Squad 4
  - Squads (Total)
- Level do jogador
- Tropa máxima (ordenada corretamente: T10 > T9 > T8...)

---

## 🧱 Stack Tecnológica

- **Frontend / App:** Streamlit
- **Backend / Dados:** MongoDB Atlas
- **Gráficos:** Matplotlib
- **Autenticação:** bcrypt
- **Processamento de dados:** Pandas + NumPy

---

## 📦 Dependências

```txt
streamlit==1.29.0
pandas==2.0.3
numpy
matplotlib
Pillow
requests
pytz

bcrypt
pymongo

streamlit-option-menu==0.3.6
streamlit-lottie==0.0.5
```

---

## 🔐 Autenticação e Sessão

- Login por e-mail e senha
- Senhas criptografadas com `bcrypt`
- Controle de acesso por `role`:
  - `admin`
  - `user`
- Sessão gerenciada via `st.session_state`

---

## 🗂️ Estrutura do Projeto

```text
Joy-Force-System/
│
├── app.py
├── requirements.txt
├── README.md
│
├── utils/
│   ├── conectaBanco.py
│   ├── auxiliar.py
│   ├── email_utils.py
│
├── paginas/
│   ├── pagina_login.py
│   ├── pagina_relatorios.py
│   ├── pagina_usuarios.py
│   ├── pagina_atualizar_forca.py
│
├── assets/
│   └── logo.png
```

---

## 🧠 Modelagem de Dados (MongoDB)

### Collection: `data`

```json
{
  "_id": "ObjectId",
  "player_name": "Dantes07",
  "timestamp": "2026-01-15T00:00:00Z",
  "power_total": 100.0,
  "level": 30,
  "squads": [
    { "slot": 1, "type": "TANQUE", "power": 26.3 },
    { "slot": 2, "type": "AÉREO", "power": 20.1 }
  ],
  "troop_level_max": "T10",
  "drone_level": 125,
  "source": "manual"
}
```

---

## ▶️ Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧭 Próximas Evoluções (Roadmap)

- 🔔 Lembrete automático para jogadores inativos
- 📈 Score de engajamento por jogador
- 🧠 Tendência de crescimento por player
- 📩 Notificações por e-mail / sistema
- 📱 Layout mobile-first

---

## 👨‍💻 Autor

Projeto desenvolvido para **gestão estratégica da aliança Joy Brasil**, com foco em dados, performance e organização.

---

⚔️ **Joy Force System**
*Dados claros. Decisão rápida. Força organizada.*
