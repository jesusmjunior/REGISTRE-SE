import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Análise Semana Registre-se",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📝 Análise de Dados da Semana Registre-se")
st.markdown("### Decoupagem Lógica e Classificação Semântica")

# Estrutura semântica conforme especificado
ESTRUTURA_SEMANTICA = {
    'Carimbo de data/hora': {'classe': 'Metadado', 'atributo': 'Timestamp', 'tipo': 'datetime'},
    'Endereço de e-mail': {'classe': 'Contato', 'atributo': 'Email Principal', 'tipo': 'string'},
    'Identificação da Serventia Extrajudicial': {'classe': 'Identificação', 'atributo': 'Nome/ID da Serventia', 'tipo': 'string'},
    'E-mail': {'classe': 'Contato', 'atributo': 'Email Secundário', 'tipo': 'string'},
    'Whatsapp': {'classe': 'Contato', 'atributo': 'Canal Instantâneo', 'tipo': 'string'},
    'Foram realizadas ações na Semana "Registre-se" em maio de 2024?': {'classe': 'Participação', 'atributo': 'Resposta Sim/Não', 'tipo': 'categórica'},
    'Em caso de resposta NÃO ao quesito anterior, qual o motivo da não participação na Semana Registre-se?': {'classe': 'Justificativa', 'atributo': 'Texto Livre', 'tipo': 'string (texto)'},
    'Quais as ações realizadas na Semana Registre-se? Identifique-as por dia, se possível.': {'classe': 'Ações', 'atributo': 'Descrição das Ações', 'tipo': 'string (texto)'},
    'Marque as opções dos públicos atendidos:': {'classe': 'Público-Alvo', 'atributo': 'Lista de Grupos Atendidos', 'tipo': 'multisseleção'},
    'Quantas 2ªs vias foram emitidas?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Segunda Via Emitida', 'tipo': 'inteiro'},
    'Quantos registros de nascimento foram feitos?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Registro de Nascimento', 'tipo': 'inteiro'},
    'Quantas averbações de paternidade foram feitas?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Averbações de Paternidade', 'tipo': 'inteiro'},
    'Quantas retificações de registro de nascimento foram iniciadas ou processadas?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Retificações de Registro', 'tipo': 'inteiro'},
    'Quantos registros tardios de nascimento foram iniciados ou processados?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Registros Tardios', 'tipo': 'inteiro'},
    'Quantas restaurações de registro de nascimento foram iniciados ou processados?': {'classe': 'Indicadores Quantitativos', 'atributo': 'Restaurações de Registro', 'tipo': 'inteiro'},
    'Classificação': {'classe': 'Classificação Administrativa', 'atributo': 'Categoria da Serventia', 'tipo': 'categórica'},
    'Tags': {'classe': 'Semântica Expandida', 'atributo': 'Etiquetas Temáticas', 'tipo': 'multirótulo'}
}

# Renomeação de colunas para facilitar o uso
MAPEAMENTO_COLUNAS = {
    'Carimbo de data/hora': 'data_hora',
    'Endereço de e-mail': 'email',
    'Identificação da Serventia Extrajudicial': 'serventia',
    'E-mail': 'email_contato',
    'Whatsapp': 'whatsapp',
    'Foram realizadas ações na Semana "Registre-se" em maio de 2024?': 'participou',
    'Em caso de resposta NÃO ao quesito anterior, qual o motivo da não participação na Semana Registre-se?': 'motivo_nao_participacao',
    'Quais as ações realizadas na Semana Registre-se? Identifique-as por dia, se possível.': 'acoes_realizadas',
    'Marque as opções dos públicos atendidos:': 'publicos_atendidos',
    'Quantas 2ªs vias foram emitidas?': 'qtd_segundas_vias',
    'Quantos registros de nascimento foram feitos?': 'qtd_registros_nascimento',
    'Quantas averbações de paternidade foram feitas?': 'qtd_averbacoes_paternidade',
    'Quantas retificações de registro de nascimento foram iniciadas ou processadas?': 'qtd_retificacoes',
    'Quantos registros tardios de nascimento foram iniciados ou processados?': 'qtd_registros_tardios',
    'Quantas restaurações de registro de nascimento foram iniciados ou processados?': 'qtd_restauracoes',
    'Classificação': 'classificacao',
    'Tags': 'tags'
}

