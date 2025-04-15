#!/usr/bin/env python
# coding: utf-8

# Verificando se o matplotlib está instalado e instalando se necessário
try:
    import matplotlib.pyplot as plt
except ImportError:
    import sys
    import subprocess
    
    # Instalando o matplotlib
    print("Instalando matplotlib...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    
    # Tentando importar novamente após a instalação
    import matplotlib.pyplot as plt

# Importações adicionais
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime

# Classe para processamento de metadados da Semana Registre-se
class MetadadoRegistreSe:
    def __init__(self, caminho_arquivo=None, df=None):
        """
        Inicializa o processador de metadados
        
        Args:
            caminho_arquivo: Caminho para o arquivo Excel (opcional)
            df: DataFrame pré-carregado (opcional)
        """
        self.caminho_arquivo = caminho_arquivo
        self.df = df
        
        # Estrutura semântica conforme especificado
        self.estrutura_semantica = {
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
        
        # Se um caminho de arquivo foi fornecido, carrega os dados
        if caminho_arquivo and df is None:
            self.carregar_dados()
    
    def carregar_dados(self):
        """
        Carrega os dados do arquivo Excel
        """
        try:
            self.df = pd.read_excel(self.caminho_arquivo)
            print(f"Arquivo importado com sucesso. Total de registros: {len(self.df)}")
            return True
        except Exception as e:
            print(f"Erro ao importar o arquivo: {e}")
            return False
    
    def limpar_dados(self):
        """
        Realiza a limpeza e transformação dos dados
        """
        if self.df is None:
            print("Nenhum dado carregado para limpar.")
            return None
        
        # Criando uma cópia para não alterar o original
        df_limpo = self.df.copy()
        
        # Renomeando colunas para facilitar o uso (opcional)
        mapeamento_colunas = {
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
        
        # Verificando quais colunas existem no DataFrame
        colunas_existentes = [col for col in mapeamento_colunas.keys() if col in df_limpo.columns]
        mapeamento_filtrado = {col: mapeamento_colunas[col] for col in colunas_existentes}
        
        # Renomeando apenas as colunas que existem
        if mapeamento_filtrado:
            df_limpo = df_limpo.rename(columns=mapeamento_filtrado)
        
        # Conversão de tipos de dados
        # Convertendo colunas numéricas
        colunas_numericas = [
            'qtd_segundas_vias', 'qtd_registros_nascimento', 
            'qtd_averbacoes_paternidade', 'qtd_retificacoes', 
            'qtd_registros_tardios', 'qtd_restauracoes'
        ]
        
        for coluna in colunas_numericas:
            if coluna in df_limpo.columns:
                df_limpo[coluna] = pd.to_numeric(df_limpo[coluna], errors='coerce').fillna(0).astype(int)
        
        # Conversão de data/hora
        if 'data_hora' in df_limpo.columns:
            df_limpo['data_hora'] = pd.to_datetime(df_limpo['data_hora'], errors='coerce')
        
        # Criando campo de status de participação mais claro
        if 'participou' in df_limpo.columns:
            df_limpo['status_participacao'] = df_limpo['participou'].apply(
                lambda x: 'Participou' if str(x).upper() == 'SIM' else 'Não Participou'
            )
        
        return df_limpo
    
    def obter_classificacao_semantica(self):
        """
        Retorna a classificação semântica das colunas
        """
        # Organizando por classe semântica
        classes_semanticas = {}
        for coluna_original, atributos in self.estrutura_semantica.items():
            classe = atributos['classe']
            if classe not in classes_semanticas:
                classes_semanticas[classe] = []
            
            classes_semanticas[classe].append({
                'coluna_original': coluna_original,
                'atributo': atributos['atributo'],
                'tipo': atributos['tipo']
            })
        
        return classes_semanticas
    
    def analisar_dados(self, df=None):
        """
        Realiza análise básica dos dados
        """
        if df is None:
            df = self.df
            
        if df is None:
            print("Nenhum dado disponível para análise.")
            return
        
        print("\n===== ANÁLISE BÁSICA DOS DADOS =====")
        
        # Estatísticas das colunas numéricas
        colunas_numericas = [col for col in df.columns if col.startswith('qtd_')]
        
        if colunas_numericas:
            print("\nEstatísticas das métricas quantitativas:")
            print(df[colunas_numericas].describe())
            
            # Soma total de cada métrica
            print("\nTotal por tipo de serviço:")
            for col in colunas_numericas:
                nome_formatado = col.replace('qtd_', '').replace('_', ' ').title()
                print(f"{nome_formatado}: {df[col].sum()}")
        
        # Análise de participação
        if 'status_participacao' in df.columns:
            print("\nDistribuição de participação:")
            print(df['status_participacao'].value_counts())
        elif 'participou' in df.columns:
            print("\nDistribuição de participação:")
            print(df['participou'].value_counts())
        
        # Análise de públicos atendidos
        if 'publicos_atendidos' in df.columns:
            print("\nPúblicos atendidos (top 5 mais comuns):")
            print(df['publicos_atendidos'].value_counts().head(5))
    
    def visualizar_metricas(self, df=None, salvar_fig=True):
        """
        Gera visualizações das métricas quantitativas
        """
        if df is None:
            df = self.df
            
        if df is None:
            print("Nenhum dado disponível para visualização.")
            return
        
        # Verificando as colunas métricas
        colunas_metricas = [col for col in df.columns if col.startswith('qtd_')]
        
        if not colunas_metricas:
            print("Nenhuma coluna de métrica encontrada para visualização.")
            return
        
        # Criando figura para gráfico de barras das métricas
        plt.figure(figsize=(14, 8))
        
        # Somando os valores das métricas
        somas_metricas = df[colunas_metricas].sum().sort_values(ascending=False)
        
        # Ajustando nomes para exibição
        nomes_formatados = [col.replace('qtd_', '').replace('_', ' ').title() for col in somas_metricas.index]
        
        # Criando o gráfico de barras
        sns.barplot(x=somas_metricas.values, y=nomes_formatados)
        plt.title('Total de Serviços Realizados na Semana Registre-se', fontsize=16)
        plt.xlabel('Quantidade', fontsize=12)
        plt.ylabel('Tipo de Serviço', fontsize=12)
        plt.tight_layout()
        
        if salvar_fig:
            plt.savefig('total_servicos.png')
        else:
            plt.show()
        
        plt.close()
        
        # Criando gráfico de pizza para distribuição percentual
        plt.figure(figsize=(12, 12))
        plt.pie(somas_metricas.values, labels=nomes_formatados, autopct='%1.1f%%', 
                shadow=True, startangle=90)
        plt.axis('equal')
        plt.title('Distribuição Percentual dos Serviços', fontsize=16)
        plt.tight_layout()
        
        if salvar_fig:
            plt.savefig('distribuicao_servicos.png')
        else:
            plt.show()
        
        plt.close()
        
        print("Visualizações das métricas quantitativas geradas com sucesso.")
    
    def gerar_relatorio_html(self, df=None, caminho_saida='relatorio_registrese.html'):
        """
        Gera um relatório HTML com os resultados da análise
        """
        if df is None:
            df = self.df
            
        if df is None:
            print("Nenhum dado disponível para gerar relatório.")
            return
        
        # Processando os dados
        df_limpo = self.limpar_dados() if df is self.df else df
        
        # Obtendo estatísticas
        colunas_metricas = [col for col in df_limpo.columns if col.startswith('qtd_')]
        estatisticas = df_limpo[colunas_metricas].describe() if colunas_metricas else None
        
        # Contagem de participação
        if 'status_participacao' in df_limpo.columns:
            participacao = df_limpo['status_participacao'].value_counts()
        elif 'participou' in df_limpo.columns:
            participacao = df_limpo['participou'].value_counts()
        else:
            participacao = None
        
        # Criando o HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório da Semana Registre-se</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .destaque {{ font-weight: bold; color: #e74c3c; }}
                .container {{ margin: 20px 0; padding: 15px; border: 1px solid #eee; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Relatório de Análise da Semana "Registre-se"</h1>
            
            <div class="container">
                <h2>1. Resumo dos Dados</h2>
                <p>Total de registros analisados: <span class="destaque">{len(df_limpo)}</span></p>
        """
        
        # Adicionando participação
        if participacao is not None:
            html += """
                <h2>2. Análise de Participação</h2>
                <table>
                    <tr>
                        <th>Resposta</th>
                        <th>Quantidade</th>
                        <th>Percentual</th>
                    </tr>
            """
            
            total = participacao.sum()
            for categoria, contagem in participacao.items():
                percentual = (contagem / total * 100)
                html += f"""
                    <tr>
                        <td>{categoria}</td>
                        <td>{contagem}</td>
                        <td>{percentual:.2f}%</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Adicionando métricas
        if estatisticas is not None:
            html += """
                <h2>3. Indicadores Quantitativos</h2>
                <table>
                    <tr>
                        <th>Indicador</th>
                        <th>Total</th>
                        <th>Média</th>
                        <th>Máximo</th>
                    </tr>
            """
            
            for coluna in estatisticas.columns:
                nome_formatado = coluna.replace('qtd_', '').replace('_', ' ').title()
                total = df_limpo[coluna].sum()
                media = estatisticas[coluna]['mean']
                maximo = estatisticas[coluna]['max']
                
                html += f"""
                    <tr>
                        <td>{nome_formatado}</td>
                        <td>{total}</td>
                        <td>{media:.2f}</td>
                        <td>{maximo}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Adicionando classificação semântica
        classes_semanticas = self.obter_classificacao_semantica()
        
        html += """
            <h2>4. Classificação Semântica</h2>
            <p>A tabela abaixo apresenta a estrutura semântica aplicada aos dados:</p>
        """
        
        for classe, atributos in classes_semanticas.items():
            html += f"""
                <h3>4.{list(classes_semanticas.keys()).index(classe) + 1}. Classe: {classe}</h3>
                <table>
                    <tr>
                        <th>Coluna Original</th>
                        <th>Atributo</th>
                        <th>Tipo</th>
                    </tr>
            """
            
            for item in atributos:
                html += f"""
                    <tr>
                        <td>{item['coluna_original']}</td>
                        <td>{item['atributo']}</td>
                        <td>{item['tipo']}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Finalizando o HTML
        html += """
            <div class="container">
                <h2>5. Conclusões</h2>
                <p>Este relatório apresenta a estrutura semântica e análise básica dos dados coletados durante a Semana "Registre-se".</p>
                <p>A decoupagem lógica dos dados facilita a compreensão e análise das informações coletadas, organizando-as em classes semânticas para melhor interpretação.</p>
            </div>
            
            <footer>
                <p>Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </footer>
        </body>
        </html>
        """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        
        # Salvando o relatório
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Relatório salvo em {caminho_saida}")

# Função principal para executar o processamento
def processar_dados_registrese(caminho_arquivo):
    """
    Executa o processamento completo dos dados da Semana Registre-se
    """
    print("Iniciando processamento dos dados da Semana Registre-se...")
    
    # Inicializando o processador
    processador = MetadadoRegistreSe(caminho_arquivo)
    
    # Limpando dados
    df_limpo = processador.limpar_dados()
    
    # Realizando análise
    processador.analisar_dados(df_limpo)
    
    # Gerando visualizações
    processador.visualizar_metricas(df_limpo)
    
    # Gerando relatório
    processador.gerar_relatorio_html(df_limpo)
    
    print("Processamento concluído com sucesso!")
    
    return processador, df_limpo

# Executar se for o script principal
if __name__ == "__main__":
    import sys
    
    # Verificando argumentos
    if len(sys.argv) > 1:
        caminho_arquivo = sys.argv[1]
    else:
        caminho_arquivo = "DATA SET DADOS REGISTRESE JAQUELINE 4.xlsx"
    
    # Processando os dados
    processador, df_limpo = processar_dados_registrese(caminho_arquivo)
