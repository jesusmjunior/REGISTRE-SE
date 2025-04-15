import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import time
from datetime import datetime

# Importando o processador sem dependência de tkinter
from dados import ProcessadorDadosRegistrese

# Configuração da página
st.set_page_config(
    page_title="Processador de Dados - Semana Registre-se",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição
st.title("📝 Processador de Dados da Semana Registre-se")
st.markdown("""
Esta aplicação processa e limpa os dados da Semana "Registre-se", gerando arquivos 
em formatos padronizados para análise posterior.
""")

# Instanciando o processador
@st.cache_resource
def get_processador():
    return ProcessadorDadosRegistrese()

processador = get_processador()

# Função para processar o arquivo
def processar_arquivo_uploaded(arquivo_uploaded):
    if arquivo_uploaded is None:
        return None, None
    
    # Exibindo informações do arquivo
    nome_arquivo = arquivo_uploaded.name
    tamanho = arquivo_uploaded.size / 1024  # Convertendo para KB
    
    st.sidebar.success(f"Arquivo carregado: {nome_arquivo} ({tamanho:.2f} KB)")
    
    # Lendo os bytes do arquivo
    bytes_data = arquivo_uploaded.read()
    
    # Adicionando informação de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Processamento simulado em etapas
    status_text.text("Analisando arquivo...")
    progress_bar.progress(10)
    time.sleep(0.5)
    
    status_text.text("Detectando formato e codificação...")
    progress_bar.progress(20)
    time.sleep(0.5)
    
    status_text.text("Processando dados...")
    progress_bar.progress(40)
    
    # Processando os dados
    df_processado = processador.processar_dados_from_bytes(bytes_data, nome_arquivo)
    
    progress_bar.progress(80)
    status_text.text("Finalizando processamento...")
    time.sleep(0.5)
    
    progress_bar.progress(100)
    status_text.text("Processamento concluído!")
    
    return df_processado, processador.log

# Função para gerar estatísticas
def gerar_estatisticas(df):
    stats = {}
    
    # Estatísticas gerais
    stats['total_registros'] = len(df)
    
    # Estatísticas de participação
    if 'status_participacao' in df.columns:
        stats['participacao'] = df['status_participacao'].value_counts().to_dict()
    
    # Estatísticas de indicadores
    colunas_numericas = [col for col in df.columns if col.startswith('qtd_')]
    stats['indicadores'] = {}
    
    for col in colunas_numericas:
        nome_formatado = col.replace('qtd_', '').replace('_', ' ').title()
        stats['indicadores'][nome_formatado] = {
            'total': int(df[col].sum()),
            'media': float(df[col].mean()),
            'maximo': int(df[col].max()),
            'serventias_ativas': int((df[col] > 0).sum())
        }
    
    return stats

# Sidebar para upload e controles
st.sidebar.title("Controles")

# Upload de arquivo
arquivo_uploaded = st.sidebar.file_uploader(
    "Selecione o arquivo de dados", 
    type=["xlsx", "xls", "csv", "txt"],
    help="Arquivo da Semana Registre-se. Compatível com Excel, CSV e TXT"
)

# Opções de processamento
if arquivo_uploaded:
    st.sidebar.subheader("Opções de Exportação")
    
    formatos_exportacao = st.sidebar.multiselect(
        "Selecione os formatos para exportação",
        ["CSV", "Excel", "TXT"],
        default=["CSV", "Excel"]
    )
    
    normalizar_texto = st.sidebar.checkbox(
        "Normalizar texto (remover acentos)",
        value=True,
        help="Remove acentos e caracteres especiais"
    )
    
    # Botão de processamento
    processar = st.sidebar.button("Processar Arquivo", type="primary")
    
    if processar:
        # Processando o arquivo
        df_processado, logs = processar_arquivo_uploaded(arquivo_uploaded)
        
        if df_processado is not None:
            # Armazenando o dataframe processado na sessão
            st.session_state['df_processado'] = df_processado
            st.session_state['logs'] = logs
            st.session_state['estatisticas'] = gerar_estatisticas(df_processado)
            
            # Gera os arquivos para download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_base = os.path.splitext(arquivo_uploaded.name)[0]
            
            if "CSV" in formatos_exportacao:
                csv_data = df_processado.to_csv(index=False).encode('utf-8')
                st.session_state['csv_data'] = csv_data
                st.session_state['csv_nome'] = f"{nome_base}_processado_{timestamp}.csv"
            
            if "Excel" in formatos_exportacao:
                excel_buffer = io.BytesIO()
                df_processado.to_excel(excel_buffer, index=False)
                excel_data = excel_buffer.getvalue()
                st.session_state['excel_data'] = excel_data
                st.session_state['excel_nome'] = f"{nome_base}_processado_{timestamp}.xlsx"
            
            if "TXT" in formatos_exportacao:
                txt_data = df_processado.to_csv(sep='\t', index=False).encode('utf-8')
                st.session_state['txt_data'] = txt_data
                st.session_state['txt_nome'] = f"{nome_base}_processado_{timestamp}.txt"

# Conteúdo principal
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visão Geral", 
    "🔍 Dados Processados", 
    "📋 Logs de Processamento",
    "💾 Download de Arquivos"
])

