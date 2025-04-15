#!/usr/bin/env python
# coding: utf-8

"""
Interface Gráfica para Processamento de Dados da Semana Registre-se

Esta aplicação fornece uma interface gráfica simples para processamento
dos dados da Semana Registre-se, permitindo convertê-los para formatos
limpos e normalizados.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import pandas as pd
import numpy as np
import re
import unicodedata
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ProcessadorRegistrese:
    """Classe para processamento dos dados da Semana Registre-se"""
    
    def __init__(self):
        """Inicializa o processador"""
        # Padrões para normalização de colunas
        self.padrao_colunas = {
            'carimbo': 'data_hora',
            'endereço': 'email_principal',
            'identificação': 'serventia',
            'e-mail': 'email_contato',
            'whatsapp': 'whatsapp',
            'foram realizadas': 'participou',
            'motivo da não': 'motivo_nao_participacao',
            'quais as ações': 'acoes_realizadas',
            'marque as opções': 'publicos_atendidos',
            'quantas 2ªs vias': 'qtd_segundas_vias',
            'quantos registros de nascimento': 'qtd_registros_nascimento',
            'quantas averbações': 'qtd_averbacoes_paternidade',
            'quantas retificações': 'qtd_retificacoes',
            'quantos registros tardios': 'qtd_registros_tardios',
            'quantas restaurações': 'qtd_restauracoes',
            'classificação': 'classificacao',
            'tags': 'tags'
        }
    
    def normalizar_texto(self, texto):
        """Normaliza texto removendo acentos e caracteres especiais"""
        if pd.isna(texto) or not isinstance(texto, str):
            return texto
        
        # Normalização usando unicodedata
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    
    def limpar_valor_numerico(self, valor):
        """Extrai valores numéricos de strings"""
        if pd.isna(valor):
            return 0
        
        # Se já é um número, retorna o valor
        if isinstance(valor, (int, float)) and not np.isnan(valor):
            return int(valor)
        
        # Converte para string e trata
        valor_str = str(valor).strip().upper()
        
        # Casos especiais
        casos_zero = [
            '', 'NAO HOUVE', 'NAO', 'NÃO', 'NAO TEVE', 'NENHUM', 'NENHUMA', 
            'SEM PROCURA', 'NENHUMA', '-', 'NEM UM', 'ZERO', '0', 'NÃO HOUVE DEMANDA',
            'HOJE NÃO TEVE', 'HOJE NAO TEVE', 'NÃO HOUVE', 'NÃO TEVE'
        ]
        
        if any(caso in valor_str for caso in casos_zero):
            return 0
        
        # Tenta extrair números da string
        numeros = re.findall(r'\d+', valor_str)
        if numeros:
            return int(numeros[0])
        
        return 0
    
    def limpar_participacao(self, valor):
        """Padroniza valores de participação"""
        if pd.isna(valor):
            return "Não Informado"
        
        valor_str = str(valor).strip().upper()
        
        if valor_str in ['SIM', 'S', 'PARTICIPOU', 'DADOS PARCIAIS', 'DADOS REFERENTES']:
            return "Sim"
        elif 'NÃO' in valor_str or 'NAO' in valor_str:
            return "Não"
        else:
            return valor_str if valor_str else "Não Informado"
    
    def limpar_nomes_colunas(self, colunas):
        """Limpa e normaliza os nomes das colunas"""
        colunas_normalizadas = []
        
        for coluna in colunas:
            coluna_str = str(coluna).lower()
            coluna_normalizada = self.normalizar_texto(coluna_str)
            
            # Tentando encontrar correspondência no padrão de nomes
            for padrao, nome_padronizado in self.padrao_colunas.items():
                if padrao in coluna_normalizada:
                    colunas_normalizadas.append(nome_padronizado)
                    break
            else:
                # Se não encontrar correspondência, mantém o original
                colunas_normalizadas.append(coluna)
        
        return colunas_normalizadas
    
    def processar_arquivo(self, caminho_arquivo, diretorio_saida=None, callback=None):
        """
        Processa o arquivo da Semana Registre-se
        
        Args:
            caminho_arquivo: Caminho para o arquivo Excel
            diretorio_saida: Diretório para salvar os arquivos processados
            callback: Função de callback para atualizar progresso
        """
        if callback:
            callback("Iniciando processamento do arquivo...")
        
        try:
            # Lendo o arquivo
            df = pd.read_excel(caminho_arquivo)
            
            if callback:
                callback(f"Arquivo carregado! Total de registros: {len(df)}")
            
            # Normalizando nomes das colunas
            if callback:
                callback("Normalizando nomes das colunas...")
            
            novas_colunas = self.limpar_nomes_colunas(df.columns)
            df.columns = novas_colunas
            
            # Removendo linhas completamente vazias
            df = df.dropna(how='all')
            
            # Processando colunas de indicadores quantitativos
            if callback:
                callback("Processando indicadores quantitativos...")
            
            colunas_numericas = [col for col in df.columns if col.startswith('qtd_')]
            
            for col in colunas_numericas:
                df[col] = df[col].apply(self.limpar_valor_numerico)
            
            # Processando coluna de participação
            if callback:
                callback("Processando informações de participação...")
                
            if 'participou' in df.columns:
                df['participou'] = df['participou'].apply(self.limpar_participacao)
                
                # Criando coluna de status de participação
                df['status_participacao'] = df['participou'].apply(
                    lambda x: 'Participou' if x == 'Sim' else 'Não Participou'
                )
            
            # Processando públicos atendidos
            if 'publicos_atendidos' in df.columns:
                df['publicos_atendidos'] = df['publicos_atendidos'].fillna('Não Informado')
            
            # Colunas categóricas para padronização
            if 'classificacao' in df.columns:
                df['classificacao'] = df['classificacao'].fillna('Não Classificado')
            
            if 'tags' in df.columns:
                df['tags'] = df['tags'].fillna('Não Categorizado')
            
            # Definindo diretório de saída
            if diretorio_saida is None:
                diretorio_saida = os.path.dirname(caminho_arquivo) or '.'
            
            # Criando diretório se não existir
            os.makedirs(diretorio_saida, exist_ok=True)
            
            # Obtendo nome base do arquivo
            nome_base = os.path.splitext(os.path.basename(caminho_arquivo))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Salvando em diferentes formatos
            if callback:
                callback("Salvando arquivos processados...")
            
            # Salvando em CSV
            caminho_csv = os.path.join(diretorio_saida, f"{nome_base}_processado_{timestamp}.csv")
            df.to_csv(caminho_csv, index=False, encoding='utf-8')
            
            # Salvando em Excel limpo
            caminho_excel = os.path.join(diretorio_saida, f"{nome_base}_processado_{timestamp}.xlsx")
            df.to_excel(caminho_excel, index=False)
            
            # Salvando em formato TXT tabulado
            caminho_txt = os.path.join(diretorio_saida, f"{nome_base}_processado_{timestamp}.txt")
            df.to_csv(caminho_txt, sep='\t', index=False, encoding='utf-8')
            
            # Estatísticas após processamento
            estatisticas = {
                'total_registros': len(df),
                'total_participantes': len(df[df['status_participacao'] == 'Participou']) if 'status_participacao' in df.columns else 0,
                'total_nao_participantes': len(df[df['status_participacao'] == 'Não Participou']) if 'status_participacao' in df.columns else 0,
                'indicadores': {col: df[col].sum() for col in colunas_numericas}
            }
            
            if callback:
                callback("Processamento concluído com sucesso!")
            
            return {
                'dataframe': df,
                'arquivos': {
                    'csv': caminho_csv,
                    'excel': caminho_excel,
                    'txt': caminho_txt
                },
                'estatisticas': estatisticas
            }
        
        except Exception as e:
            if callback:
                callback(f"Erro ao processar o arquivo: {e}")
            return None


class InterfaceRegistrese:
    """Interface gráfica para o processador de dados"""
    
    def __init__(self, root):
        """Inicializa a interface gráfica"""
        self.root = root
        self.root.title("Processador de Dados - Semana Registre-se")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configuração do estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=('Arial', 11))
        self.style.configure("Header.TLabel", font=('Arial', 14, 'bold'))
        self.style.configure("Subheader.TLabel", font=('Arial', 12, 'bold'))
        
        # Instância do processador
        self.processador = ProcessadorRegistrese()
        
        # Variáveis de controle
        self.arquivo_selecionado = tk.StringVar()
        self.diretorio_saida = tk.StringVar()
        self.status = tk.StringVar()
        self.status.set("Selecione um arquivo para iniciar")
        
        # Criando os widgets
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Processador de Dados da Semana Registre-se", style="Header.TLabel").pack(pady=(0, 20))
        
        # Frame para seleção de arquivo
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Arquivo Excel:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.arquivo_selecionado, width=50).grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(file_frame, text="Selecionar", command=self.selecionar_arquivo).grid(row=0, column=2, padx=(10, 0))
        
        # Frame para seleção de diretório de saída
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(dir_frame, text="Diretório de Saída:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(dir_frame, textvariable=self.diretorio_saida, width=50).grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(dir_frame, text="Selecionar", command=self.selecionar_diretorio).grid(row=0, column=2, padx=(10, 0))
        
        # Configurando grid para expansão
        file_frame.columnconfigure(1, weight=1)
        dir_frame.columnconfigure(1, weight=1)
        
        # Botão de processar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Processar Arquivo", command=self.iniciar_processamento, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Ajuda", command=self.mostrar_ajuda, width=10).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Sair", command=self.root.quit, width=10).pack(side=tk.RIGHT)
        
        # Frame para log de status
        log_frame = ttk.Frame(main_frame, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(log_frame, text="Status de Processamento:", style="Subheader.TLabel").pack(anchor=tk.W)
        
        # Área de texto para log
        self.log_area = tk.Text(log_frame, height=12, width=80, wrap=tk.WORD, bg="#f8f8f8", fg="#333")
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar para o log
        scrollbar = ttk.Scrollbar(self.log_area, command=self.log_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_area.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_frame, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)
    
    def selecionar_arquivo(self):
        """Permite selecionar um arquivo Excel"""
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        
        if arquivo:
            self.arquivo_selecionado.set(arquivo)
            
            # Pré-definir o diretório de saída como o mesmo do arquivo
            diretorio = os.path.dirname(arquivo)
            self.diretorio_saida.set(diretorio)
            
            self.adicionar_log(f"Arquivo selecionado: {arquivo}")
            self.status.set("Arquivo selecionado. Clique em 'Processar Arquivo' para continuar.")
    
    def selecionar_diretorio(self):
        """Permite selecionar o diretório de saída"""
        diretorio = filedialog.askdirectory(title="Selecione o diretório de saída")
        
        if diretorio:
            self.diretorio_saida.set(diretorio)
            self.adicionar_log(f"Diretório de saída: {diretorio}")
    
    def adicionar_log(self, mensagem):
        """Adiciona uma mensagem à área de log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {mensagem}\n"
        
        self.log_area.insert(tk.END, log_msg)
        self.log_area.see(tk.END)  # Rola para o final
    
    def atualizar_status(self, mensagem):
        """Atualiza o status e adiciona ao log"""
        self.status.set(mensagem)
        self.adicionar_log(mensagem)
    
    def iniciar_processamento(self):
        """Inicia o processamento do arquivo em uma thread separada"""
        arquivo = self.arquivo_selecionado.get()
        diretorio = self.diretorio_saida.get()
        
        if not arquivo:
            messagebox.showerror("Erro", "Selecione um arquivo Excel primeiro!")
            return
        
        # Limpar a área de log
        self.log_area.delete(1.0, tk.END)
        
        self.adicionar_log("Iniciando processamento...")
        self.status.set("Processando arquivo...")
        
        # Iniciando o processamento em uma thread separada
        threading.Thread(target=self.processar_em_thread, args=(arquivo, diretorio)).start()
    
    def processar_em_thread(self, arquivo, diretorio):
        """Processa o arquivo em uma thread separada"""
        def callback(mensagem):
            """Callback para atualizar a interface durante o processamento"""
            # Usando after para executar no thread principal
            self.root.after(0, self.atualizar_status, mensagem)
        
        # Processar o arquivo
        resultado = self.processador.processar_arquivo(arquivo, diretorio, callback)
        
        # Verificando resultado
        if resultado:
            arquivos = resultado['arquivos']
            estatisticas = resultado['estatisticas']
            
            # Atualizando o log com informações de arquivos gerados
            self.root.after(0, self.adicionar_log, "\n=== ARQUIVOS GERADOS ===")
            for formato, caminho in arquivos.items():
                nome_arquivo = os.path.basename(caminho)
                self.root.after(0, self.adicionar_log, f"  - {formato.upper()}: {nome_arquivo}")
            
            # Atualizando o log com estatísticas
            self.root.after(0, self.adicionar_log, "\n=== ESTATÍSTICAS ===")
            self.root.after(0, self.adicionar_log, f"Total de registros: {estatisticas['total_registros']}")
            
            if 'total_participantes' in estatisticas:
                participacao = estatisticas['total_participantes']
                nao_participacao = estatisticas['total_nao_participantes']
                self.root.after(0, self.adicionar_log, f"Participantes: {participacao}")
                self.root.after(0, self.adicionar_log, f"Não participantes: {nao_participacao}")
            
            # Exibindo totais de indicadores
            if 'indicadores' in estatisticas:
                self.root.after(0, self.adicionar_log, "\nTotais por indicador:")
                for indicador, total in estatisticas['indicadores'].items():
                    nome_indicador = indicador.replace('qtd_', '').replace('_', ' ').title()
                    self.root.after(0, self.adicionar_log, f"  - {nome_indicador}: {total}")
            
            # Mensagem final
            self.root.after(0, self.status.set, "Processamento concluído com sucesso!")
            self.root.after(0, messagebox.showinfo, "Sucesso", "Arquivo processado com sucesso!")
        else:
            self.root.after(0, self.status.set, "Erro no processamento!")
            self.root.after(0, messagebox.showerror, "Erro", "Ocorreu um erro ao processar o arquivo!")
    
    def mostrar_ajuda(self):
        """Exibe uma janela de ajuda"""
        ajuda_texto = """
        PROCESSADOR DE DADOS DA SEMANA REGISTRE-SE
        
        Esta ferramenta processa e limpa os dados coletados durante a Semana "Registre-se", 
        gerando arquivos em formatos padronizados e normalizados para análise.
        
        Como usar:
        
        1. Clique em "Selecionar" para escolher o arquivo Excel com os dados originais.
        2. Opcionalmente, escolha um diretório de saída para os arquivos processados.
        3. Clique em "Processar Arquivo" para iniciar o processamento.
        4. Acompanhe o progresso na área de log.
        
        O processamento inclui:
        - Normalização dos nomes das colunas
        - Limpeza e padronização de dados numéricos
        - Padronização das informações de participação
        - Geração de estatísticas básicas
        
        A ferramenta gera arquivos nos seguintes formatos:
        - CSV (.csv) - Para importação em outras ferramentas
        - Excel (.xlsx) - Formatado e limpo
        - TXT tabulado (.txt) - Formato universal
        
        Todos os arquivos gerados incluem um timestamp no nome para evitar sobrescrever dados.
        """
        
        # Criando janela de ajuda
        ajuda_janela = tk.Toplevel(self.root)
        ajuda_janela.title("Ajuda - Processador de Dados")
        ajuda_janela.geometry("600x500")
        ajuda_janela.resizable(True, True)
        
        # Adicionando texto de ajuda
        texto = tk.Text(ajuda_janela, wrap=tk.WORD, padx=10, pady=10)
        texto.pack(fill=tk.BOTH, expand=True)
        texto.insert(tk.END, ajuda_texto)
        texto.config(state=tk.DISABLED)  # Somente leitura
        
        # Adicionando scrollbar
        scrollbar = ttk.Scrollbar(texto, command=texto.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        texto.config(yscrollcommand=scrollbar.set)
        
        # Botão de fechar
        ttk.Button(ajuda_janela, text="Fechar", command=ajuda_janela.destroy).pack(pady=10)


# Função principal
def main():
    """Função principal para executar a aplicação"""
    root = tk.Tk()
    app = InterfaceRegistrese(root)
    root.mainloop()


# Executar se for o script principal
if __name__ == "__main__":
    main()
