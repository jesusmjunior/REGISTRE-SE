import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import json
import uuid
import os
import io

# Configurações do GitHub
GITHUB_TOKEN = st.secrets.get("GH_TOKEN")  # Token de acesso
REPO_OWNER = "jesusmjunior"  # Usuário do GitHub
REPO_NAME = "REGISTRE-SE"    # Nome do repositório
FILE_PATH = "REGISTRE-SE COGEX - Página1.csv"  # Caminho do arquivo CSV
GITHUB_API_BASE = "https://api.github.com"

# Configuração da página
st.set_page_config(page_title="Formulário de Participação COGEX", layout="centered", page_icon="📋")

# Função para carregar JSON com tratamento de erro
def carregar_json(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar {caminho_arquivo}: {e}")
        return None

# Função para salvar dados no GitHub via API
def salvar_dados_github(dados):
    # Validar token de acesso
    if not GITHUB_TOKEN:
        st.error("Token de acesso do GitHub não configurado.")
        return False
    
    try:
        # Cabeçalhos para autenticação
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # URL da API do GitHub
        url_get = f"{GITHUB_API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        
        # Obter conteúdo atual do arquivo
        response_get = requests.get(url_get, headers=headers)
        
        # Preparar DataFrame
        if response_get.status_code == 200:
            # Decodificar conteúdo existente
            current_content = base64.b64decode(response_get.json()['content']).decode('utf-8')
            df_existente = pd.read_csv(io.StringIO(current_content))
            current_sha = response_get.json()['sha']
        else:
            # Criar DataFrame vazio se arquivo não existir
            df_existente = pd.DataFrame(columns=list(dados.keys()))
            current_sha = None
        
        # Adicionar novo registro
        df_novo = pd.DataFrame([dados])
        df_combinado = pd.concat([df_existente, df_novo], ignore_index=True)
        
        # Converter para CSV
        csv_content = df_combinado.to_csv(index=False)
        
        # Codificar para base64
        csv_base64 = base64.b64encode(csv_content.encode()).decode()
        
        # Preparar payload para atualização
        payload = {
            "message": f"Adicionar registro - {dados['Protocolo']}",
            "content": csv_base64,
            "sha": current_sha
        }
        
        # Enviar atualização
        response_put = requests.put(url_get, headers=headers, json=payload)
        
        # Verificar resposta
        if response_put.status_code in [200, 201]:
            st.success("Registro salvo com sucesso no GitHub!")
            return True
        else:
            st.error(f"Falha ao salvar no GitHub. Erro: {response_put.text}")
            return False
    
    except Exception as e:
        st.error(f"Erro ao salvar dados no GitHub: {e}")
        return False

# Carregar serventias
def carregar_serventias():
    data = carregar_json("serventias_registre_se.json")
    return [s["nome"] for s in data["serventias"]] if data else []

# Preparar opções de públicos
def preparar_opcoes_publicos():
    data = carregar_json("publico_atendido.json")
    if not data:
        return []
    
    opcoes = []
    for grupo in data["publico_atendido"]["grupos"]:
        grupo_nome = grupo["nome"]
        for valor in grupo["valores"]:
            opcoes.append(f"{grupo_nome}: {valor}")
    return opcoes

# Função para gerar protocolo único
def gerar_protocolo():
    return str(uuid.uuid4()).split('-')[0].upper()

# Função para salvar dados localmente (backup)
def salvar_dados_local(dados):
    try:
        # Criar diretório de logs se não existir
        os.makedirs("logs", exist_ok=True)
        
        # Salvar em arquivo JSON
        arquivo_log = f"logs/registro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo_log, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados localmente: {e}")
        return False