# Função para carregar e limpar dados
@st.cache_data
def carregar_e_limpar_dados(arquivo):
    """
    Carrega e limpa os dados do arquivo Excel
    """
    try:
        df = pd.read_excel(arquivo)
        
        # Verificando quais colunas existem no DataFrame
        colunas_existentes = [col for col in MAPEAMENTO_COLUNAS.keys() if col in df.columns]
        mapeamento_filtrado = {col: MAPEAMENTO_COLUNAS[col] for col in colunas_existentes}
        
        # Renomeando apenas as colunas que existem
        if mapeamento_filtrado:
            df = df.rename(columns=mapeamento_filtrado)
        
        # Conversão de tipos de dados
        # Convertendo colunas numéricas
        colunas_numericas = [
            'qtd_segundas_vias', 'qtd_registros_nascimento', 
            'qtd_averbacoes_paternidade', 'qtd_retificacoes', 
            'qtd_registros_tardios', 'qtd_restauracoes'
        ]
        
        for coluna in colunas_numericas:
            if coluna in df.columns:
                df[coluna] = pd.to_numeric(df[coluna], errors='coerce').fillna(0).astype(int)
        
        # Conversão de data/hora
        if 'data_hora' in df.columns:
            df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
        
        # Criando campo de status de participação mais claro
        if 'participou' in df.columns:
            df['status_participacao'] = df['participou'].apply(
                lambda x: 'Participou' if str(x).upper() == 'SIM' else 'Não Participou'
            )
            
        return df
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# Função para obter a estrutura semântica agrupada por classe
def obter_estrutura_por_classe():
    """
    Agrupa a estrutura semântica por classe
    """
    classes_semanticas = {}
    for coluna_original, atributos in ESTRUTURA_SEMANTICA.items():
        classe = atributos['classe']
        if classe not in classes_semanticas:
            classes_semanticas[classe] = []
        
        classes_semanticas[classe].append({
            'coluna_original': coluna_original,
            'atributo': atributos['atributo'],
            'tipo': atributos['tipo']
        })
    
    return classes_semanticas

# Função para analisar a distribuição de participação
def analisar_participacao(df):
    """
    Analisa a distribuição de participação
    """
    if 'status_participacao' in df.columns:
        return df['status_participacao'].value_counts()
    elif 'participou' in df.columns:
        return df['participou'].value_counts()
    else:
        return None

# Função para analisar públicos atendidos
def analisar_publicos(df):
    """
    Analisa os públicos atendidos
    """
    if 'publicos_atendidos' not in df.columns:
        return None
    
    # Processando cada entrada de públicos
    publicos_contagem = {}
    
    # Processando cada entrada de públicos
    for publicos in df['publicos_atendidos'].dropna():
        # Dividindo múltiplas opções se estiverem separadas por vírgulas ou pontos
        opcoes = re.split(r'[,.]', str(publicos))
        
        for opcao in opcoes:
            opcao = opcao.strip()
            if opcao:
                publicos_contagem[opcao] = publicos_contagem.get(opcao, 0) + 1
    
    # Convertendo para DataFrame
    df_publicos = pd.DataFrame({
        'Público': list(publicos_contagem.keys()),
        'Contagem': list(publicos_contagem.values())
    }).sort_values(by='Contagem', ascending=False)
    
    return df_publicos