# Tab 1: Visão Geral
with tab1:
    if 'df_processado' in st.session_state:
        df = st.session_state['df_processado']
        stats = st.session_state['estatisticas']
        
        # Layout de estatísticas em 3 colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", stats['total_registros'])
        
        if 'participacao' in stats:
            participou = stats['participacao'].get('Participou', 0)
            nao_participou = stats['participacao'].get('Não Participou', 0)
            
            with col2:
                st.metric("Serventias Participantes", participou)
            
            with col3:
                st.metric("Serventias Não Participantes", nao_participou)
        
        # Estatísticas de indicadores
        if 'indicadores' in stats and stats['indicadores']:
            st.subheader("Indicadores Quantitativos")
            
            # Criando dados para o gráfico
            indicadores = stats['indicadores']
            dados_grafico = []
            
            for nome, valores in indicadores.items():
                dados_grafico.append({
                    "Indicador": nome,
                    "Total": valores['total']
                })
            
            df_grafico = pd.DataFrame(dados_grafico)
            
            # Exibindo tabela de indicadores
            st.dataframe(
                df_grafico.style.highlight_max(subset=['Total'], color='lightgreen'),
                use_container_width=True
            )
            
            # Exibindo gráfico de barras
            st.bar_chart(df_grafico.set_index('Indicador'))
        
        # Gráfico de pizza para participação
        if 'participacao' in stats:
            st.subheader("Distribuição de Participação")
            
            # Criando DataFrame para o gráfico
            df_participacao = pd.DataFrame({
                'Status': list(stats['participacao'].keys()),
                'Quantidade': list(stats['participacao'].values())
            })
            
            # Exibindo o gráfico
            st.pie_chart(df_participacao.set_index('Status'))
    else:
        st.info("Carregue um arquivo e clique em 'Processar Arquivo' para visualizar os resultados.")

# Tab 2: Dados Processados
with tab2:
    if 'df_processado' in st.session_state:
        df = st.session_state['df_processado']
        
        # Controles para filtragem
        st.subheader("Dados Processados")
        
        # Opções de filtro
        filtro_col1, filtro_col2 = st.columns(2)
        
        with filtro_col1:
            if 'status_participacao' in df.columns:
                filtro_participacao = st.multiselect(
                    "Filtrar por Participação",
                    options=df['status_participacao'].unique(),
                    default=df['status_participacao'].unique()
                )
            else:
                filtro_participacao = None
        
        with filtro_col2:
            filtro_registros = st.slider(
                "Número máximo de registros",
                min_value=10,
                max_value=len(df),
                value=min(100, len(df)),
                step=10
            )
