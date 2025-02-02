# Installation de Langflow avec Docker

Cette configuration permet de déployer Langflow avec une base de données PostgreSQL persistante et une configuration optimisée.

## Structure des dossiers

```
./
├── config/          # Configuration de Langflow
├── data/           # Données persistantes de Langflow
├── postgres-data/  # Données persistantes PostgreSQL
└── docker-compose.yml
```

## Prérequis

- Docker
- Docker Compose

## Installation

1. Lancer l'application :
```bash
docker compose up -d
```

2. Accéder à l'interface :
- Ouvrir http://localhost:7860 dans votre navigateur

## Configuration

### Volumes persistants
- `./config`: Configuration de Langflow
- `./data`: Stockage des données Langflow
- `./postgres-data`: Données PostgreSQL

### Base de données
- PostgreSQL 16
- Nom de la base : langflow
- Utilisateur : langflow
- Mot de passe : langflow_password
- Port : 5432

### Ports exposés
- Langflow UI : 7860
- PostgreSQL : 5432

## Maintenance

### Logs
```bash
docker compose logs -f langflow  # Logs de Langflow
docker compose logs -f postgres  # Logs de PostgreSQL
```

### Redémarrage
```bash
docker compose restart  # Redémarre tous les services
```

### Mise à jour
```bash
docker compose pull    # Télécharge les nouvelles images
docker compose up -d  # Redémarre avec les nouvelles images
```

## Sécurité

Les données sont persistées localement dans les dossiers dédiés. Il est recommandé de :
- Sauvegarder régulièrement les dossiers `config`, `data` et `postgres-data`
- Modifier les mots de passe par défaut en production
