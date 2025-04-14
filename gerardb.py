import pandas as pd
import numpy as np
from datetime import datetime
import uuid

# Criar o modelo de banco de dados
def create_database_template():
    # Definir as colunas do banco de dados
    columns = [
        'ID_REGISTRO',
        'NOME_SERVENTIA',
        'UF',
        'CARIMBO_TEORA',
        'EMAIL_INSTITUCIONAL',
        'TELEFONE_WHATSAPP',
        'PARTICIPA_SEMANA',
        'MOTIVO_PARTICIPACAO',
        'CLASSE',
        'ATRIBUTO',
        'GRAU_PERTENCIMENTO',
        'GRAU_CONEXAO',
        'JUSTIFICATIVA_OBSERVACAO',
        'OUTROS',
        'DATA_HORA_REGISTRO'
    ]
    
    # Criar um DataFrame com as colunas
    df = pd.DataFrame(columns=columns)
    
    # Adicionar algumas linhas de exemplo
    example_data = [
        {
            'ID_REGISTRO': f"REG-{uuid.uuid4().hex[:8].upper()}",
            'NOME_SERVENTIA': "1º Ofício de Registro Civil de São Luís",
            'UF': "MA",
            'CARIMBO_TEORA': "https://drive.google.com/file/carimbo1",
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
            'DATA_HORA_REGISTRO': datetime.now()
        },
        {
            'ID_REGISTRO': f"REG-{uuid.uuid4().hex[:8].upper()}",
            'NOME_SERVENTIA': "2º Tabelionato de Notas de São Paulo",
            'UF': "SP",
            'CARIMBO_TEORA': "https://drive.google.com/file/carimbo2",
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
            'DATA_HORA_REGISTRO': datetime.now()
        }
    ]
    
    # Adicionar os exemplos ao DataFrame
    for example in example_data:
        df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
    
    # Salvar o DataFrame para Excel
    df.to_excel("Modelo_DB_Semana_Registre-se.xlsx", index=False)
    
    return df

# Executar a criação do modelo
if __name__ == "__main__":
    create_database_template()
    print("Modelo de banco de dados criado com sucesso!")
