
,## **Préparation Initiale**

Avant de commencer, assurez-vous d'avoir Docker et Docker Compose installés sur votre système.

Ce guide assume que vous avez un dossier de projet vide pour Langflow. Créez un dossier vide qui servira de base pour votre projet. Ce dossier sera utilisé comme point de départ pour l'installation avec Docker. Vous pouvez le créer simplement avec :

```bash
mkdir mon-projet-langflow
cd mon-projet-langflow
```

### **Création du Dépôt GitHub (Facultatif)**

Si vous souhaitez utiliser un dépôt GitHub pour votre projet, vous pouvez le créer après avoir créé le dossier local :

1. Connectez-vous à votre compte GitHub
2. Cliquez sur "New Repository"
3. Donnez un nom au projet (par exemple `mon-projet-langflow`)
4. Sélectionnez "Private" ou "Public" selon vos besoins
5. Ne cochez pas "Initialize this repository with a README"
6. Créez le dépôt

Ensuite, connectez votre projet local au dépôt GitHub :

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/votre-utilisateur/mon-projet-langflow.git
git push -u origin main
```

Cela établit la connexion avec le dépôt distant.

Ce dossier initial est essentiel car il permettra d'organiser tous les fichiers nécessaires à l'installation et à la configuration.

## **Architecture Finale (Simplifiée mais Robustre)**

Voici l'architecture de base du projet que nous allons utiliser :

```bash
langflow-project/
├── .env                  # Clés secrètes (à ne PAS versionner)
├── docker-compose.yml    # Configuration Docker
├── Dockerfile            # Build de l'image
├── app/                  # Code source de Langflow (personnalisable)
│   ├── components/       # Composants personnalisés
│   └── ...
├── data/                 # Données persistantes
│   └── postgres/         # Base de données PostgreSQL
├── scripts/              # Utilitaires (optionnel)
│   ├── backup_db.sh      # Sauvegarde manuelle de la BDD
│   └── init_db.sh        # Initialisation (optionnel) init_db.sh sert uniquement à pré-remplir la base avec quelques tables ou données initiales si besoin.
└── docs/                 # Documentation (optionnel)
    └── API_DOCS.md       # Documentation générée via Swagger (optionnel)
```

## **Étape 1 : Configuration de Base**

### **1.1 Fichier `.env`**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```bash
# Secrets (à personnaliser)
POSTGRES_USER=admin
POSTGRES_PASSWORD=UnMotDePasseSuperSecurise123!
POSTGRES_DB=langflow_db

# Langflow
LANGFLOW_HOST=0.0.0.0
LANGFLOW_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Langfuse (monitoring, optionnel)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
```

**Important** : Remplacez les valeurs de `POSTGRES_USER`, `POSTGRES_PASSWORD`, `LANGFUSE_SECRET_KEY` et `LANGFUSE_PUBLIC_KEY` par vos propres valeurs.

### **1.2 Fichier `docker-compose.yml`**

Créez un fichier `docker-compose.yml` à la racine du projet avec le contenu suivant :

```yaml
version: '3.8'

services:
  langflow:
    build: .
    volumes:
      - ./app:/app:rw
    ports:
      - "7860:7860"
    environment:
      - LANGFLOW_HOST=${LANGFLOW_HOST}
      - DATABASE_URL=${LANGFLOW_DATABASE_URL}
      # Langfuse (si nécessaire)
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - langflow-network

  db:
    image: postgres:15-alpine
    volumes:
      - ./data/postgres:/var/lib/postgresql/data:rw
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - langflow-network

networks:
  langflow-network:
    driver: bridge
```

### **1.3 Fichier `Dockerfile`**

Le fichier `Dockerfile` doit utiliser l'image Langflow officielle et installer les dépendances nécessaires. Voici un exemple de `Dockerfile` mis à jour :

```dockerfile
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

# Création de l'utilisateur non-root avec permissions adaptées
RUN useradd -m -d /app langflowuser && \
    chown -R langflowuser:langflowuser /app

# Passage à l'utilisateur dédié
USER langflowuser

EXPOSE 7860

