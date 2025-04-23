# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras
import datetime
import random
import string
import json

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir requisições do frontend

# Configuração do banco de dados PostgreSQL
DB_CONFIG = {
    'dbname': os.environ.get("DB_NAME", "cogex_db"),
    'user': os.environ.get("DB_USER", "postgres"),
    'password': os.environ.get("DB_PASS", "sua-senha"),
    'host': os.environ.get("DB_HOST", "IP_PUBLICO_DA_INSTANCIA"),  # Para desenvolvimento
    # Para produção no Cloud Run:
    # 'host': os.environ.get("DB_HOST", "/cloudsql/SEU-PROJETO:REGIAO:cogex-postgres"),
    'port': os.environ.get("DB_PORT", "5432")
}

# Helper para conectar ao banco de dados
def get_db_connection():
    # Para desenvolvimento local
    if os.environ.get("ENVIRONMENT") == "development":
        return psycopg2.connect(
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
    
    # Para Cloud Run com conexão privada ao Cloud SQL
    return psycopg2.connect(
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host']
    )

# Endpoint para inicializar o banco de dados
@app.route("/api/init_db", methods=["GET"])
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Criar tabela se não existir
        cur.execute("""
        CREATE TABLE IF NOT EXISTS registro_semanal (
          id SERIAL PRIMARY KEY,
          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          protocolo TEXT,
          serventia TEXT NOT NULL,
          email TEXT,
          telefone TEXT,
          responsavel TEXT NOT NULL,
          participacao TEXT,
          data_inicio DATE,
          motivo_nao_participacao TEXT,
          acoes_realizadas TEXT,
          publicos_atendidos TEXT,
          vias_emitidas INTEGER DEFAULT 0,
          registros_nascimento INTEGER DEFAULT 0,
          averbacoes_paternidade INTEGER DEFAULT 0,
          retificacoes INTEGER DEFAULT 0,
          registros_tardios INTEGER DEFAULT 0,
          restauracoes INTEGER DEFAULT 0,
          classificacao TEXT,
          tags TEXT,
          observacoes TEXT
        );
        
        -- Criar índices para otimização
        CREATE INDEX IF NOT EXISTS idx_registro_serventia ON registro_semanal(serventia);
        CREATE INDEX IF NOT EXISTS idx_registro_timestamp ON registro_semanal(timestamp);
        CREATE INDEX IF NOT EXISTS idx_registro_participacao ON registro_semanal(participacao);
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Banco de dados inicializado com sucesso!"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Gerar protocolo único
def gerar_protocolo():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"REG-{timestamp}-{random_str}"

# Endpoint para registrar novos dados
@app.route("/api/registrar", methods=["POST"])
def registrar():
    try:
        # Obter os dados do JSON
        data = request.get_json()
        
        # Validação básica
        required_fields = ["Serventia", "Responsavel"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False, 
                    "error": f"Campo obrigatório ausente: {field}"
                }), 400
        
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Gerar protocolo
        protocolo = gerar_protocolo()
        
        # Preparar query de inserção
        query = """
        INSERT INTO registro_semanal (
            protocolo, serventia, email, telefone, responsavel, 
            participacao, data_inicio, motivo_nao_participacao, 
            acoes_realizadas, publicos_atendidos, vias_emitidas,
            registros_nascimento, averbacoes_paternidade, retificacoes,
            registros_tardios, restauracoes, classificacao, tags, observacoes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id;
        """
        
        # Converter data para formato correto
        data_inicio = None
        if "Data de Início" in data and data["Data de Início"]:
            try:
                data_inicio = datetime.datetime.strptime(data["Data de Início"], "%Y-%m-%d").date()
            except ValueError:
                data_inicio = None
        
        # Preparar valores para inserção
        valores = (
            protocolo,
            data.get("Serventia", ""),
            data.get("Email", ""),
            data.get("Telefone", ""),
            data.get("Responsavel", ""),
            data.get("Participação", "Sim"),
            data_inicio,
            data.get("Motivo Não Participação", ""),
            data.get("Ações Realizadas", ""),
            data.get("Públicos Atendidos", ""),
            int(data.get("Vias Emitidas", 0)),
            int(data.get("Registros Nascimento", 0)),
            int(data.get("Averbações Paternidade", 0)),
            int(data.get("Retificações", 0)),
            int(data.get("Registros Tardios", 0)),
            int(data.get("Restaurações", 0)),
            data.get("Classificação", ""),
            data.get("Tags", ""),
            data.get("Observações", "")
        )
        
        # Executar a inserção
        cur.execute(query, valores)
        id_inserted = cur.fetchone()[0]
        conn.commit()
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Registro criado com sucesso!",
            "data": {
                "id": id_inserted,
                "protocolo": protocolo
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Endpoint para consultar todos os registros
@app.route("/api/consultar", methods=["GET"])
def consultar():
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Filtros (opcional)
        filtro = request.args.get("filtro", "")
        query_base = "SELECT * FROM registro_semanal"
        params = []
        
        if filtro:
            query_base += """ WHERE 
                serventia ILIKE %s OR 
                responsavel ILIKE %s OR
                protocolo ILIKE %s"""
            termo_busca = f"%{filtro}%"
            params = [termo_busca, termo_busca, termo_busca]
        
        # Ordenação por timestamp decrescente (mais recentes primeiro)
        query_base += " ORDER BY timestamp DESC"
        
        # Executar a consulta
        cur.execute(query_base, params)
        registros = cur.fetchall()
        
        # Converter para lista de dicionários
        resultado = []
        for registro in registros:
            registro_dict = dict(registro)
            
            # Converter para formato compatível com o frontend
            resultado.append({
                "ID": registro_dict["id"],
                "Timestamp": registro_dict["timestamp"].isoformat() if registro_dict["timestamp"] else None,
                "Protocolo": registro_dict["protocolo"],
                "Serventia": registro_dict["serventia"],
                "Email": registro_dict["email"],
                "Telefone": registro_dict["telefone"],
                "Responsável": registro_dict["responsavel"],
                "Participação": registro_dict["participacao"],
                "Data de Início": registro_dict["data_inicio"].isoformat() if registro_dict["data_inicio"] else None,
                "Motivo Não Participação": registro_dict["motivo_nao_participacao"],
                "Ações Realizadas": registro_dict["acoes_realizadas"],
                "Públicos Atendidos": registro_dict["publicos_atendidos"],
                "Vias Emitidas": registro_dict["vias_emitidas"],
                "Registros Nascimento": registro_dict["registros_nascimento"],
                "Averbações Paternidade": registro_dict["averbacoes_paternidade"],
                "Retificações": registro_dict["retificacoes"],
                "Registros Tardios": registro_dict["registros_tardios"],
                "Restaurações": registro_dict["restauracoes"],
                "Classificação": registro_dict["classificacao"],
                "Tags": registro_dict["tags"],
                "Observações": registro_dict["observacoes"]
            })
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": resultado
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Endpoint para obter um registro específico
@app.route("/api/getRegistro", methods=["GET"])
def get_registro():
    try:
        # Obter ID do registro
        id = request.args.get("id")
        if not id:
            return jsonify({
                "success": False,
                "error": "ID não fornecido"
            }), 400
        
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Buscar o registro
        cur.execute("SELECT * FROM registro_semanal WHERE id = %s", (id,))
        registro = cur.fetchone()
        
        if not registro:
            return jsonify({
                "success": False,
                "error": "Registro não encontrado"
            }), 404
        
        # Converter para dicionário e ajustar nomes de campos para compatibilidade com frontend
        registro_dict = dict(registro)
        resultado = {
            "ID": registro_dict["id"],
            "Timestamp": registro_dict["timestamp"].isoformat() if registro_dict["timestamp"] else None,
            "Protocolo": registro_dict["protocolo"],
            "Serventia": registro_dict["serventia"],
            "Email": registro_dict["email"],
            "Telefone": registro_dict["telefone"],
            "Responsável": registro_dict["responsavel"],
            "Participação": registro_dict["participacao"],
            "Data de Início": registro_dict["data_inicio"].isoformat() if registro_dict["data_inicio"] else None,
            "Motivo Não Participação": registro_dict["motivo_nao_participacao"],
            "Ações Realizadas": registro_dict["acoes_realizadas"],
            "Públicos Atendidos": registro_dict["publicos_atendidos"],
            "Vias Emitidas": registro_dict["vias_emitidas"],
            "Registros Nascimento": registro_dict["registros_nascimento"],
            "Averbações Paternidade": registro_dict["averbacoes_paternidade"],
            "Retificações": registro_dict["retificacoes"],
            "Registros Tardios": registro_dict["registros_tardios"],
            "Restaurações": registro_dict["restauracoes"],
            "Classificação": registro_dict["classificacao"],
            "Tags": registro_dict["tags"],
            "Observações": registro_dict["observacoes"]
        }
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "data": resultado
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Endpoint para atualizar um registro
@app.route("/api/atualizarRegistro", methods=["POST"])
def atualizar_registro():
    try:
        # Obter os dados
        data = request.get_json()
        id = data.get("id")
        
        if not id:
            return jsonify({
                "success": False,
                "error": "ID não fornecido"
            }), 400
        
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se o registro existe
        cur.execute("SELECT id FROM registro_semanal WHERE id = %s", (id,))
        if not cur.fetchone():
            return jsonify({
                "success": False,
                "error": "Registro não encontrado"
            }), 404
        
        # Mapeamento de campos do frontend para o banco de dados
        mapeamento_campos = {
            "Serventia": "serventia",
            "Email": "email",
            "Telefone": "telefone",
            "Responsável": "responsavel",
            "Participação": "participacao",
            "Data de Início": "data_inicio",
            "Motivo Não Participação": "motivo_nao_participacao",
            "Ações Realizadas": "acoes_realizadas",
            "Públicos Atendidos": "publicos_atendidos",
            "Vias Emitidas": "vias_emitidas",
            "Registros Nascimento": "registros_nascimento",
            "Averbações Paternidade": "averbacoes_paternidade",
            "Retificações": "retificacoes",
            "Registros Tardios": "registros_tardios",
            "Restaurações": "restauracoes",
            "Classificação": "classificacao",
            "Tags": "tags",
            "Observações": "observacoes"
        }
        
        # Criar query de atualização
        set_clauses = []
        valores = []
        
        for campo_frontend, campo_db in mapeamento_campos.items():
            if campo_frontend in data:
                # Tratamento especial para data
                if campo_frontend == "Data de Início" and data[campo_frontend]:
                    try:
                        # Converter string para objeto date
                        data_valor = datetime.datetime.strptime(data[campo_frontend], "%Y-%m-%d").date()
                        set_clauses.append(f"{campo_db} = %s")
                        valores.append(data_valor)
                    except ValueError:
                        # Se falhar a conversão, definir como NULL
                        set_clauses.append(f"{campo_db} = NULL")
                else:
                    set_clauses.append(f"{campo_db} = %s")
                    valores.append(data[campo_frontend])
        
        if not set_clauses:
            return jsonify({
                "success": False,
                "error": "Nenhum campo para atualizar"
            }), 400
        
        # Adicionar ID para a cláusula WHERE
        valores.append(id)
        
        # Executar a atualização
        query = f"UPDATE registro_semanal SET {', '.join(set_clauses)} WHERE id = %s"
        cur.execute(query, valores)
        conn.commit()
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Registro atualizado com sucesso!"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Endpoint para excluir um registro
@app.route("/api/excluirRegistro", methods=["GET"])
def excluir_registro():
    try:
        # Obter ID do registro
        id = request.args.get("id")
        if not id:
            return jsonify({
                "success": False,
                "error": "ID não fornecido"
            }), 400
        
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar se o registro existe
        cur.execute("SELECT id FROM registro_semanal WHERE id = %s", (id,))
        if not cur.fetchone():
            return jsonify({
                "success": False,
                "error": "Registro não encontrado"
            }), 404
        
        # Executar a exclusão
        cur.execute("DELETE FROM registro_semanal WHERE id = %s", (id,))
        conn.commit()
        
        # Fechar a conexão
        cur.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Registro excluído com sucesso!"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Endpoint raiz (para verificar se a API está funcionando)
@app.route("/")
def index():
    return jsonify({
        "message": "API COGEX está rodando!",
        "version": "1.0.0",
        "endpoints": [
            "/api/init_db",
            "/api/registrar",
            "/api/consultar",
            "/api/getRegistro",
            "/api/atualizarRegistro",
            "/api/excluirRegistro"
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=(os.environ.get("ENVIRONMENT") == "development"))
