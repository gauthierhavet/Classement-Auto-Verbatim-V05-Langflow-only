## **Préparation Initiale**

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
│   └── sqlite/         # Base de données SQLite
├── scripts/              # Utilitaires (optionnel)
│   └── init_db.sh        # Initialisation (optionnel) init_db.sh sert uniquement à pré-remplir la base avec quelques tables ou données initiales si besoin.
└── docs/                 # Documentation (optionnel)
    └── API_DOCS.md       # Documentation générée via Swagger (optionnel)
```

## **Étape 1 : Configuration de Base**

### **1.1 Fichier `.env`**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```bash
# Langflow
LANGFLOW_HOST=0.0.0.0
LANGFLOW_DATABASE_URL=sqlite:///./data/sqlite/langflow.db

# Langfuse (monitoring, optionnel)

# Configuration des dossiers (important)
LANGFLOW_CONFIG_DIR=/data
LANGFLOW_SAVE_DB_IN_CONFIG_DIR=true
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST="https://cloud.langfuse.com"
```

**Important** : Remplacez les valeurs de `LANGFUSE_SECRET_KEY` et `LANGFUSE_PUBLIC_KEY` par vos propres valeurs.

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
      - LANGFUSE_HOST=${LANGFUSE_HOST}
    networks:
      - langflow-network
    env_file:
      - .env

volumes:
  data:
  app:

networks:
  langflow-network:
    driver: bridge
```


**Note importante**: La déclaration des volumes est nécessaire pour assurer la persistance des données
et la bonne gestion des permissions entre le conteneur et le système hôte.

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
    uv venv -p python3.11 && \  # Version Python spécifique pour stabilité
    uv pip install --system "langflow>=1.1.3"

# Attribution des permissions sur le dossier de Langflow (crucial)
RUN chmod -R 777 /usr/local/lib/python3.12/site-packages/langflow

# Création de l'utilisateur non-root avec permissions adaptées
RUN useradd -m -d /app langflowuser && \
    # S'assure que l'utilisateur a les bonnes permissions
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
python-dotenv
```

## **Étape 2 : Commandes d'Installation**

### **2.1 Initialisation du Projet (Si vous n'avez pas déjà créé les fichiers)**

Si vous n'avez pas déjà créé les fichiers nécessaires, vous pouvez les créer avec les commandes suivantes :

```bash
mkdir -p langflow-project/{app,data/sqlite,scripts,docs}
cd langflow-project
touch .env docker-compose.yml Dockerfile requirements.txt
```

### **2.2 Premier Lancement**

Construisez et démarrez les conteneurs Docker avec la commande suivante :

```bash
docker-compose up --build -d
```

Cette commande construira l'image Docker de Langflow en utilisant le `Dockerfile` et démarrera le conteneur pour Langflow.

**Note :** La base de données SQLite sera créée automatiquement dans le répertoire `./data/sqlite` lors du premier démarrage.

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

-   Accédez à la documentation : [http://localhost:7860/docs](http://localhost:7860/docs)

## **Étape 4 : Gestion des Données**

###  **4.1 Gestion de la base de données SQLite**

Pour inspecter ou modifier la base SQLite, vous pouvez utiliser des outils comme DB Browser for SQLite.

**Note** : Par défaut, la base SQLite est supprimée si Langflow est désinstallé. Pour éviter cela, utilisez `LANGFLOW_SAVE_DB_IN_CONFIG_DIR=true`.

**Important** : Avec la nouvelle configuration :
- La base de données est automatiquement sauvegardée dans `/data/langflow.db`
- Le fichier `secret_key` est stocké dans `/data`
- Cette configuration assure une meilleure persistance des données
- Les permissions sont correctement gérées grâce aux volumes Docker

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

### **6.3 Gestion des Logs Applicatifs**

Langflow génère des logs détaillés qui sont maintenant stockés dans le dossier `app/logs/`. Pour les consulter :

```bash
# Voir les logs en direct
tail -f app/logs/langflow.log
```

Les logs contiennent des informations importantes sur :
- Les requêtes HTTP
- Les erreurs d'exécution
- Les performances de l'application

## **Résumé des Commandes Utiles**

| Action               | Commande                                       |
| -------------------- | ---------------------------------------------- |
| Démarrer/Stopper     | `docker-compose up -d` / `docker-compose down` |
| Voir les logs        | `docker-compose logs -f`                      |
| Redémarrer           | `docker-compose restart`                      |

## **FAQ pour Débutants**

**Q** : *Où sont stockées les données de la base SQLite ?*
**R** : Dans `./data/langflow.db`. Ne supprimez pas ce dossier !

**Q** : *Comment ajouter une clé API externe ?*
**R** : Ajoutez-la dans `.env` et référencez-la dans `docker-compose.yml`.

**Q** : *Pourquoi utiliser UV dans le Dockerfile ?*
**R** : UV est un nouvel installateur Python ultra-rapide qui :
- Accélère significativement l'installation des dépendances
- Offre une meilleure gestion du cache
- Assure une compatibilité plus stable avec Python 3.11
- Réduit le temps de construction de l'image Docker

Le paramètre `UV_HTTP_TIMEOUT=300` permet d'éviter les timeouts lors de l'installation de gros packages.

**Q** : *Pourquoi utiliser `docker-compose` ?*
**R** : C’est l’outil standard pour gérer des applications multi-conteneurs simplement.

Cette méthode couvre **100% de vos besoins actuels** tout en restant simple. Testez chaque étape, et adaptez-la progressivement ! 🚀

## **Utilisation de PostgreSQL (optionnel)**

Si vous souhaitez utiliser une base de données PostgreSQL au lieu de SQLite, vous pouvez suivre les étapes suivantes :

1. Créez un fichier `.env` et définissez la variable `LANGFLOW_DATABASE_URL` avec l'URL de connexion à PostgreSQL (format : `postgresql://user:password@host:port/dbname`).
2. Modifiez le fichier `docker-compose.yml` pour ajouter un service `db` pour PostgreSQL. Voici un exemple de configuration :

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
          - POSTGRES_USER=admin
          - POSTGRES_PASSWORD=UnMotDePasseSuperSecurise123!
          - POSTGRES_DB=langflow_db
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
          interval: 10s
          timeout: 5s
          retries: 5
        networks:
          - langflow-network

    networks:
      langflow-network:
        driver: bridge
    ```
3. Exécutez Langflow avec `docker-compose up -d` pour démarrer les conteneurs Langflow et PostgreSQL.
```
<line_count>394</line_count>