# Commande de démarrage avec rechargement automatique
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
```

### **1.4 Fichier `requirements.txt`**

Le fichier `requirements.txt` doit contenir les dépendances Python nécessaires pour Langflow. Voici un exemple de contenu pour `requirements.txt` :

```text
langflow>=1.1.3
psycopg2-binary
python-dotenv
```

## **Étape 2 : Commandes d'Installation**

### **2.1 Initialisation du Projet (Si vous n'avez pas déjà créé les fichiers)**

Si vous n'avez pas déjà créé les fichiers nécessaires, vous pouvez les créer avec les commandes suivantes :

```bash
mkdir -p langflow-project/{app,data/postgres,scripts,docs}
cd langflow-project
touch .env docker-compose.yml Dockerfile requirements.txt
```

### **2.2 Premier Lancement**

Construisez et démarrez les conteneurs Docker avec la commande suivante :

```bash
docker-compose up --build -d
```

Cette commande construira l'image Docker de Langflow en utilisant le `Dockerfile`, téléchargera l'image PostgreSQL et démarrera les conteneurs pour Langflow et la base de données.

**Note :** La base de données PostgreSQL sera créée automatiquement dans le répertoire `./data/postgres` lors du premier démarrage. Vous n'avez pas besoin de créer manuellement un fichier de base de données.

Accédez à Langflow : [http://localhost:7860](http://localhost:7860)

## **Étape 3 : Personnalisation de Langflow**

### **3.1 Modifier le code de Langflow**

Vous pouvez modifier le code source de Langflow dans le répertoire `./app`. Les changements seront reflétés instantanément dans le conteneur grâce au volume monté.

Exemple pour ajouter un composant personnalisé :

```bash
mkdir -p app/components/custom
touch app/components/custom/my_component.py
```

### **3.2 Documentation Automatique (Swagger)**

Vous pouvez générer automatiquement une documentation API avec Swagger.

*   Accédez à la documentation : [http://localhost:7860/docs](http://localhost:7860/docs)

## **Étape 4 : Gestion des Données**

### **4.1 Sauvegarde de la base de données PostgreSQL**

GitHub ne sauvegarde **pas** automatiquement les données des conteneurs !

Pour sauvegarder la base de données PostgreSQL, vous pouvez utiliser un script comme `scripts/backup_db.sh` :

```bash
#!/bin/bash
docker-compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y-%m-%d).sql
```

Exécutez-le avec :

```bash
chmod +x scripts/backup_db.sh
./scripts/backup_db.sh
```

### **4.2 Restauration de la BDD**

Pour restaurer la base de données PostgreSQL à partir d'une sauvegarde :

```bash
cat backup_2023-10-01.sql | docker-compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} 
```

## **Étape 5 : Sécurité Basique**

### **5.1 Fichier `.gitignore`**

Créez un fichier `.gitignore` pour éviter de commiter les fichiers sensibles :

```text
.env
data/
__pycache__
*.pyc
```

### **5.2 Mise à Jour des Dépendances**

Mettez à jour `requirements.txt` si nécessaire, puis reconstruisez l'image :

```bash
docker-compose build --no-cache && docker-compose up -d
```

## **Étape 6 : Déploiement en Production (Light)**

### **6.1 Modifications pour la Production**

Dans `docker-compose.yml`, ajoutez `restart: unless-stopped` au service `langflow` pour un redémarrage automatique en cas d'erreur :

```yaml
services:
  langflow:
    restart: unless-stopped  # Redémarrage automatique
    environment:
      - LANGFLOW_ENV=production
```

### **6.2 Surveillance des Logs**

```bash
docker-compose logs -f langflow
```

## **Résumé des Commandes Utiles**

| Action               | Commande                                       |
| -------------------- | ---------------------------------------------- |
| Démarrer/Stopper     | `docker-compose up -d` / `docker-compose down` |
| Voir les logs        | `docker-compose logs -f`                      |
| Accès à la BDD       | `docker-compose exec db psql -U admin -d langflow_db` |
| Sauvegarder          | `./scripts/backup_db.sh`                      |
| Redémarrer           | `docker-compose restart`                      |

## **FAQ pour Débutants**

**Q** : *Où sont stockées les données de la base PostgreSQL ?*
**R** : Dans `./data/postgres`. Ne supprimez pas ce dossier !

**Q** : *Comment ajouter une clé API externe ?*
**R** : Ajoutez-la dans `.env` et référencez-la dans `docker-compose.yml`.

**Q** : *Pourquoi utiliser `docker-compose` ?*
**R** : C’est l’outil standard pour gérer des applications multi-conteneurs simplement.

Cette méthode couvre **100% de vos besoins actuels** tout en restant simple. Testez chaque étape, et adaptez-la progressivement ! 🚀