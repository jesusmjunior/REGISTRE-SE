import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json

st.set_page_config(page_title="Formulário de Participação", layout="centered")
st.title("📅 Formulário de Registro de Serventia")

# --- DADOS DA SERVENTIA EM SELECTBOX ---
serventias = [
    "Cartório da 1ª Zona de Registro de Imóveis de São Luis",
    "Cartório do ofício Único de Poção de Pedras",
    "Cartório da 2ª Zona de Registro de Imóveis de São Luis",
    "Cartório do 7º Ofício de Imperatriz",
    "Cartório do 6º Ofício de Imperatriz",
    "Cartório do 1º Ofício de Caxias",
    "Cartório do 1º Ofício de São José de Ribamar",
    "Cartório do 2º Ofício de Açailândia",
    "Cartório do 1º Ofício de Açailândia",
    "Cartório do 1º Ofício de Timon"
]

# --- FORMULÁRIO DE ENTRADA ---
with st.form("formulario"):
    st.subheader("🔢 Dados da Serventia")

    nome_serventia = st.selectbox("Selecione a Serventia", options=serventias)
    email = st.text_input("Endereço de e-mail da serventia")
    telefone = st.text_input("Whatsapp de contato")

    st.subheader("📊 Informações da Semana Registre-se")

    participa_semana = st.selectbox("Foram realizadas ações na Semana 'Registre-se' em maio de 2024?", ["Sim", "Não"])
    motivo_nao_part = st.text_area("Em caso de resposta NÃO ao quesito anterior, qual o motivo da não participação na Semana Registre-se?")
    acoes_realizadas = st.text_area("Quais as ações realizadas na Semana Registre-se? Identifique-as por dia, se possível.")
    publicos_atendidos = st.text_input("Marque as opções dos públicos atendidos:")

    vias_emitidas = st.number_input("Quantas 2ª vias foram emitidas?", min_value=0)
    registros_nasc = st.number_input("Quantos registros de nascimento foram feitos?", min_value=0)
    averbacoes_pat = st.number_input("Quantas averbações de paternidade foram feitas?", min_value=0)
    retificacoes = st.number_input("Quantas retificações de registro de nascimento foram iniciadas ou processadas?", min_value=0)
    registros_tardios = st.number_input("Quantos registros tardios de nascimento foram iniciados ou processados?", min_value=0)
    restauracoes = st.number_input("Quantas restaurações de registro de nascimento foram iniciadas ou processadas?", min_value=0)

    classificacao = st.selectbox("Classificação", ["Infraestrutura", "Engajamento", "Participação"])
    tags = st.text_input("Tags (separadas por vírgula)")

    enviado = st.form_submit_button("📥 Enviar Dados")

# --- PROCESSAMENTO DOS DADOS ---
if enviado:
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados = {
        "Carimbo de data/hora": data_hora,
        "Identificação da Serventia Extrajudicial": nome_serventia,
        "Endereço de e-mail": email,
        "Whatsapp": telefone,
        "Foram realizadas ações na Semana 'Registre-se'?": participa_semana,
        "Motivo da não participação": motivo_nao_part,
        "Ações realizadas": acoes_realizadas,
        "Públicos atendidos": publicos_atendidos,
        "2as vias emitidas": vias_emitidas,
        "Registros de nascimento": registros_nasc,
        "Averbações de paternidade": averbacoes_pat,
        "Retificações de registro": retificacoes,
        "Registros tardios": registros_tardios,
        "Restaurações de registro": restauracoes,
        "Classificação": classificacao,
        "Tags": tags
    }

    df_novo = pd.DataFrame([dados])
    st.success("✅ Dados registrados com sucesso!")
    st.dataframe(df_novo)

    st.warning("⚠️ Para salvar na planilha pública, o sistema precisa de uma API intermediária com autenticação via chave JSON.")

    # Placeholder para integração com gspread + OAuth2
    # API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"
    # CSV de leitura: https://docs.google.com/spreadsheets/d/e/2PACX-1vQ8DMerTOl7-0wF6sH9_Hiz7T0gUwZYhPUuDejn4k--U_Q9SuAQ2haIMcs05_LFAQ8CcN7hLAZ_ojiy/pub?output=csv
