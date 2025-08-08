FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para dados
RUN mkdir -p /app/data

# Expor porta (opcional, para health checks futuros)
EXPOSE 8000

# Comando padrão: rodar migrações e iniciar bot
CMD alembic upgrade head && python run.py