# Função para gerar HTML de confirmação
def gerar_html_confirmacao(dados):
    df_novo = pd.DataFrame([dados])
    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>COGEX REGISTRE-SE - Confirmação de Cadastro</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1, h2 {{ color: #333; }}
            .protocolo {{ background-color: #f0f0f0; padding: 10px; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div style='text-align: center;'>
            <h1>COGEX - REGISTRE-SE</h1>
        </div>
        
        <div class='protocolo'>
            <h2>Comprovante de Participação</h2>
            <p><strong>Protocolo de envio:</strong> {dados['Protocolo']}</p>
            <p><strong>Data de Registro:</strong> {dados['Carimbo de data/hora']}</p>
        </div>

        <h3>Resumo do Cadastro</h3>
        {df_novo.to_html(index=False, classes='dataframe')}

        <p style='margin-top: 20px; color: #666;'>
            <strong>Importante:</strong> Este documento serve como comprovante de registro. 
            Mantenha-o em local seguro.
        </p>
    </body>
    </html>
    """
    return html_content

# Aplicação Streamlit Principal
def main():
    # Título e introdução
    st.title("📅 Formulário de Registro de Serventia")
    st.markdown("**Semana Registre-se - Maio de 2024**")
    
    # Carregamento inicial de dados
    serventias = carregar_serventias()
    opcoes_publicos = preparar_opcoes_publicos()

    # Formulário principal
    with st.form("formulario_registro", clear_on_submit=True):
        st.subheader("🏢 Identificação da Serventia")
        
        # Dados básicos da serventia
        col1, col2 = st.columns(2)
        with col1:
            nome_serventia = st.selectbox(
                "Selecione a Serventia", 
                options=serventias, 
                index=0, 
                placeholder="Escolha a serventia..."
            )
        with col2:
            email = st.text_input("E-mail de contato", help="Insira o endereço de e-mail oficial da serventia")
        
        telefone = st.text_input("Whatsapp para contato", help="Número para comunicação oficial")

        # Seção de informações da semana Registre-se
        st.subheader("📊 Detalhes da Participação")
        
        participa_semana = st.selectbox(
            "Participação na Semana Registre-se", 
            ["Sim", "Não"], 
            help="Indique se foram realizadas ações durante o evento"
        )

        # Campos condicionais
        if participa_semana == "Não":
            motivo_nao_part = st.text_area(
                "Motivo da não participação", 
                help="Explique brevemente por que não houve participação"
            )
            acoes_realizadas = ""
        else:
            motivo_nao_part = ""
            acoes_realizadas = st.text_area(
                "Descreva as ações realizadas", 
                help="Detalhe as atividades por dia, se possível"
            )

        # Públicos atendidos (múltipla escolha)
        publicos_atendidos = st.multiselect(
            "Públicos atendidos durante o evento", 
            options=opcoes_publicos,
            help="Selecione todos os grupos sociais alcançados"
        )

        # Métricas de atendimento
        st.subheader("📈 Métricas de Atendimento")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            vias_emitidas = st.number_input("2ª Vias", min_value=0, help="Total de segundas vias emitidas")
            registros_nasc = st.number_input("Registros de Nascimento", min_value=0)
        
        with col2:
            averbacoes_pat = st.number_input("Averbações de Paternidade", min_value=0)
            retificacoes = st.number_input("Retificações de Registro", min_value=0)
        
        with col3:
            registros_tardios = st.number_input("Registros Tardios", min_value=0)
            restauracoes = st.number_input("Restaurações de Registro", min_value=0)

        # Classificação e tags
        classificacao = st.selectbox(
            "Classificação da Participação", 
            ["Infraestrutura", "Engajamento", "Participação"]
        )
        tags = st.text_input("Tags adicionais", help="Palavras-chave separadas por vírgula")

        # Botão de submissão
        enviado = st.form_submit_button("📥 Registrar Participação")

    # Processamento dos dados após submissão
    if enviado:
        # Validações básicas
        if not nome_serventia:
            st.error("Por favor, selecione a serventia.")
            return
        
        if participa_semana == "Sim" and not acoes_realizadas:
            st.error("Para participação, descreva as ações realizadas.")
            return

        # Preparar dados para registro
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        protocolo = gerar_protocolo()
        
        dados = {
            "Protocolo": protocolo,
            "Carimbo de data/hora": data_hora,
            "Identificação da Serventia Extrajudicial": nome_serventia,
            "Endereço de e-mail": email,
            "Whatsapp": telefone,
            "Participação na Semana Registre-se": participa_semana,
            "Motivo da não participação": motivo_nao_part,
            "Ações realizadas": acoes_realizadas,
            "Públicos atendidos": ", ".join(publicos_atendidos),
            "2as vias emitidas": vias_emitidas,
            "Registros de nascimento": registros_nasc,
            "Averbações de paternidade": averbacoes_pat,
            "Retificações de registro": retificacoes,
            "Registros tardios": registros_tardios,
            "Restaurações de registro": restauracoes,
            "Classificação": classificacao,
            "Tags": tags
        }

        # Tentar salvar dados no GitHub
        sheets_salvo = salvar_dados_github(dados)
        
        # Salvar backup local independentemente do resultado
        salvar_dados_local(dados)

        if sheets_salvo:
            # Criar DataFrame para exibição
            df_novo = pd.DataFrame([dados])
            
            # Mensagens de sucesso
            st.success(f"✅ Registro realizado com sucesso! Protocolo: {protocolo}")
            st.dataframe(df_novo)

            # Gerar HTML de confirmação
            html_confirmacao = gerar_html_confirmacao(dados)
            
            # Botão para download do HTML
            st.download_button(
                label="📄 Baixar Comprovante",
                data=html_confirmacao,
                file_name=f"comprovante_registrese_{protocolo}.html",
                mime="text/html",
                help="Baixe o comprovante de participação"
            )
        else:
            st.error("Falha ao salvar o registro. Verifique sua conexão.")

# Execução da aplicação
if __name__ == "__main__":
    main()
