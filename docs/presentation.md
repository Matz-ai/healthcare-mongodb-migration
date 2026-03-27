# Présentation — Migration Healthcare vers MongoDB

## Slide 1 — Page de garde

**Migration Big Data Healthcare vers MongoDB**

Solution scalable et conteneurisée pour la gestion des données patients

Date : Mars 2026 | Équipe Data Engineering

---

## Slide 2 — Contexte et problématique

### Le client
- **Secteur** : Healthcare / Santé
- **Dataset** : 55 500 patients, 15 attributs médicaux
- **Format actuel** : Fichier CSV plat

### Problèmes identifiés
- Données impossibles à interroger efficacement
- Aucune indexation → recherches lentes
- Pas de validation automatique des données
- Aucune scalabilité horizontale possible

> **Objectif** : Migrer vers une infrastructure moderne, scalable et sécurisée.

---

## Slide 3 — Solution technique retenue

### Pourquoi MongoDB ?
- **Base documentaire** : Structure flexible adaptée aux données patients
- **Scalabilité horizontale** : Sharding natif pour accompagner la croissance
- **Performance** : Indexes pour des requêtes rapides
- **Écosystème mature** : Drivers Python, outils de monitoring intégrés

### Pourquoi Docker ?
- **Portabilité** : Même environnement local/staging/production
- **Reproductibilité** : `docker-compose up` suffit pour démarrer
- **Isolation** : MongoDB et le script de migration dans des conteneurs séparés

---

## Slide 4 — Architecture technique

```
┌───────────────────────────────────────────────┐
│              DOCKER COMPOSE                   │
├───────────────────────────────────────────────┤
│                                               │
│   CSV (55k patients)                          │
│        │                                      │
│        ▼                                      │
│   ┌──────────────────┐    ┌───────────────┐   │
│   │ Migration Service│───►│   MongoDB     │   │
│   │ (Python 3.11)    │    │   (mongo:7.0) │   │
│   │                  │    │               │   │
│   │ • Validation     │    │ • patients    │   │
│   │ • Batch insert   │    │ • 5 indexes   │   │
│   │ • Dédoublonnage  │    │ • Auth RBAC   │   │
│   └──────────────────┘    └───────┬───────┘   │
│                                   │           │
│                           ┌───────┴───────┐   │
│                           │ Volume Docker │   │
│                           │ (persistance) │   │
│                           └───────────────┘   │
└───────────────────────────────────────────────┘
```

---

## Slide 5 — Schéma de la base de données

### Collection `patients`
```json
{
  "patient_id": "string (unique, clé MD5)",
  "name": "string",
  "age": "int",
  "gender": "Male | Female",
  "blood_type": "A+ | A- | B+ | B- | AB+ | AB- | O+ | O-",
  "medical_condition": "string",
  "admission": {
    "date": "ISODate",
    "type": "Elective | Emergency | Urgent",
    "room_number": "int"
  },
  "discharge_date": "ISODate",
  "doctor": "string",
  "hospital": "string",
  "billing_amount": "double",
  "medication": "string",
  "test_results": "Normal | Abnormal | Inconclusive"
}
```

### Indexes : `patient_id` (unique), `medical_condition`, `admission.date`, `hospital`, `doctor`

---

## Slide 6 — Script de migration

### Processus en 5 étapes

| Étape | Description |
|---|---|
| 1. Lecture | Parsing du CSV ligne par ligne |
| 2. Validation | 8 contrôles (âge, genre, dates, montant, etc.) |
| 3. Dédoublonnage | Clé unique MD5 (nom + âge + date admission) |
| 4. Insertion batch | Lots de 1 000 documents pour la performance |
| 5. Vérification | Count + intégrité post-migration |

### Résultats
- **55 500** documents lus → **~54 966** insérés
- **534** doublons détectés et ignorés
- Durée : **~30 secondes** (~1 800 docs/s)

---

## Slide 7 — Sécurité et authentification

### Modèle RBAC

| Utilisateur | Rôle | Permissions |
|---|---|---|
| `admin` | root | Tous les droits |
| `migrate_user` | readWrite + dbAdmin | Lecture/écriture + gestion indexes |
| `readonly_user` | read | Lecture seule |

### Mesures de sécurité
- Authentification SCRAM-SHA-256
- Réseau Docker isolé (bridge dédié)
- Variables d'environnement pour les credentials
- Volumes en lecture seule pour le CSV source

---

## Slide 8 — Tests et validation

### Tests automatisés (pytest)
- Validation des données patients (âge, genre, groupe sanguin, dates)
- Vérification de la structure du document MongoDB
- Contrôle de la configuration (variables d'environnement)

### Contrôles post-migration
- Comptage des documents vs lignes CSV
- Vérification des valeurs distinctes (conditions, groupes sanguins)
- Calcul de la moyenne billing pour détecter les anomalies
- Vérification que les 5 indexes sont bien créés

---

## Slide 9 — Options de déploiement AWS

| Solution | Coût/mois | Maintenance | Idéal pour |
|---|---|---|---|
| Amazon DocumentDB | ~300 € | Faible | Besoins simples |
| **MongoDB Atlas** | **~450 €** | **Nulle** | **Recommandé** |
| ECS + Fargate | ~160 € | Moyenne | Architecture microservices |
| EC2 self-hosted | ~150 € | Élevée | Budget contraint |

### Recommandation : MongoDB Atlas
- HIPAA compliance native (critique pour le secteur santé)
- Backup continu avec point-in-time recovery
- Sharding automatique si le volume augmente
- Zéro maintenance opérationnelle

---

## Slide 10 — Synthèse et prochaines étapes

### Ce qui a été livré
- ✅ Script de migration Python avec validation et tests
- ✅ Infrastructure Docker portable et fonctionnelle
- ✅ Authentification MongoDB avec rôles adaptés
- ✅ Documentation complète (README, AWS, présentation)

### Prochaines étapes
1. **Validation client** : Démonstration live de la migration
2. **Choix infrastructure cloud** : Atlas vs ECS selon budget
3. **Migration production** : Import vers le cluster cloud choisi
4. **Formation** : Prise en main par l'équipe du client

---

*Merci pour votre attention — démonstration disponible sur demande*
