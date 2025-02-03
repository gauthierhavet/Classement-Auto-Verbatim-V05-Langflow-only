FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV PIP_DEFAULT_TIMEOUT=100

# Crée un utilisateur non-root
RUN useradd -m langflowuser && \
    mkdir /app && \
    chown langflowuser:langflowuser /app

WORKDIR /app

# Installe les dépendances système et les certificats SSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure pip pour utiliser des miroirs alternatifs et augmente la tolérance aux erreurs
RUN pip install --upgrade pip && \
    pip config set global.timeout 100 && \
    pip config set global.retries 10

# Copie et installation des dépendances Python avec des options de robustesse
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

USER langflowuser

EXPOSE 7860

CMD ["langflow", "run"]