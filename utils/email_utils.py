import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def gerar_email_institucional(tipo, dados):
    link_sistema = dados.get("link_sistema", "https://joy-force-system.streamlit.app/")

    header = f"""
    <div style='background-color:#004080; padding:20px; text-align:center;'>
    </div>
    """

    footer = """
    <div style='background:#f0f0f0; padding:10px; text-align:center; font-size:11px; color:#777;'>
        Este e-mail foi enviado automaticamente pelo sistema Joy Force System.
    </div>
    """

    if tipo == "criar_usuario":
        body = f"""
        <h2 style='color:#004080;'>🚀 Sua conta foi criada</h2>
        <p>Olá <strong>{dados.get('nickname') or dados.get('nome') or dados.get('username')}</strong>,</p>
        <p>Seu acesso ao sistema Joy foi criado com sucesso!</p>
        <p><b>Usuário:</b> {dados['username']}<br>
        <b>Senha Provisória:</b> {dados['senha']}</p>
        <p style='font-size:13px; color:#666;'>Recomendamos trocar sua senha após o primeiro login.</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    elif tipo == "upload_certificado":
        body = f"""
        <h2 style='color:#004080;'>📄 Novo Certificado Enviado</h2>
        <p>O usuário <strong>{dados['nome']}</strong> realizou o upload de um novo certificado.</p>
        <p><b>Arquivo:</b> {dados['arquivo']}</p>
        """

    elif tipo == "redefinir_senha":
        body = f"""
        <h2 style='color:#004080;'>🔑 Redefinição de Senha</h2>
        <p>Olá <strong>{dados.get('nickname') or dados.get('nome') or dados.get('username')}</strong>,</p>
        <p>Conforme solicitado, sua senha foi redefinida.</p>
        <p><b>Nova Senha:</b> {dados['senha']}</p>
        <p>Por segurança, altere sua senha assim que possível.</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    elif tipo == "notificacao":
        body = f"""
        <h2 style='color:#004080;'>🔔 Notificação</h2>
        <p>{dados['mensagem']}</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    else:
        body = "<p>Tipo de e-mail inválido.</p>"

    return f"""
    <div style='font-family: Arial, sans-serif; max-width:600px; margin:auto; border:1px solid #e0e0e0; border-radius:8px; overflow:hidden; background:#ffffff;'>
        {header}
        <div style='padding:20px;'>{body}</div>
        {footer}
    </div>
    """
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def enviar_resultado(subject, body, recipients, html=False):
    smtp_cfg = st.secrets["smtp"]

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_cfg["sender"]
    msg["To"] = ", ".join(recipients)

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_cfg["server"], smtp_cfg["port"]) as server:
            server.starttls()
            server.login(smtp_cfg["user"], smtp_cfg["password"])
            server.sendmail(
                smtp_cfg["sender"],
                recipients,
                msg.as_string()
            )
    except Exception as e:
        # Não quebra o app
        print(f"Erro ao enviar e-mail: {e}")
