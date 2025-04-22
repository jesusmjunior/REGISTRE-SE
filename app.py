import pandas as pd
import json
import uuid
from datetime import datetime
import os

class CogexRegistrationApp:
    def __init__(self):
        # Load initial data
        self.serventias = self.carregar_serventias()
        self.opcoes_publicos = self.preparar_opcoes_publicos()

    def carregar_json(self, caminho_arquivo):
        """Load JSON file with error handling"""
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar {caminho_arquivo}: {e}")
            return None

    def carregar_serventias(self):
        """Load list of serventias from JSON"""
        data = self.carregar_json("serventias_registre_se.json")
        return [s["nome"] for s in data["serventias"]] if data else []

    def preparar_opcoes_publicos(self):
        """Prepare list of public options"""
        data = self.carregar_json("publico_atendido.json")
        if not data:
            return []
        
        opcoes = []
        for grupo in data["publico_atendido"]["grupos"]:
            grupo_nome = grupo["nome"]
            for valor in grupo["valores"]:
                opcoes.append(f"{grupo_nome}: {valor}")
        return opcoes

    def gerar_protocolo(self):
        """Generate unique protocol"""
        return str(uuid.uuid4()).split('-')[0].upper()

    def salvar_dados(self, dados):
        """Save data to a log file"""
        try:
            # Create logs directory if it doesn't exist
            os.makedirs("logs", exist_ok=True)
            
            # Save as JSON log file
            arquivo_log = f"logs/registro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(arquivo_log, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False

    def gerar_html_confirmacao(self, dados):
        """Generate HTML confirmation page"""
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

    def coletar_input(self):
        """Collect user input from console"""
        print("📅 Formulário de Registro de Serventia")
        print("Semana Registre-se - Maio de 2024\n")

        # Serventia selection
        print("🏢 Identificação da Serventia")
        print("Serventias disponíveis:")
        for i, serventia in enumerate(self.serventias, 1):
            print(f"{i}. {serventia}")
        
        while True:
            try:
                selecao_serventia = int(input("Escolha o número da serventia: "))
                nome_serventia = self.serventias[selecao_serventia - 1]
                break
            except (ValueError, IndexError):
                print("Seleção inválida. Tente novamente.")

        # Contact information
        email = input("E-mail de contato: ")
        telefone = input("Whatsapp para contato: ")

        # Participation details
        participa_semana = input("Participação na Semana Registre-se (Sim/Não): ").lower()

        if participa_semana == 'não' or participa_semana == 'nao':
            motivo_nao_part = input("Motivo da não participação: ")
            acoes_realizadas = ""
        else:
            motivo_nao_part = ""
            acoes_realizadas = input("Descreva as ações realizadas: ")

        # Publics served
        print("\nPúblicos atendidos:")
        for i, publico in enumerate(self.opcoes_publicos, 1):
            print(f"{i}. {publico}")
        
        while True:
            selecao_publicos = input("Digite os números dos públicos atendidos (separados por vírgula): ")
            try:
                publicos_atendidos = [
                    self.opcoes_publicos[int(p.strip()) - 1] 
                    for p in selecao_publicos.split(',')
                ]
                break
            except (ValueError, IndexError):
                print("Seleção inválida. Tente novamente.")

        # Metrics
        print("\n📈 Métricas de Atendimento")
        vias_emitidas = int(input("2ª Vias emitidas: "))
        registros_nasc = int(input("Registros de Nascimento: "))
        averbacoes_pat = int(input("Averbações de Paternidade: "))
        retificacoes = int(input("Retificações de Registro: "))
        registros_tardios = int(input("Registros Tardios: "))
        restauracoes = int(input("Restaurações de Registro: "))

        # Classification and tags
        print("\nClassificações:")
        print("1. Infraestrutura\n2. Engajamento\n3. Participação")
        classificacao_num = int(input("Escolha o número da classificação: "))
        classificacoes = ["Infraestrutura", "Engajamento", "Participação"]
        classificacao = classificacoes[classificacao_num - 1]

        tags = input("Tags adicionais (separadas por vírgula): ")

        # Prepare data
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        protocolo = self.gerar_protocolo()
        
        dados = {
            "Protocolo": protocolo,
            "Carimbo de data/hora": data_hora,
            "Identificação da Serventia Extrajudicial": nome_serventia,
            "Endereço de e-mail": email,
            "Whatsapp": telefone,
            "Participação na Semana Registre-se": "Sim" if participa_semana == 'sim' else "Não",
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

        return dados

    def executar(self):
        """Main execution method"""
        try:
            # Collect input
            dados = self.coletar_input()

            # Save data
            if self.salvar_dados(dados):
                print(f"\n✅ Registro realizado com sucesso! Protocolo: {dados['Protocolo']}")
                
                # Generate HTML confirmation
                html_confirmacao = self.gerar_html_confirmacao(dados)
                
                # Save HTML file
                nome_arquivo = f"comprovante_registrese_{dados['Protocolo']}.html"
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    f.write(html_confirmacao)
                
                print(f"📄 Comprovante salvo como: {nome_arquivo}")
            else:
                print("Falha ao salvar o registro. Tente novamente.")

        except Exception as e:
            print(f"Erro durante o registro: {e}")

def main():
    app = CogexRegistrationApp()
    app.executar()

if __name__ == "__main__":
    main()
