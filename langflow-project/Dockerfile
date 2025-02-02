FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

# Crée un utilisateur non-root
RUN useradd -m langflowuser && \
    mkdir /app && \
    chown langflowuser:langflowuser /app

WORKDIR /app

# Installe les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER langflowuser

EXPOSE 7860

CMD ["langflow", "run"]