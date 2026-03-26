# Healthcare MongoDB Migration

## 📋 Contexte

Migration d'un dataset médical de **55 500 patients** vers MongoDB avec conteneurisation Docker pour garantir la portabilité et la scalabilité.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐         ┌──────────────────────────┐     │
│  │   MongoDB    │◄────────┤    Migration Service     │     │
│  │   :27017     │         │    (Python Script)       │     │
│  │              │         │                          │     │
│  │  • healthcare│         │  • Validation données    │     │
│  │  • patients  │         │  • Insertion batch       │     │
│  │  • indexes   │         │  • Tests d'intégrité     │     │
│  └──────────────┘         └──────────────────────────┘     │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                         │
│  │MongoDB Volume│  (Persistance données)                   │
│  └──────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Schéma de la Base de Données

### Collection : `patients`

```json
{
  "_id": ObjectId,
  "patient_id": "string (unique)",
  "name": "string",
  "age": "int",
  "gender": "string [Male|Female]",
  "blood_type": "string",
  "medical_condition": "string",
  "admission": {
    "date": "ISODate",
    "type": "string [Elective|Emergency|Urgent]",
    "room_number": "int"
  },
  "discharge_date": "ISODate",
  "doctor": "string",
  "hospital": "string",
  "insurance_provider": "string",
  "billing_amount": "double",
  "medication": "string",
  "test_results": "string [Normal|Abnormal|Inconclusive]",
  "metadata": {
    "imported_at": "ISODate",
    "batch_id": "string",
    "validation_status": "string"
  }
}
```

### Indexes créés

- `patient_id` : Unique
- `medical_condition` : Pour filtres rapides
- `admission.date` : Pour requêtes temporelles
- `hospital` : Pour regroupements
- `doctor` : Pour recherches par praticien

## 🔐 Authentification & Rôles

| Utilisateur | Rôle | Permissions |
|-------------|------|-------------|
| `admin` | root | Tous les droits |
| `migrate_user` | readWrite healthcare | Lecture/Écriture sur DB healthcare |
| `readonly_user` | read healthcare | Lecture seule sur DB healthcare |

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose installés
- Git (pour versionnement)

### Installation

```bash
# 1. Cloner le projet
git clone <repo-url>
cd healthcare-mongodb

# 2. Lancer MongoDB
docker-compose up -d mongo

# 3. Attendre l'initialisation (10s)
sleep 10

# 4. Lancer la migration
docker-compose run --rm migration

# 5. Vérifier l'importation
docker-compose exec mongo mongosh -u migrate_user -p migrate_pass --authenticationDatabase healthcare --eval "db.patients.countDocuments()"
```

### Résultat attendu
```
✅ Migration réussie!
📊 55 500 documents insérés
📈 534 doublons ignorés
⏱️ Durée: ~30 secondes
```

## 📁 Structure du Projet

```
healthcare-mongodb/
├── data/
│   └── healthcare_dataset.csv    # Dataset source
├── src/
│   ├── migrate.py                # Script de migration principal
│   └── test_migration.py         # Tests unitaires
├── mongo-init/
│   └── init-mongo.js             # Création users/roles/indexes
├── docs/
│   ├── aws-deployment.md         # Recherche AWS
│   └── presentation.md           # Structure présentation
├── docker-compose.yml            # Orchestration containers
├── requirements.txt              # Dépendances Python
├── Dockerfile                    # Image migration
└── README.md                     # Ce fichier
```

## 🧪 Tests

```bash
# Lancer les tests
docker-compose run --rm migration pytest test_migration.py -v
```

Tests inclus :
- ✅ Connexion MongoDB
- ✅ Intégrité des données (count, doublons)
- ✅ Validation des types
- ✅ Performance des requêtes (indexes)

## ☁️ Déploiement AWS

Voir [docs/aws-deployment.md](docs/aws-deployment.md) pour :
- Amazon DocumentDB
- MongoDB Atlas sur AWS
- Déploiement EC2 avec Docker
- Architecture recommandée

## 📈 Performance

| Métrique | Valeur |
|----------|--------|
| Temps de migration | ~30s |
| Insertion batch | 1000 docs/batch |
| Index créés | 5 |
| Doublons détectés | 534 |

## 📝 Journal de Bord

| Date | Étape | Statut |
|------|-------|--------|
| 25/03 | Analyse dataset | ✅ |
| 25/03 | Création architecture Docker | ✅ |
| 25/03 | Script migration Python | ✅ |
| 25/03 | Authentification MongoDB | ✅ |
| 25/03 | Tests d'intégrité | ✅ |
| 25/03 | Documentation AWS | ✅ |

## 👤 Auteur

Mission réalisée dans le cadre du projet de migration Big Data pour client healthcare.
