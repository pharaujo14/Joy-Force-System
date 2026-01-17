import streamlit as st
import re
import random
import string

def validar_senha(senha):
    return (
        len(senha) >= 8 and
        any(c.isupper() for c in senha) and
        any(c.islower() for c in senha) and
        any(c.isdigit() for c in senha) and
        any(not c.isalnum() for c in senha)
    )

def gerar_senha_automatica():
    """
    Gera uma senha forte que inclui:
    - Pelo menos uma letra maiúscula
    - Pelo menos uma letra minúscula
    - Pelo menos um número
    - Pelo menos um caractere especial
    - Comprimento mínimo de 8 caracteres
    """
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    senha = [
        random.choice(string.ascii_uppercase),  # Garantir uma maiúscula
        random.choice(string.ascii_lowercase),  # Garantir uma minúscula
        random.choice(string.digits),           # Garantir um número
        random.choice("!@#$%^&*()-_=+"),        # Garantir um caractere especial
    ]
    senha += random.choices(caracteres, k=8 - len(senha))  # Restante aleatório
    random.shuffle(senha)  # Misturar os caracteres
    return ''.join(senha)

def validar_email(email):
    """
    Verifica se o e-mail é válido.
    """
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def formatar_nome(email):
    """
    Formata o nome a partir de um e-mail no formato 'nome.sobrenome@dominio.com'.
    """
    nome_sobrenome = email.split('@')[0]  # Pega a parte antes do @
    partes = nome_sobrenome.split('.')    # Divide em partes pelo '.'
    if len(partes) >= 2:
        nome = partes[0].capitalize()    # Capitaliza o primeiro nome
        sobrenome = partes[1].capitalize()  # Capitaliza o sobrenome
        return f"{nome} {sobrenome}"
    return nome_sobrenome.capitalize()  # Caso não tenha sobrenome, usa apenas o nome