# Função para analisar indicadores quantitativos
def analisar_indicadores(df):
    """
    Analisa os indicadores quantitativos
    """
    colunas_metricas = [col for col in df.columns if col.startswith('qtd_')]
    if not colunas_metricas:
        return None
    
    # Estatísticas descritivas
    estatisticas = df[colunas_metricas].describe()
    
    # Somando totais
    totais = df[colunas_metricas].sum().to_frame('Total')
    
    # Contando participantes que reportaram valores > 0
    participantes = {}
    medias_ativas = {}
    
    for col in colunas_metricas:
        participantes[col] = (df[col] > 0).sum()
        
        # Calculando média apenas para serventias ativas
        ativos = df[df[col] > 0]
        if len(ativos) > 0:
            medias_ativas[col] = ativos[col].mean()
        else:
            medias_ativas[col] = 0
    
    return {
        'estatisticas': estatisticas,
        'totais': totais,
        'participantes': participantes,
        'medias_ativas': medias_ativas
    }

# Função para analisar palavras-chave nas ações
def analisar_palavras_chave(df):
    """
    Analisa palavras-chave presentes nas descrições de ações
    """
    if 'acoes_realizadas' not in df.columns:
        return None
    
    # Lista de stop words para remover
    stop_words = ['de', 'a', 'o', 'e', 'do', 'da', 'dos', 'das', 'para', 'com', 'em', 'no', 'na', 'por', 
                  'que', 'se', 'foi', 'como', 'uma', 'um', 'ou']
    
    # Processando cada entrada de ações
    palavras_chave = []
    
    for acoes in df['acoes_realizadas'].dropna():
        # Convertendo para string e transformando para minúsculas
        texto = str(acoes).lower()
        
        # Removendo caracteres especiais e dividindo em palavras
        palavras = re.findall(r'\b[a-záéíóúàâêôãõç]+\b', texto)
        
        # Filtrando palavras com mais de 3 letras e removendo stop words
        palavras = [p for p in palavras if len(p) > 3 and p not in stop_words]
        
        palavras_chave.extend(palavras)
    
    # Contando frequência das palavras-chave
    contador_palavras = {}
    for palavra in palavras_chave:
        contador_palavras[palavra] = contador_palavras.get(palavra, 0) + 1
    
    # Convertendo para DataFrame
    df_palavras = pd.DataFrame({
        'Palavra': list(contador_palavras.keys()),
        'Frequência': list(contador_palavras.values())
    }).sort_values(by='Frequência', ascending=False)
    
    return df_palavras

# Barra lateral
st.sidebar.title("Controles")

# Upload de arquivo
arquivo_uploaded = st.sidebar.file_uploader("Faça upload do arquivo Excel", type=["xlsx", "xls"])

