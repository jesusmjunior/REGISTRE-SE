import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import datetime
import uuid
import re
import base64
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="COGEX - Semana Registre-se",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definição de cores da aplicação
COLOR_WINE = "#800020"  # Vinho
COLOR_RED = "#FF0000"   # Vermelho
COLOR_BLACK = "#222222" # Preto
COLOR_GOLD = "#D4AF37"  # Dourado

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        color: #800020;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        color: #222222;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .form-header {
        background-color: #800020;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 20px 0;
    }
    .error-message {
        background-color: #FF0000;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 20px 0;
    }
    .stButton>button {
        background-color: #800020;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #600018;
    }
    .cogex-footer {
        color: #800020;
        text-align: center;
        margin-top: 30px;
        font-weight: bold;
    }
    .cogex-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    div.stTabs button {
        background-color: #800020;
        color: white;
    }
    div.stTabs button[aria-selected="true"] {
        background-color: #D4AF37;
        color: #222222;
    }
</style>
""", unsafe_allow_html=True)

# Função para exibir o logotipo da COGEX
def display_logo():
    st.markdown(
        """
        <div class="cogex-logo">
            <img src="https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/cogex-logo.png" width="400">
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Se a imagem do link não carregar, podemos exibir um título alternativo
    st.markdown('<h1 class="main-header">CORREGEDORIA GERAL DO FORO EXTRAJUDICIAL</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header" style="text-align:center; color:#D4AF37; margin-top:-15px;">SEMANA REGISTRE-SE</h2>', unsafe_allow_html=True)

# Funções para manipulação de arquivos e autenticação
def create_database():
    """Cria um modelo de banco de dados vazio se ele não existir"""
    db_path = "Modelo_DB_Semana_Registre-se.xlsx"
    
    if not os.path.exists(db_path):
        # Criar um DataFrame vazio com as colunas necessárias
        df = pd.DataFrame({
            'ID_REGISTRO': [],
            'NOME_SERVENTIA': [],
            'UF': [],
            'CARIMBO_TEORA': [],
            'EMAIL_INSTITUCIONAL': [],
            'TELEFONE_WHATSAPP': [],
            'PARTICIPA_SEMANA': [],
            'MOTIVO_PARTICIPACAO': [],
            'CLASSE': [],
            'ATRIBUTO': [],
            'GRAU_PERTENCIMENTO': [],
            'GRAU_CONEXAO': [],
            'JUSTIFICATIVA_OBSERVACAO': [],
            'OUTROS': [],
            'DATA_HORA_REGISTRO': []
        })
        
        # Adicionar dados de exemplo
        example_data = [
            {
                'ID_REGISTRO': f"REG-{uuid.uuid4().hex[:8].upper()}",
                'NOME_SERVENTIA': "1º Ofício de Registro Civil de São Luís",
                'UF': "MA",
                'CARIMBO_TEORA': "",
                'EMAIL_INSTITUCIONAL': "cartorio1@exemplo.com.br",
                'TELEFONE_WHATSAPP': "(98) 98765-4321",
                'PARTICIPA_SEMANA': "Sim",
                'MOTIVO_PARTICIPACAO': "Subregistro",
                'CLASSE': "Participação",
                'ATRIBUTO': "Digital",
                'GRAU_PERTENCIMENTO': 0.9,
                'GRAU_CONEXAO': 0.8,
                'JUSTIFICATIVA_OBSERVACAO': "Participação para reduzir subregistros na região",
                'OUTROS': "",
                'DATA_HORA_REGISTRO': datetime.datetime.now()
            },
            {
                'ID_REGISTRO': f"REG-{uuid.uuid4().hex[:8].upper()}",
                'NOME_SERVENTIA': "2º Tabelionato de Notas de São Paulo",
                'UF': "SP",
                'CARIMBO_TEORA': "",
                'EMAIL_INSTITUCIONAL': "cartorio2@exemplo.com.br",
                'TELEFONE_WHATSAPP': "(11) 98765-4321",
                'PARTICIPA_SEMANA': "Sim",
                'MOTIVO_PARTICIPACAO': "Ações sociais",
                'CLASSE': "Engajamento",
                'ATRIBUTO': "Presencial",
                'GRAU_PERTENCIMENTO': 0.7,
                'GRAU_CONEXAO': 0.6,
                'JUSTIFICATIVA_OBSERVACAO': "Ações sociais planejadas para a comunidade local",
                'OUTROS': "",
                'DATA_HORA_REGISTRO': datetime.datetime.now()
            }
        ]
        
        # Adicionar os exemplos ao DataFrame
        for example in example_data:
            df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
        
        try:
            # Tentar salvar como Excel
            try:
                df.to_excel(db_path, index=False)
            except:
                # Se falhar, tentar instalar openpyxl
                import sys
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
                df.to_excel(db_path, index=False)
        except:
            # Se ainda falhar, tentar CSV
            df.to_csv("Modelo_DB_Semana_Registre-se.csv", index=False)
            db_path = "Modelo_DB_Semana_Registre-se.csv"
        
        st.success(f"Banco de dados criado com sucesso: {db_path}")
    
    return db_path

