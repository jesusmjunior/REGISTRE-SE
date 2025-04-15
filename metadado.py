# Consultas Semânticas e Extração de Insights dos Dados da Semana "Registre-se"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import re
from collections import Counter

# Importando funções dos scripts anteriores
from decoupagem_logica import importar_dados, limpar_dados, classificacao_semantica

class ConsultorSemantico:
    """
    Classe para realizar consultas semânticas nos dados da Semana Registre-se
    usando a estrutura semântica definida
    """
    
    def __init__(self, df, estrutura_semantica, classes_semanticas, metadados_colunas):
        """
        Inicializa o objeto de consultas semânticas
        
        Args:
            df: DataFrame com os dados
            estrutura_semantica: Estrutura semântica das colunas
            classes_semanticas: Agrupamento das colunas por classes semânticas
            metadados_colunas: Metadados de cada coluna
        """
        self.df = df
        self.estrutura_semantica = estrutura_semantica
        self.classes_semanticas = classes_semanticas
        self.metadados_colunas = metadados_colunas
    
    def listar_colunas_por_classe(self, classe):
        """
        Lista todas as colunas pertencentes a uma determinada classe semântica
        
        Args:
            classe: Nome da classe semântica
        
        Returns:
            Lista de colunas da classe
        """
        if classe not in self.classes_semanticas:
            print(f"Classe '{classe}' não encontrada. Classes disponíveis: {list(self.classes_semanticas.keys())}")
            return []
        
        return [item['coluna_renomeada'] for item in self.classes_semanticas[classe]]
    
    def listar_colunas_por_tipo(self, tipo):
        """
        Lista todas as colunas de um determinado tipo de dado
        
        Args:
            tipo: Tipo de dado (string, inteiro, datetime, etc.)
        
        Returns:
            Lista de colunas do tipo especificado
        """
        colunas = []
        for coluna, metadados in self.metadados_colunas.items():
            if metadados['tipo'].lower() == tipo.lower():
                colunas.append(coluna)
        
        return colunas
    
    def obter_metadados_coluna(self, coluna):
        """
        Retorna os metadados de uma coluna específica
        
        Args:
            coluna: Nome da coluna (renomeada)
        
        Returns:
            Dicionário com os metadados da coluna
        """
        if coluna not in self.metadados_colunas:
            print(f"Coluna '{coluna}' não encontrada no mapeamento de metadados.")
            return None
        
        return self.metadados_colunas[coluna]
    
    def consultar_indicadores_quantitativos(self):
        """
        Realiza uma consulta agregada sobre os indicadores quantitativos
        
        Returns:
            DataFrame com estatísticas dos indicadores quantitativos
        """
        colunas_indicadores = self.listar_colunas_por_classe('Indicadores Quantitativos')
        
        if not colunas_indicadores:
            print("Nenhuma coluna de indicadores quantitativos encontrada.")
            return None
        
        # Estatísticas descritivas
        estatisticas = self.df[colunas_indicadores].describe()
        
        # Somando totais
        totais = self.df[colunas_indicadores].sum().to_frame('Total')
        
        # Contando participantes que reportaram valores > 0
        participantes = {}
        for col in colunas_indicadores:
            participantes[col] = (self.df[col] > 0).sum()
        
        df_participantes = pd.DataFrame(participantes.items(), 
                                       columns=['Indicador', 'Serventias com Valores > 0'])
        df_participantes.set_index('Indicador', inplace=True)
        
        # Calculando média por participante ativo
        media_por_ativo = {}
        for col in colunas_indicadores:
            ativos = self.df[self.df[col] > 0]
            media_por_ativo[col] = ativos[col].mean() if len(ativos) > 0 else 0
        
        df_media_ativos = pd.DataFrame(media_por_ativo.items(),
                                      columns=['Indicador', 'Média por Serventia Ativa'])
        df_media_ativos.set_index('Indicador', inplace=True)
        
        # Formatando nomes para exibição
        nomes_formatados = {}
        for col in colunas_indicadores:
            meta = self.metadados_colunas.get(col, {})
            atributo = meta.get('atributo', col)
            nomes_formatados[col] = atributo
        
        return {
            'estatisticas': estatisticas,
            'totais': totais,
            'participantes': df_participantes,
            'media_por_ativo': df_media_ativos,
            'nomes_formatados': nomes_formatados
        }
    
    def analisar_participacao(self):
        """
        Analisa dados de participação na Semana Registre-se
        
        Returns:
            Dicionário com análises de participação
        """
        # Identificando coluna de participação
        coluna_participacao = None
        for coluna, metadados in self.metadados_colunas.items():
            if metadados['classe'] == 'Participação' and 'sim' in metadados['atributo'].lower():
                coluna_participacao = coluna
                break
        
        if coluna_participacao is None or coluna_participacao not in self.df.columns:
            print("Coluna de participação não encontrada.")
            return None
        
        # Contando respostas SIM/NÃO
        contagem = self.df[coluna_participacao].value_counts()
        
        # Calculando percentuais
        percentual = contagem / contagem.sum() * 100
        
        # Analisando motivos de não participação
        coluna_motivo = None
        for coluna, metadados in self.metadados_colunas.items():
            if metadados['classe'] == 'Justificativa':
                coluna_motivo = coluna
                break
        
        motivos = None
        if coluna_motivo and coluna_motivo in self.df.columns:
            # Filtrando apenas quem não participou
            nao_participantes = self.df[self.df[coluna_participacao].str.upper() != 'SIM']
            motivos = nao_participantes[coluna_motivo].value_counts()
        
        return {
            'contagem': contagem,
            'percentual': percentual,
            'motivos': motivos
        }
    
    def analisar_publicos_atendidos(self):
        """
        Analisa os públicos atendidos durante a Semana Registre-se
        
        Returns:
            Dicionário com análises dos públicos atendidos
        """
        # Identificando coluna de públicos atendidos
        coluna_publicos = None
        for coluna, metadados in self.metadados_colunas.items():
            if metadados['classe'] == 'Público-Alvo':
                coluna_publicos = coluna
                break
        
        if coluna_publicos is None or coluna_publicos not in self.df.columns:
            print("Coluna de públicos atendidos não encontrada.")
            return None
        
        # Processando cada entrada de públicos
        publicos_contagem = {}
        
        # Processando cada entrada de públicos
        for publicos in self.df[coluna_publicos].dropna():
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
        
        return {
            'contagem_detalhada': df_publicos,
            'top_publicos': df_publicos.head(10)
        }
    
    def analisar_acoes_realizadas(self):
        """
        Analisa as ações realizadas durante a Semana Registre-se
        
        Returns:
            Dicionário com análises das ações realizadas
        """
        # Identificando coluna de ações realizadas
        coluna_acoes = None
        for coluna, metadados in self.metadados_colunas.items():
            if metadados['classe'] == 'Ações':
                coluna_acoes = coluna
                break
        
        if coluna_acoes is None or coluna_acoes not in self.df.columns:
            print("Coluna de ações realizadas não encontrada.")
            return None
        
        # Extraindo palavras-chave das ações realizadas
        palavras_chave = []
        
        # Lista de stop words para remover
        stop_words = ['de', 'a', 'o', 'e', 'do', 'da', 'dos', 'das', 'para', 'com', 'em', 'no', 'na', 'por']
        
        # Processando cada entrada de ações
        for acoes in self.df[coluna_acoes].dropna():
            # Convertendo para string e transformando para minúsculas
            texto = str(acoes).lower()
            
            # Removendo caracteres especiais e dividindo em palavras
            palavras = re.findall(r'\b[a-záéíóúàâêôãõç]+\b', texto)
            
            # Filtrando palavras com mais de 3 letras e removendo stop words
            palavras = [p for p in palavras if len(p) > 3 and p not in stop_words]
            
            palavras_chave.extend(palavras)
        
        # Contando frequência das palavras-chave
        contador = Counter(palavras_chave)
        
        # Convertendo para DataFrame
        df_palavras = pd.DataFrame({
            'Palavra': list(contador.keys()),
            'Frequência': list(contador.values())
        }).sort_values(by='Frequência', ascending=False)
        
        # Analisando menções a dias da semana
        dias_semana = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
        mencoes_dias = {dia: 0 for dia in dias_semana}
        
        for acoes in self.df[coluna_acoes].dropna():
            texto = str(acoes).lower()
            for dia in dias_semana:
                if dia in texto:
                    mencoes_dias[dia] += 1
        
        df_dias = pd.DataFrame({
            'Dia da Semana': list(mencoes_dias.keys()),
            'Menções': list(mencoes_dias.values())
        }).sort_values(by='Menções', ascending=False)
        
        return {
            'palavras_frequentes': df_palavras.head(20),
            'mencoes_dias': df_dias
        }
    
    def correlacionar_indicadores(self):
        """
        Analisa correlações entre os indicadores quantitativos
        
        Returns:
            DataFrame com correlações entre indicadores
        """
        # Obtendo colunas de indicadores quantitativos
        colunas_indicadores = self.listar_colunas_por_classe('Indicadores Quantitativos')
        
        if not colunas_indicadores:
            print("Nenhuma coluna de indicadores quantitativos encontrada.")
            return None
        
        # Calculando correlações
        correlacoes = self.df[colunas_indicadores].corr()
        
        return correlacoes
    
    def visualizar_correlacoes(self):
        """
        Gera visualização de correlações entre indicadores quantitativos
        """
        correlacoes = self.correlacionar_indicadores()
        
        if correlacoes is None:
            return
        
        # Obtendo metadados para nomes formatados
        nomes_formatados = {}
        for col in correlacoes.columns:
            meta = self.metadados_colunas.get(col, {})
            atributo = meta.get('atributo', col)
            nomes_formatados[col] = atributo
        
        # Renomeando colunas e índices para exibição
        correlacoes_fmt = correlacoes.rename(columns=nomes_formatados, index=nomes_formatados)
        
        # Criando heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlacoes_fmt, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0)
        plt.title('Correlações entre Indicadores Quantitativos', fontsize=16)
        plt.tight_layout()
        plt.savefig('correlacoes_indicadores.png')
        plt.close()
        
        print("Visualização de correlações gerada com sucesso.")
        
        return correlacoes_fmt
    
    def analisar_tendencias_pca(self):
        """
        Realiza análise de componentes principais (PCA) para identificar tendências
        nos indicadores quantitativos
        
        Returns:
            Dicionário com resultados da análise PCA
        """
        # Obtendo colunas de indicadores quantitativos
        colunas_indicadores = self.listar_colunas_por_classe('Indicadores Quantitativos')
        
        if not colunas_indicadores or len(colunas_indicadores) < 3:
            print("Número insuficiente de indicadores quantitativos para análise PCA.")
            return None
        
        # Preparando dados para PCA
        X = self.df[colunas_indicadores].fillna(0)
        
        # Normalizando os dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicando PCA
        pca = PCA(n_components=2)  # Reduzindo para 2 componentes para visualização
        X_pca = pca.fit_transform(X_scaled)
        
        # Criando DataFrame com resultados do PCA
        df_pca = pd.DataFrame(X_pca, columns=['PC1', 'PC2'])
        
        # Calculando variância explicada
        var_explicada = pca.explained_variance_ratio_
        
        # Obtendo contribuição de cada variável
        contribuicoes = pd.DataFrame(
            pca.components_.T,
            columns=['PC1', 'PC2'],
            index=colunas_indicadores
        )
        
        # Visualizando resultados do PCA
        plt.figure(figsize=(12, 10))
        
        # Plotando pontos (amostras)
        plt.scatter(df_pca['PC1'], df_pca['PC2'], alpha=0.7)
        
        # Plotando vetores de contribuição das variáveis
        for i, (var, pc1, pc2) in enumerate(zip(contribuicoes.index, 
                                                contribuicoes['PC1'], 
                                                contribuicoes['PC2'])):
            plt.arrow(0, 0, pc1*5, pc2*5, head_width=0.1, head_length=0.1, 
                      fc='red', ec='red', alpha=0.7)
            
            # Formatando nome para exibição
            meta = self.metadados_colunas.get(var, {})
            nome_exibicao = meta.get('atributo', var)
            
            plt.text(pc1*5.2, pc2*5.2, nome_exibicao, color='red', ha='center', va='center')
        
        plt.grid(True)
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        plt.xlabel(f'PC1 ({var_explicada[0]:.2%} da variância)', fontsize=12)
        plt.ylabel(f'PC2 ({var_explicada[1]:.2%} da variância)', fontsize=12)
        plt.title('Análise de Componentes Principais (PCA) dos Indicadores', fontsize=16)
        plt.tight_layout()
        plt.savefig('pca_indicadores.png')
        plt.close()
        
        return {
            'pca_scores': df_pca,
            'variancia_explicada': var_explicada,
            'contribuicoes': contribuicoes
        }
    
    def gerar_relatorio_completo(self, caminho_saida='relatorio_semana_registrese.html'):
        """
        Gera um relatório completo com todas as análises realizadas
        
        Args:
            caminho_saida: Caminho para salvar o relatório HTML
        """
        # Obtendo resultados de todas as análises
        indicadores = self.consultar_indicadores_quantitativos()
        participacao = self.analisar_participacao()
        publicos = self.analisar_publicos_atendidos()
        acoes = self.analisar_acoes_realizadas()
        correlacoes = self.correlacionar_indicadores()
        
        # Criando relatório HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório da Semana Registre-se</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; margin: 15px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .destaque { font-weight: bold; color: #e74c3c; }
                .container { margin: 20px 0; padding: 15px; border: 1px solid #eee; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Relatório de Análise da Semana "Registre-se"</h1>
            
            <div class="container">
                <h2>1. Resumo Executivo</h2>
                <p>Este relatório apresenta a análise completa dos dados coletados durante a Semana "Registre-se" em maio de 2024, 
                com base na classificação semântica e decoupagem lógica dos dados.</p>
        """
        
        # Seção de Participação
        if participacao:
            html += """
                <h2>2. Análise de Participação</h2>
                <table>
                    <tr>
                        <th>Resposta</th>
                        <th>Quantidade</th>
                        <th>Percentual</th>
                    </tr>
            """
            
            for resposta, quantidade in participacao['contagem'].items():
                percentual = participacao['percentual'][resposta]
                html += f"""
                    <tr>
                        <td>{resposta}</td>
                        <td>{quantidade}</td>
                        <td>{percentual:.2f}%</td>
                    </tr>
                """
            
            html += """
                </table>
            """
            
            # Motivos de não participação
            if participacao['motivos'] is not None and not participacao['motivos'].empty:
                html += """
                    <h3>2.1 Motivos para Não Participação</h3>
                    <table>
                        <tr>
                            <th>Motivo</th>
                            <th>Quantidade</th>
                        </tr>
                """
                
                for motivo, quantidade in participacao['motivos'].items():
                    html += f"""
                        <tr>
                            <td>{motivo}</td>
                            <td>{quantidade}</td>
                        </tr>
                    """
                
                html += """
                    </table>
                """
        
        # Seção de Indicadores Quantitativos
        if indicadores:
            html += """
                <h2>3. Indicadores Quantitativos</h2>
                <h3>3.1 Totais por Serviço</h3>
                <table>
                    <tr>
                        <th>Serviço</th>
                        <th>Total</th>
                    </tr>
            """
            
            for indice, valor in indicadores['totais'].iterrows():
                nome_formatado = indicadores['nomes_formatados'].get(indice, indice)
                html += f"""
                    <tr>
                        <td>{nome_formatado}</td>
                        <td>{int(valor['Total'])}</td>
                    </tr>
                """
            
            html += """
                </table>
                
                <h3>3.2 Estatísticas por Serviço</h3>
                <table>
                    <tr>
                        <th>Serviço</th>
                        <th>Média</th>
                        <th>Mediana</th>
                        <th>Máximo</th>
                        <th>Serventias Ativas</th>
                        <th>Média por Ativa</th>
                    </tr>
            """
            
            for coluna in indicadores['estatisticas'].columns:
                nome_formatado = indicadores['nomes_formatados'].get(coluna, coluna)
                media = indicadores['estatisticas'][coluna]['mean']
                mediana = indicadores['estatisticas'][coluna]['50%']
                maximo = indicadores['estatisticas'][coluna]['max']
                
                serventias_ativas = indicadores['participantes'].loc[coluna, 'Serventias com Valores > 0'] \
                    if coluna in indicadores['participantes'].index else 0
                
                media_ativa = indicadores['media_por_ativo'].loc[coluna, 'Média por Serventia Ativa'] \
                    if coluna in indicadores['media_por_ativo'].index else 0
                
                html += f"""
                    <tr>
                        <td>{nome_formatado}</td>
                        <td>{media:.2f}</td>
                        <td>{mediana:.2f}</td>
                        <td>{maximo:.0f}</td>
                        <td>{serventias_ativas}</td>
                        <td>{media_ativa:.2f}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Seção de Públicos Atendidos
        if publicos and 'top_publicos' in publicos and not publicos['top_publicos'].empty:
            html += """
                <h2>4. Análise de Públicos Atendidos</h2>
                <h3>4.1 Top 10 Públicos Mais Atendidos</h3>
                <table>
                    <tr>
                        <th>Público</th>
                        <th>Número de Menções</th>
                    </tr>
            """
            
            for _, row in publicos['top_publicos'].iterrows():
                html += f"""
                    <tr>
                        <td>{row['Público']}</td>
                        <td>{row['Contagem']}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
        
        # Seção de Ações Realizadas
        if acoes and 'palavras_frequentes' in acoes and not acoes['palavras_frequentes'].empty:
            html += """
                <h2>5. Análise de Ações Realizadas</h2>
                <h3>5.1 Palavras-chave Mais Frequentes</h3>
                <table>
                    <tr>
                        <th>Palavra</th>
                        <th>Frequência</th>
                    </tr>
            """
            
            for _, row in acoes['palavras_frequentes'].head(15).iterrows():
                html += f"""
                    <tr>
                        <td>{row['Palavra']}</td>
                        <td>{row['Frequência']}</td>
                    </tr>
                """
            
            html += """
                </table>
            """
            
            # Menções a dias da semana
            if 'mencoes_dias' in acoes and not acoes['mencoes_dias'].empty:
                html += """
                    <h3>5.2 Menções a Dias da Semana</h3>
                    <table>
                        <tr>
                            <th>Dia da Semana</th>
                            <th>Número de Menções</th>
                        </tr>
                """
                
                for _, row in acoes['mencoes_dias'].iterrows():
                    html += f"""
                        <tr>
                            <td>{row['Dia da Semana'].title()}</td>
                            <td>{row['Menções']}</td>
                        </tr>
                    """
                
                html += """
                    </table>
                """
        
        # Conclusão
        html += """
            <h2>6. Conclusões e Recomendações</h2>
            <div class="container">
                <p>A análise dos dados da Semana "Registre-se" permite identificar as principais tendências 
                e padrões na participação das serventias extrajudiciais, destacando os serviços mais oferecidos
                e os públicos mais atendidos.</p>
                
                <p>Recomendações para próximas edições:</p>
                <ul>
                    <li>Foco nos serviços com maior demanda identificados nesta análise</li>
                    <li>Ações específicas para os públicos prioritários</li>
                    <li>Estratégias para aumentar a participação das serventias</li>
                    <li>Aprimoramento do formulário de coleta de dados para análises futuras</li>
                </ul>
            </div>
            
            <footer>
                <p>Relatório gerado automaticamente através de classificação semântica e análise de dados.</p>
            </footer>
        </body>
        </html>
        """
        
        # Salvando o relatório
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Relatório completo gerado com sucesso e salvo em '{caminho_saida}'")


# Função para demonstrar o uso da classe de consulta semântica
def demonstrar_consultor(caminho_arquivo):
    """
    Demonstra o uso da classe ConsultorSemantico
    """
    from decoupagem_logica import importar_dados, limpar_dados, classificacao_semantica
    
    print("Iniciando demonstração do Consultor Semântico...")
    
    # Carregando e preparando os dados
    df_original = importar_dados(caminho_arquivo)
    df_limpo = limpar_dados(df_original)
    estrutura_semantica, classes_semanticas, estrutura_simplificada, metadados_colunas = classificacao_semantica(df_limpo)
    
    # Criando o consultor semântico
    consultor = ConsultorSemantico(df_limpo, estrutura_semantica, classes_semanticas, metadados_colunas)
    
    # Demonstrando consultas básicas
    print("\n1. Listando colunas por classe semântica:")
    print("Colunas de Indicadores Quantitativos:", consultor.listar_colunas_por_classe('Indicadores Quantitativos'))
    print("Colunas de Contato:", consultor.listar_colunas_por_classe('Contato'))
    
    # Demonstrando consulta de indicadores quantitativos
    print("\n2. Consultando indicadores quantitativos:")
    indicadores = consultor.consultar_indicadores_quantitativos()
    if indicadores:
        print("Total de serviços realizados:")
        print(indicadores['totais'])
    
    # Demonstrando análise de participação
    print("\n3. Analisando participação:")
    participacao = consultor.analisar_participacao()
    if participacao:
        print("Contagem de participação:")
        print(participacao['contagem'])
    
    # Demonstrando correlações
    print("\n4. Analisando correlações entre indicadores:")
    correlacoes = consultor.correlacionar_indicadores()
    if correlacoes is not None:
        print("Matriz de correlação (primeiras 3 linhas e colunas):")
        print(correlacoes.iloc[:3, :3])
    
    # Gerando visualizações
    print("\n5. Gerando visualizações:")
    consultor.visualizar_correlacoes()
    
    # Gerando relatório completo
    print("\n6. Gerando relatório completo:")
    consultor.gerar_relatorio_completo()
    
    return consultor

# Para executar a demonstração, use:
# consultor = demonstrar_consultor("DATA SET DADOS REGISTRESE JAQUELINE 4.xlsx")
