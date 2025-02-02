## **Préparation Initiale**

Avant de commencer, créez un dossier GitHub vide (scratch) qui servira de base pour votre projet. Ce dossier sera utilisé comme point de départ pour l'installation avec Docker. Vous pouvez le créer simplement avec :

```bash
mkdir mon-projet-langflow
cd mon-projet-langflow

### **Création du Dépôt GitHub**

Après avoir créé le dossier local, créez un nouveau repository sur GitHub :

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

```

Ce dossier initial est essentiel car il permettra d'organiser tous les fichiers nécessaires à l'installation et à la configuration.


Merci pour ces précisions ! Voici une **méthode complète et simplifiée** pour installer Langflow avec PostgreSQL, adaptée à vos besoins (débutant, mono-utilisateur, prêt pour production légère). Je vais tout détailler en étapes claires.

---

## **Architecture Finale (Simplifiée mais Robustre)**
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
├── scripts/              # Utilitaires
│   ├── backup_db.sh      # Sauvegarde manuelle de la BDD
│   └── init_db.sh        # Initialisation (optionnel) init_db.sh sert uniquement à pré-remplir la base avec quelques tables ou données initiales si besoin.
└── docs/                 # Documentation
    └── API_DOCS.md       # Documentation générée via Swagger
```

---

## **Étape 1 : Configuration de Base**

### **1.1 Fichier `.env`**
```bash
# Secrets (à personnaliser)
POSTGRES_USER=admin
POSTGRES_PASSWORD=UnMotDePasseSuperSecurise123!
POSTGRES_DB=langflow_db

# Langflow
LANGFLOW_HOST=0.0.0.0
LANGFLOW_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

# Langfuse (monitoring)
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
```

### **1.2 Fichier `docker-compose.yml`**
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
```dockerfile
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
```

### **1.4 Fichier `requirements.txt`**
```text
langflow
psycopg2
python-dotenv  # Pour charger les variables d'environnement depuis .env
```

---

## **Étape 2 : Commandes d'Installation**

### **2.1 Initialisation du Projet**
```bash
mkdir -p langflow-project/{app,data/postgres,scripts,docs}
cd langflow-project
touch .env docker-compose.yml Dockerfile requirements.txt
```

### **2.2 Premier Lancement**
```bash
docker-compose up --build -d
```

Accédez à Langflow : [http://localhost:7860](http://localhost:7860)

---

## **Étape 3 : Personnalisation de Langflow**

### **3.1 Modifier le code de Langflow**
- Éditez les fichiers dans `./app` → changements instantanés dans le conteneur.
- Exemple pour ajouter un composant personnalisé :
  ```bash
  mkdir -p app/components/custom
  touch app/components/custom/my_component.py
  ```

### **3.2 Documentation Automatique (Swagger)**
- Ajoutez une route dans `app/main.py` :
  ```python
  from fastapi import FastAPI
  from fastapi.openapi.utils import get_openapi

  app = FastAPI()

  def custom_openapi():
      if app.openapi_schema:
          return app.openapi_schema
      openapi_schema = get_openapi(
          title="Langflow API",
          version="1.0.0",
          routes=app.routes,
      )
      app.openapi_schema = openapi_schema
      return app.openapi_schema

  app.openapi = custom_openapi
  ```
- Accédez à la documentation : [http://localhost:7860/docs](http://localhost:7860/docs)

---

## **Étape 4 : Gestion des Données**

### **4.1 Sauvegarde de la BDD (Réponse à votre question sur GitHub)**
- GitHub ne sauvegarde **pas** automatiquement les données des conteneurs !  
- Utilisez le script `scripts/backup_db.sh` :
  ```bash
  #!/bin/bash
  docker-compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y-%m-%d).sql
  ```
- Exécutez-le :
  ```bash
  chmod +x scripts/backup_db.sh
  ./scripts/backup_db.sh
  ```

### **4.2 Restauration de la BDD**
```bash
cat backup_2023-10-01.sql | docker-compose exec -T db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

---

## **Étape 5 : Sécurité Basique**

### **5.1 Fichier `.gitignore`**
```text
.env
data/
__pycache__
*.pyc
```

### **5.2 Mise à Jour des Dépendances**
- Mettez à jour `requirements.txt` puis :
  ```bash
  docker-compose build --no-cache && docker-compose up -d
  ```

---

## **Étape 6 : Déploiement en Production (Light)**

### **6.1 Modifications pour la Production**
- Dans `docker-compose.yml`, ajoutez :
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

---

## **Résumé des Commandes Utiles**

| **Action**               | **Commande**                                  |
|--------------------------|-----------------------------------------------|
| Démarrer/Stopper         | `docker-compose up -d` / `docker-compose down`|
| Voir les logs            | `docker-compose logs -f`                     |
| Accès à la BDD           | `docker-compose exec db psql -U admin -d langflow_db` |
| Sauvegarder              | `./scripts/backup_db.sh`                     |
| Redémarrer               | `docker-compose restart`                     |

---

## **FAQ pour Débutants**

**Q**: *Où sont stockées les données de la base PostgreSQL ?*  
**R**: Dans `./data/postgres`. Ne supprimez pas ce dossier !

**Q**: *Comment ajouter une clé API externe ?*  
**R**: Ajoutez-la dans `.env` et référencez-la dans `docker-compose.yml`.

**Q**: *Pourquoi utiliser `docker-compose` ?*  
**R**: C’est l’outil standard pour gérer des applications multi-conteneurs simplement.

---

Cette méthode couvre **100% de vos besoins actuels** tout en restant simple. Testez chaque étape, et adaptez-la progressivement ! 🚀