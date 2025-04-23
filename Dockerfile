# Dockerfile para API COGEX
FROM python:3.9-slim

WORKDIR /app

# Copiar arquivos de requisitos e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Configurar variável de ambiente para porta
ENV PORT 8080

# Executar o aplicativo com Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