# Verificação se o arquivo foi carregado
if arquivo_uploaded is not None:
    # Carregando e limpando os dados
    df = carregar_e_limpar_dados(arquivo_uploaded)
    
    if df is not None:
        st.sidebar.success(f"Arquivo carregado com sucesso! Total de registros: {len(df)}")
        
        # Menu de navegação
        pagina = st.sidebar.radio(
            "Navegue pelas seções:",
            ["📊 Visão Geral", 
             "🔍 Decoupagem Lógica",
             "📋 Análise de Participação", 
             "📈 Indicadores Quantitativos",
             "👥 Públicos Atendidos",
             "🔠 Análise Textual"]
        )
        
        # Visão Geral
        if pagina == "📊 Visão Geral":
            st.header("📊 Visão Geral dos Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total de Registros", len(df))
                
                participacao = analisar_participacao(df)
                if participacao is not None:
                    st.metric("Serventias Participantes", 
                              participacao.get('Participou', 0) if 'Participou' in participacao else 
                              participacao.get('SIM', 0) if 'SIM' in participacao else 0)
            
            with col2:
                indicadores = analisar_indicadores(df)
                if indicadores is not None:
                    total_servicos = indicadores['totais']['Total'].sum()
                    st.metric("Total de Serviços Realizados", f"{total_servicos:,}".replace(",", "."))
                    
                    # Maior indicador
                    maior_indicador = indicadores['totais'].idxmax()[0]
                    maior_valor = indicadores['totais'].max()[0]
                    
                    nome_formatado = maior_indicador.replace('qtd_', '').replace('_', ' ').title()
                    st.metric("Serviço Mais Realizado", f"{nome_formatado}: {maior_valor:,}".replace(",", "."))
            
            # Gráfico de totais por serviço
            if indicadores is not None:
                st.subheader("Distribuição de Serviços")
                
                # Preparando os dados para o gráfico
                df_chart = indicadores['totais'].reset_index()
                df_chart.columns = ['Serviço', 'Total']
                
                # Renomeando serviços para exibição
                df_chart['Serviço'] = df_chart['Serviço'].apply(
                    lambda x: x.replace('qtd_', '').replace('_', ' ').title()
                )
                
                # Criando gráfico de barras horizontais usando Altair
                chart = alt.Chart(df_chart).mark_bar().encode(
                    x='Total:Q',
                    y=alt.Y('Serviço:N', sort='-x'),
                    tooltip=['Serviço', 'Total']
                ).properties(
                    height=300
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
            
            # Visão rápida dos dados
            with st.expander("Visualizar amostra dos dados"):
                st.dataframe(df.head(10))
        
        # Decoupagem Lógica
        elif pagina == "🔍 Decoupagem Lógica":
            st.header("🔍 Decoupagem Lógica e Classificação Semântica")
            
            st.markdown("""
            A tabela abaixo mostra a estrutura semântica aplicada aos dados da Semana Registre-se, 
            organizando as colunas em classes semânticas com seus respectivos atributos e tipos de dados.
            """)
            
            # Obter estrutura semântica
            classes_semanticas = obter_estrutura_por_classe()
            
            # Criar abas para cada classe semântica
            tabs = st.tabs([classe for classe in classes_semanticas.keys()])
            
            for i, (classe, tab) in enumerate(zip(classes_semanticas.keys(), tabs)):
                with tab:
                    st.subheader(f"Classe: {classe}")
                    
                    # Criando DataFrame para exibir a estrutura
                    df_estrutura = pd.DataFrame(classes_semanticas[classe])
                    
                    # Adicionando coluna de existência nos dados
                    df_estrutura['Presente nos Dados'] = df_estrutura['coluna_original'].apply(
                        lambda x: "✅ Sim" if x in df.columns or MAPEAMENTO_COLUNAS.get(x) in df.columns else "❌ Não"
                    )
                    
                    # Renomeando colunas para exibição
                    df_estrutura = df_estrutura.rename(columns={
                        'coluna_original': 'Coluna Original',
                        'atributo': 'Atributo',
                        'tipo': 'Tipo de Dado'
                    })
                    
                    st.dataframe(df_estrutura[['Coluna Original', 'Atributo', 'Tipo de Dado', 'Presente nos Dados']], 
                                use_container_width=True)
            
            # Mostrar mapeamento de colunas renomeadas
            with st.expander("Ver mapeamento de colunas renomeadas"):
                st.subheader("Mapeamento de Colunas")
                
                mapeamento_df = pd.DataFrame([
                    {"Coluna Original": col_orig, "Coluna Renomeada": col_nova}
                    for col_orig, col_nova in MAPEAMENTO_COLUNAS.items()
                    if col_orig in df.columns
                ])
                
                st.dataframe(mapeamento_df, use_container_width=True)
        
        # Análise de Participação
        elif pagina == "📋 Análise de Participação":
            st.header("📋 Análise de Participação")
            
            participacao = analisar_participacao(df)
            
            if participacao is not None:
                # Métricas
                col1, col2, col3 = st.columns(3)
                
                total = participacao.sum()
                
                # Identificando valores de participação
                sim_key = 'Participou' if 'Participou' in participacao else 'SIM' if 'SIM' in participacao else None
                nao_key = 'Não Participou' if 'Não Participou' in participacao else 'NÃO' if 'NÃO' in participacao else None
                
                participaram = participacao.get(sim_key, 0) if sim_key else 0
                nao_participaram = participacao.get(nao_key, 0) if nao_key else 0
                
                with col1:
                    st.metric("Total de Respostas", total)
                
                with col2:
                    st.metric("Participaram", participaram)
                    porcentagem_sim = (participaram / total * 100) if total > 0 else 0
                    st.caption(f"{porcentagem_sim:.1f}% do total")
                
                with col3:
                    st.metric("Não Participaram", nao_participaram)
                    porcentagem_nao = (nao_participaram / total * 100) if total > 0 else 0
                    st.caption(f"{porcentagem_nao:.1f}% do total")
                
                # Gráfico de participação
                st.subheader("Distribuição de Participação")
                
                df_chart = pd.DataFrame({
                    'Status': participacao.index,
                    'Quantidade': participacao.values
                })
                
                chart = alt.Chart(df_chart).mark_arc().encode(
                    theta=alt.Theta(field="Quantidade", type="quantitative"),
                    color=alt.Color(field="Status", type="nominal", 
                                   scale=alt.Scale(
                                       domain=[sim_key, nao_key] if sim_key and nao_key else None,
                                       range=['#2ecc71', '#e74c3c'] if sim_key and nao_key else None
                                   )),
                    tooltip=['Status', 'Quantidade']
                ).properties(
                    width=400,
                    height=400
                )
                
                st.altair_chart(chart, use_container_width=True)
                
                # Análise de motivos de não participação
                if 'motivo_nao_participacao' in df.columns:
                    st.subheader("Motivos para Não Participação")
                    
                    # Filtrando apenas serventias que não participaram
                    nao_participaram_df = df[df['status_participacao'] == 'Não Participou'] if 'status_participacao' in df.columns else \
                                          df[df['participou'].str.upper() == 'NÃO'] if 'participou' in df.columns else pd.DataFrame()
                    
                    if not nao_participaram_df.empty:
                        motivos = nao_participaram_df['motivo_nao_participacao'].value_counts()
                        
                        if not motivos.empty:
                            df_motivos = pd.DataFrame({
                                'Motivo': motivos.index,
                                'Quantidade': motivos.values
                            })
                            
                            # Limitando a 10 motivos mais comuns
                            if len(df_motivos) > 10:
                                df_motivos = df_motivos.head(10)
                                st.caption("Mostrando os 10 motivos mais comuns")
                            
                            chart = alt.Chart(df_motivos).mark_bar().encode(
                                x='Quantidade:Q',
                                y=alt.Y('Motivo:N', sort='-x'),
                                tooltip=['Motivo', 'Quantidade']
                            ).properties(
                                height=30 * len(df_motivos)  # Altura dinâmica baseada no número de motivos
                            )
                            
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.info("Nenhum motivo registrado para não participação.")
                    else:
                        st.info("Não foram encontrados registros de serventias que não participaram.")
            else:
                st.warning("Não foi possível analisar a participação. Verifique se a coluna de participação existe nos dados.")
        
        # Indicadores Quantitativos
        elif pagina == "📈 Indicadores Quantitativos":
            st.header("📈 Indicadores Quantitativos")
            
            indicadores = analisar_indicadores(df)
            
            if indicadores is not None:
                # Métricas principais
                total_servicos = indicadores['totais']['Total'].sum()
                
                st.metric("Total de Serviços Realizados", f"{total_servicos:,}".replace(",", "."))
                
                # Tabela de indicadores
                st.subheader("Resumo dos Indicadores")
                
                # Criando DataFrame para exibição
                dados_tabela = []
                
                for col in indicadores['totais'].index:
                    nome_formatado = col.replace('qtd_', '').replace('_', ' ').title()
                    total = int(indicadores['totais'].loc[col, 'Total'])
                    participantes = indicadores['participantes'][col]
                    media_geral = indicadores['estatisticas'].loc['mean', col]
                    media_ativa = indicadores['medias_ativas'][col]
                    maximo = int(indicadores['estatisticas'].loc['max', col])
                    
                    percentual = (total / total_servicos * 100) if total_servicos > 0 else 0
                    
                    dados_tabela.append({
                        'Serviço': nome_formatado,
                        'Total': total,
                        'Percentual': f"{percentual:.1f}%",
                        'Serventias Ativas': participantes,
                        'Média p/ Ativa': f"{media_ativa:.1f}",
                        'Máximo': maximo
                    })
                
                df_tabela = pd.DataFrame(dados_tabela)
                st.dataframe(df_tabela, use_container_width=True)
                
                # Gráfico de totais por serviço
                st.subheader("Distribuição dos Serviços")
                
                # Preparando os dados para o gráfico
                df_chart = indicadores['totais'].reset_index()
                df_chart.columns = ['Serviço', 'Total']
                
                # Renomeando serviços para exibição
                df_chart['Serviço'] = df_chart['Serviço'].apply(
                    lambda x: x.replace('qtd_', '').replace('_', ' ').title()
                )
                
                # Calculando percentual
                df_chart['Percentual'] = df_chart['Total'] / df_chart['Total'].sum() * 100
                df_chart['Rótulo'] = df_chart.apply(
                    lambda x: f"{x['Serviço']}: {x['Total']:,} ({x['Percentual']:.1f}%)".replace(",", "."), 
                    axis=1
                )
                
                # Criando gráfico de pizza usando Altair
                chart = alt.Chart(df_chart).mark_arc().encode(
                    theta=alt.Theta(field="Total", type="quantitative"),
                    color=alt.Color(field="Serviço", type="nominal", 
                                   scale=alt.Scale(scheme='category10')),
                    tooltip=['Serviço', 'Total', 'Percentual:Q']
                ).properties(
                    width=500,
                    height=500
                )
                
                text = alt.Chart(df_chart).mark_text(radius=170, size=12).encode(
                    theta=alt.Theta(field="Total", type="quantitative"),
                    text=alt.Text('Rótulo:N')
                )
                
                st.altair_chart(chart + text, use_container_width=True)
                
                # Histograma de distribuição para cada indicador
                st.subheader("Distribuição de Valores por Serviço")
                
                # Seleção do indicador
                colunas_metricas = [col for col in df.columns if col.startswith('qtd_')]
                opcoes_indicadores = {col.replace('qtd_', '').replace('_', ' ').title(): col for col in colunas_metricas}
                
                indicador_selecionado = st.selectbox(
                    "Selecione o serviço para visualizar a distribuição:",
                    list(opcoes_indicadores.keys())
                )
                
                coluna_indicador = opcoes_indicadores[indicador_selecionado]
                
                # Filtrando apenas valores > 0
                df_filtered = df[df[coluna_indicador] > 0]
                
                if not df_filtered.empty:
                    # Criando histograma
                    hist = alt.Chart(df_filtered).mark_bar().encode(
                        alt.X(f'{coluna_indicador}:Q', bin=True, title=indicador_selecionado),
                        y='count()',
                        tooltip=['count()']
                    ).properties(
                        width=600,
                        height=400
                    )
                    
                    st.altair_chart(hist, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(f"Total de {indicador_selecionado}", 
                                 df[coluna_indicador].sum())
                    
                    with col2:
                        st.metric(f"Serventias com {indicador_selecionado} > 0", 
                                 len(df_filtered))
                else:
                    st.info(f"Não há registros com valores de {indicador_selecionado} maiores que zero.")
            else:
                st.warning("Não foi possível analisar os indicadores quantitativos. Verifique se as colunas existem nos dados.")
        
        # Públicos Atendidos
        elif pagina == "👥 Públicos Atendidos":
            st.header("👥 Análise de Públicos Atendidos")
            
            publicos = analisar_publicos(df)
            
            if publicos is not None and not publicos.empty:
                # Métricas
                st.metric
