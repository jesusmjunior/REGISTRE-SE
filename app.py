import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import uuid

st.set_page_config(page_title="Formulário de Participação", layout="centered")
st.title("📅 Formulário de Registro de Serventia")

# --- CARREGAR SERVENTIAS DO JSON EXTERNO ---
try:
    with open("serventias_registre_se.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        serventias = [s["nome"] for s in data["serventias"]]
except Exception as e:
    st.error(f"Erro ao carregar JSON de serventias: {e}")
    serventias = []

# --- FORMULÁRIO DE ENTRADA ---
with st.form("formulario"):
    st.subheader("🔢 Dados da Serventia")

    nome_serventia = st.selectbox("Selecione a Serventia", options=serventias, index=0, placeholder="Digite para buscar...", label_visibility="visible")
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
    protocolo = str(uuid.uuid4()).split('-')[0].upper()
    dados = {
        "Protocolo": protocolo,
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

    if st.button("✅ Finalizar Cadastro e Gerar Protocolo"):
        html_content = f"""
        <html>
        <head><meta charset='utf-8'><title>COGEX REGISTRE-SE</title></head>
        <body style='font-family:sans-serif;'>
            <img src='COGEX.png' width='300'/>
            <h1>COGEX - REGISTRE-SE</h1>
            <p><strong>Obrigado pela sua participação!</strong></p>
            <p>Protocolo de envio: <strong>{protocolo}</strong></p>
            <hr/>
            <h3>Resumo do Cadastro</h3>
            {df_novo.to_html(index=False)}
        </body>
        </html>
        """
        with open("cogex_registre_se_confirmacao.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        with open("cogex_registre_se_confirmacao.html", "r", encoding="utf-8") as f:
            st.download_button(
                label="📄 Baixar Confirmação HTML",
                data=f.read(),
                file_name="cogex_registre_se_confirmacao.html",
                mime="text/html"
            )
