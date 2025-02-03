# Installation de Langflow avec Docker Compose

Ce guide vous expliquera comment installer et exécuter Langflow en utilisant Docker Compose.

## Prérequis

*   Docker et Docker Compose doivent être installés sur votre système.

## Étapes d'installation

1. **Clonez le dépôt Langflow :**

    ```bash
    git clone <URL_du_depot>
    cd langflow-project
    ```

2. **Configurez les variables d'environnement :**

    *   Renommez le fichier `.env.example` en `.env` s'il existe.
    *   Ouvrez le fichier `.env` et mettez à jour les variables suivantes si nécessaire :
        *   `POSTGRES_USER` : Nom d'utilisateur pour la base de données PostgreSQL.
        *   `POSTGRES_PASSWORD` : Mot de passe pour la base de données PostgreSQL.
        *   `POSTGRES_DB` : Nom de la base de données PostgreSQL.
        *   `LANGFLOW_HOST` : Hôte sur lequel Langflow sera accessible (laissez `0.0.0.0` pour une accessibilité depuis n'importe quelle interface).
        *   `LANGFLOW_DATABASE_URL` : URL de connexion à la base de données PostgreSQL. La valeur par défaut devrait fonctionner si vous utilisez les paramètres par défaut de Docker Compose.
        *   `LANGFUSE_SECRET_KEY` et `LANGFUSE_PUBLIC_KEY` : Clés pour l'intégration de Langfuse (facultatif).

3. **Construisez et exécutez les conteneurs Docker :**

    ```bash
    docker-compose up --build
    ```

    Cette commande construira l'image Docker de Langflow en utilisant le `Dockerfile` et démarrera les conteneurs pour Langflow et la base de données PostgreSQL.

4. **Accédez à l'application Langflow :**

    Une fois les conteneurs démarrés, vous pouvez accéder à l'application Langflow dans votre navigateur à l'adresse `http://localhost:7860`.

## Remarques

*   Les données de la base de données PostgreSQL seront stockées dans le répertoire `./data/postgres` sur votre hôte.
*   Si vous rencontrez des erreurs lors de l'installation, assurez-vous que les variables d'environnement sont correctement configurées et que les ports nécessaires sont disponibles.
*   Vous pouvez arrêter les conteneurs en exécutant `docker-compose down` dans le répertoire `langflow-project`.

## Dépannage

*   **Erreur "unable to open database file"** : Cette erreur peut se produire si le fichier de base de données SQLite n'existe pas ou n'est pas accessible. Cependant, dans cette configuration, Langflow utilise une base de données PostgreSQL, et non SQLite. Assurez-vous que la variable `LANGFLOW_DATABASE_URL` est correctement configurée pour pointer vers la base de données PostgreSQL.
*   **Erreur "no configuration file provided: not found"** : Assurez-vous d'exécuter la commande `docker-compose up --build` dans le répertoire `langflow-project`, où se trouve le fichier `docker-compose.yml`.