# Utilise l'image officielle mise à jour de Langflow
FROM langflowai/langflow:latest

ENV PYTHONUNBUFFERED=1
ENV LANGFLOW_HOST=0.0.0.0
ENV LANGFLOW_PORT=7860

# Configuration spécifique pour les dépendances
ENV UV_HTTP_TIMEOUT=300
ENV UV_CACHE_DIR=/app/cache

WORKDIR /app

# Passage temporaire en root pour les installations
USER root

# Installation des dépendances système critiques
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libssl-dev \
    ca-certificates \
    curl \
    build-essential \
    gcc \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Installation de lz4 en premier
RUN pip install --no-cache-dir lz4==4.3.2

# Configuration optimisée de UV et installation de langflow
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv venv -p python3.11 && \
    uv pip install --system "langflow>=1.1.3"

# Attribution des permissions sur le dossier de Langflow
RUN chmod -R 777 /usr/local/lib/python3.12/site-packages/langflow

# Création de l'utilisateur non-root avec permissions adaptées
RUN useradd -m -d /app langflowuser && \
    chown -R langflowuser:langflowuser /app

# Passage à l'utilisateur dédié
USER langflowuser

EXPOSE 7860

# Commande de démarrage avec rechargement automatique
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]