# Função para carregar o banco de dados
def load_database(db_path):
    """Carrega o banco de dados do arquivo Excel ou CSV"""
    try:
        if db_path.endswith('.xlsx'):
            try:
                df = pd.read_excel(db_path)
            except:
                st.error("Erro ao ler arquivo Excel. Tentando instalar openpyxl...")
                import sys
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
                df = pd.read_excel(db_path)
        elif db_path.endswith('.csv'):
            df = pd.read_csv(db_path)
        else:
            st.error("Formato de arquivo não suportado.")
            df = pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar o banco de dados: {e}")
        df = pd.DataFrame()
    
    return df

# Função para salvar o banco de dados
def save_database(df, db_path):
    """Salva o banco de dados para o arquivo Excel ou CSV"""
    try:
        if db_path.endswith('.xlsx'):
            df.to_excel(db_path, index=False)
        elif db_path.endswith('.csv'):
            df.to_csv(db_path, index=False)
        else:
            st.error("Formato de arquivo não suportado.")
            return False
        return True
    except Exception as e:
        st.error(f"Erro ao salvar o banco de dados: {e}")
        return False

# Função para adicionar um novo registro
def add_record(df, record, db_path):
    """Adiciona um novo registro ao banco de dados"""
    # Adicionar um ID único
    if 'ID_REGISTRO' not in record or not record['ID_REGISTRO']:
        record['ID_REGISTRO'] = f"REG-{uuid.uuid4().hex[:8].upper()}"
    
    # Adicionar timestamp
    if 'DATA_HORA_REGISTRO' not in record or not record['DATA_HORA_REGISTRO']:
        record['DATA_HORA_REGISTRO'] = datetime.datetime.now()
    
    # Adicionar o registro ao DataFrame
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    
    # Salvar o banco de dados
    if save_database(df, db_path):
        return df
    else:
        return None

