import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Formulário de Participação", layout="centered")
st.title("📅 Formulário de Registro de Serventia")

# --- FORMULÁRIO DE ENTRADA ---
with st.form("formulario"):
    st.subheader("🔢 Dados da Serventia")

    nome_serventia = st.text_input("Nome da Serventia")
    uf = st.selectbox("Estado (UF)", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    carimbo_teora = st.text_input("Carimbo TEORA (hash/url)")
    email = st.text_input("E-mail Institucional")
    telefone = st.text_input("Telefone / WhatsApp")

    st.subheader("🔄 Informacões de Participação")

    participa_semana = st.selectbox("Participa da Semana?", ["Sim", "Não"])
    motivo = st.text_area("Motivo da Participação")
    classe = st.selectbox("Classe", ["Infraestrutura", "Engajamento", "Participação"])
    atributo = st.selectbox("Atributo", ["Digital", "Presencial", "Misto"])

    grau_pertinencia = st.slider("Grau de Pertinência (Fuzzy)", 0.0, 1.0, 0.8)
    grau_conexao = st.slider("Grau de Conexão", 0.0, 1.0, 0.7)

    justificativa = st.text_area("Justificativa / Observação")
    outros = st.text_input("Outros")

    enviado = st.form_submit_button("📥 Enviar Dados")

# --- PROCESSAMENTO DOS DADOS ---
if enviado:
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados = {
        "NOME_SERVENTIA": nome_serventia,
        "UF": uf,
        "CARIMBO_TEORA": carimbo_teora,
        "EMAIL_INSTITUCIONAL": email,
        "TELEFONE_WHATSAPP": telefone,
        "PARTICIPA_SEMANA": participa_semana,
        "MOTIVO_PARTICIPACAO": motivo,
        "CLASSE": classe,
        "ATRIBUTO": atributo,
        "GRAU_PERTENCIMENTO": grau_pertinencia,
        "GRAU_CONEXAO": grau_conexao,
        "JUSTIFICATIVA/OBSERVAÇÃO": justificativa,
        "OUTROS": outros,
        "DATA_HORA_REGISTRO": data_hora
    }

    df_novo = pd.DataFrame([dados])
    st.success("✅ Dados registrados com sucesso!")
    st.dataframe(df_novo)

    # [PRÓXIMO PASSO] Integrar com API Google Sheets usando gspread ou requests
