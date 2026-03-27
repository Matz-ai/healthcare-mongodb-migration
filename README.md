# Healthcare MongoDB Migration

## Contexte

Migration d'un dataset médical de **55 500 patients** (CSV) vers MongoDB, conteneurisé avec Docker.

## Architecture

```
┌────────────────────────────────────────────────────┐
│                  DOCKER COMPOSE                    │
├────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────────┐  │
│  │   MongoDB 7.0    │◄───┤  Migration Service   │  │
│  │   :27017         │    │  (Python 3.11)       │  │
│  │                  │    │                      │  │
│  │  • healthcare DB │    │  • Dédoublonnage     │  │
│  │  • patients col. │    │  • Insertion batch   │  │
│  │  • auth RBAC     │    │  • Vérification      │  │
│  └────────┬─────────┘    └──────────────────────┘  │
│           │                                        │
│   ┌───────┴────────┐  ┌────────────────────────┐   │
│   │  Volume MongoDB│  │  Volume CSV (read-only)│   │
│   └────────────────┘  └────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

## Schéma de la base de données

### Collection : `patients`

```json
{
  "_id": "ObjectId",
  "patient_id": "string (unique, clé MD5)",
  "name": "string",
  "age": "int",
  "gender": "string",
  "blood_type": "string",
  "medical_condition": "string",
  "admission_date": "string",
  "admission_type": "string",
  "discharge_date": "string",
  "room_number": "int",
  "doctor": "string",
  "hospital": "string",
  "insurance_provider": "string",
  "billing_amount": "double",
  "medication": "string",
  "test_results": "string"
}
```

Un index unique est créé sur `patient_id` pour empêcher les doublons.

## Authentification & Rôles

Les utilisateurs sont créés automatiquement au premier lancement via `mongo-init/init-mongo.js` :

| Utilisateur | Rôle | Permissions |
|---|---|---|
| `admin` | root | Tous les droits (créé par Docker) |
| `migrate_user` | readWrite + dbAdmin | Lecture/écriture sur la DB healthcare |
| `readonly_user` | read | Lecture seule |

## Logique du script de migration

Le script `src/migrate.py` effectue 3 opérations :

1. **Dédoublonnage** : chaque patient reçoit un ID unique (hash MD5 de nom + âge + date d'admission). Si deux lignes produisent le même ID, seule la première est conservée.

2. **Insertion par batch** : les documents sont insérés par paquets de 1 000 pour optimiser les performances.

3. **Vérification** : après la migration, le script compare le nombre de documents en base avec le nombre attendu.

## Démarrage rapide

### Prérequis
- Docker & Docker Compose

### Lancer le projet

```bash
# Cloner le dépôt
git clone <repo-url>
cd healthcare-mongodb

# Démarrer MongoDB
docker-compose up -d mongo

# Attendre l'initialisation (~10s)
sleep 10

# Lancer la migration
docker-compose run --rm migration

# Vérifier le résultat
docker-compose exec mongo mongosh -u migrate_user -p migrate_pass \
  --authenticationDatabase healthcare \
  --eval "db.patients.countDocuments()"
```

## Structure du projet

```
healthcare-mongodb/
├── data/
│   └── healthcare_dataset.csv      # Dataset source (55 500 lignes)
├── src/
│   ├── migrate.py                  # Script de migration
│   └── test_migration.py           # Tests unitaires
├── mongo-init/
│   └── init-mongo.js               # Création users et rôles
├── docs/
│   ├── aws-deployment.md           # Étude déploiement AWS
│   └── presentation.md             # Support de présentation
├── docker-compose.yml              # Orchestration des conteneurs
├── Dockerfile                      # Image du service migration
├── requirements.txt                # Dépendances Python
└── README.md
```

## Tests

```bash
docker-compose run --rm migration pytest src/test_migration.py -v
```

## Déploiement AWS

Voir [docs/aws-deployment.md](docs/aws-deployment.md) pour l'étude comparative : DocumentDB, ECS, S3, tarifications.