# Funções para gerar o arquivo para download
def to_excel(df):
    """Converte o DataFrame para Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Semana_Registre-se')
    
    processed_data = output.getvalue()
    return processed_data

def get_download_link(df, filename="Modelo_DB_Semana_Registre-se.xlsx", text="Baixar arquivo Excel"):
    """Gera um link para download do DataFrame como Excel"""
    try:
        excel_data = to_excel(df)
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
        return href
    except:
        # Tentar CSV se Excel falhar
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename.replace(".xlsx", ".csv")}">{text} (CSV)</a>'
        return href

# Funções para análise e visualização de dados
def generate_kpis(df):
    """Gera os principais indicadores de desempenho"""
    kpis = {
        "Total de Serventias": len(df),
        "Estados Participantes": df['UF'].nunique(),
        "Taxa de Participação": f"{df['PARTICIPA_SEMANA'].value_counts().get('Sim', 0) / len(df) * 100:.1f}%" if len(df) > 0 else "0%",
        "Motivo Principal": df['MOTIVO_PARTICIPACAO'].value_counts().index[0] if len(df) > 0 and len(df['MOTIVO_PARTICIPACAO'].value_counts()) > 0 else "N/A"
    }
    return kpis

def plot_participation_by_state(df):
    """Cria um gráfico de barras mostrando a participação por estado"""
    if len(df) == 0:
        return None
    
    state_counts = df.groupby('UF').size().reset_index(name='counts')
    state_counts = state_counts.sort_values('counts', ascending=False)
    
    fig = px.bar(
        state_counts,
        x='UF',
        y='counts',
        title='Participação por Estado',
        labels={'counts': 'Número de Serventias', 'UF': 'Estado'},
        color_discrete_sequence=['#800020']  # Cor vinho
    )
    return fig

def plot_participation_reasons(df):
    """Cria um gráfico de pizza mostrando os motivos de participação"""
    if len(df) == 0 or df['MOTIVO_PARTICIPACAO'].isna().all():
        return None
    
    reason_counts = df['MOTIVO_PARTICIPACAO'].value_counts().reset_index()
    reason_counts.columns = ['Motivo', 'Contagem']
    
    fig = px.pie(
        reason_counts,
        values='Contagem',
        names='Motivo',
        title='Motivos de Participação',
        color_discrete_sequence=['#800020', '#FF0000', '#222222', '#444444']  # Cores: vinho, vermelho, preto, cinza escuro
    )
    return fig

# Verificar usuário e senha
def check_password():
    """Retorna `True` se a senha estiver correta, `False` caso contrário."""
    def password_entered():
        """Verifica se a senha inserida pelo usuário está correta."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuário", key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuário", key="username")
        st.text_input(
            "Senha", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Usuário ou senha incorretos")
        return False
    else:
        # Password correct.
        return True

# Interface de login simulada caso não consiga usar st.secrets
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Tentativa de usar st.secrets, se falhar, usamos autenticação simulada
try:
    if "passwords" in st.secrets:
        if check_password():
            st.session_state['logged_in'] = True
    else:
        # Se não houver secrets, usar autenticação simulada
        if not st.session_state['logged_in']:
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            
            if st.button("Login"):
                if username == "admin" and password == "cogex2025":
                    st.session_state['logged_in'] = True
                else:
                    st.error("😕 Usuário ou senha incorretos")
except:
    # Se houver algum erro, usar autenticação simulada
    if not st.session_state['logged_in']:
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Login"):
            if username == "admin" and password == "cogex2025":
                st.session_state['logged_in'] = True
            else:
                st.error("😕 Usuário ou senha incorretos")

# Aplicação principal (só mostrada após login)
if st.session_state['logged_in']:
    # Exibir o logo
    display_logo()
    
    # Inicializar o banco de dados
    db_path = create_database()
    df = load_database(db_path)
    
    # Criar abas para navegação
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Formulário", "📋 Registros"])
    
    # Aba de Dashboard
    with tab1:
        st.markdown('<h3 class="sub-header">Dashboard - Semana Registre-se</h3>', unsafe_allow_html=True)
        
        # Exibir KPIs
        kpis = generate_kpis(df)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Serventias", kpis["Total de Serventias"])
        with col2:
            st.metric("Estados Participantes", kpis["Estados Participantes"])
        with col3:
            st.metric("Taxa de Participação", kpis["Taxa de Participação"])
        with col4:
            st.metric("Motivo Principal", kpis["Motivo Principal"])
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            fig1 = plot_participation_by_state(df)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem dados suficientes para gerar o gráfico de participação por estado.")
        
        with col2:
            fig2 = plot_participation_reasons(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados suficientes para gerar o gráfico de motivos de participação.")
        
        # Download do banco de dados
        st.markdown("### Download do Banco de Dados")
        st.markdown(get_download_link(df), unsafe_allow_html=True)
    
    # Aba de Formulário
    with tab2:
        st.markdown('<h3 class="sub-header">Formulário de Registro - Semana Registre-se</h3>', unsafe_allow_html=True)
        
        with st.form("registro_form"):
            col1, col2 = st.columns(2)
            with col1:
                nome_serventia = st.text_input("Nome da Serventia", help="Nome completo da serventia")
                uf = st.selectbox("Estado (UF)", ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"])
                email = st.text_input("E-mail Institucional", help="E-mail oficial da serventia")
                telefone = st.text_input("Telefone/WhatsApp", help="Telefone com DDD")
            
            with col2:
                participa = st.radio("Participa da Semana?", ["Sim", "Não"])
                motivo = st.selectbox("Motivo da Participação", ["Subregistro", "Ações sociais", "Atendimento remoto", "Outros"])
                
                if motivo == "Outros":
                    outros_motivos = st.text_input("Especifique outro motivo")
                else:
                    outros_motivos = ""
                
                classe = st.selectbox("Classe de Participação", ["Participação", "Engajamento", "Infraestrutura", "Outros"])
                atributo = st.selectbox("Atributo", ["Digital", "Presencial", "Misto", "Outros"])
            
            justificativa = st.text_area("Justificativa/Observações", help="Informações adicionais relevantes")
            
            # Valores que serão preenchidos automaticamente
            grau_pertencimento = 0.8
            grau_conexao = 0.7
            
            submitted = st.form_submit_button("Enviar Registro")
            
            if submitted:
                # Validar e-mail
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Por favor, insira um e-mail válido.")
                elif not nome_serventia:
                    st.error("Por favor, insira o nome da serventia.")
                else:
                    # Verificar se o e-mail já existe
                    if email in df['EMAIL_INSTITUCIONAL'].values:
                        st.warning("Este e-mail já está registrado. Por favor, use outro e-mail.")
                    else:
                        # Criar o registro
                        record = {
                            'ID_REGISTRO': f"REG-{uuid.uuid4().hex[:8].upper()}",
                            'NOME_SERVENTIA': nome_serventia,
                            'UF': uf,
                            'CARIMBO_TEORA': "",
                            'EMAIL_INSTITUCIONAL': email,
                            'TELEFONE_WHATSAPP': telefone,
                            'PARTICIPA_SEMANA': participa,
                            'MOTIVO_PARTICIPACAO': motivo if motivo != "Outros" else outros_motivos,
                            'CLASSE': classe,
                            'ATRIBUTO': atributo,
                            'GRAU_PERTENCIMENTO': grau_pertencimento,
                            'GRAU_CONEXAO': grau_conexao,
                            'JUSTIFICATIVA_OBSERVACAO': justificativa,
                            'OUTROS': outros_motivos if motivo == "Outros" else "",
                            'DATA_HORA_REGISTRO': datetime.datetime.now()
                        }
                        
                        # Adicionar o registro
                        updated_df = add_record(df, record, db_path)
                        
                        if updated_df is not None:
                            df = updated_df
                            st.success("Registro adicionado com sucesso!")
                        else:
                            st.error("Ocorreu um erro ao adicionar o registro.")
    
    # Aba de Registros
    with tab3:
        st.markdown('<h3 class="sub-header">Lista de Registros</h3>', unsafe_allow_html=True)
        
        if len(df) > 0:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                uf_filter = st.multiselect("Filtrar por UF", options=sorted(df['UF'].unique()))
            with col2:
                participa_filter = st.multiselect("Filtrar por Participação", options=sorted(df['PARTICIPA_SEMANA'].unique()))
            with col3:
                motivo_filter = st.multiselect("Filtrar por Motivo", options=sorted(df['MOTIVO_PARTICIPACAO'].unique()))
            
            # Aplicar filtros
            filtered_df = df.copy()
            if uf_filter:
                filtered_df = filtered_df[filtered_df['UF'].isin(uf_filter)]
            if participa_filter:
                filtered_df = filtered_df[filtered_df['PARTICIPA_SEMANA'].isin(participa_filter)]
            if motivo_filter:
                filtered_df = filtered_df[filtered_df['MOTIVO_PARTICIPACAO'].isin(motivo_filter)]
            
            # Mostrar a tabela
            st.dataframe(
                filtered_df[['NOME_SERVENTIA',
