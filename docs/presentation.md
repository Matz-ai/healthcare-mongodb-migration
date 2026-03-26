# Présentation : Migration Healthcare vers MongoDB

## SLIDE 1 - Page de Garde
**Titre** : Migration Big Data Healthcare vers MongoDB  
**Sous-titre** : Solution scalable et cloud-ready pour la gestion des données patients  
**Date** : Mars 2026  
**Présentateur** : Équipe Data Engineering

---

## SLIDE 2 - Contexte de la Mission

### Le Client
- **Secteur** : Healthcare / Santé
- **Problématique** : Scalabilité des traitements de données quotidiennes
- **Dataset** : 55 500+ patients, 15 attributs médicaux
- **Enjeu** : Performance, sécurité, évolutivité

### Défi
> "Comment migrer nos données médicales vers une infrastructure moderne, scalable et cloud-ready tout en garantissant la sécurité et l'intégrité des données ?"

---

## SLIDE 3 - État des Lieux

### Dataset analysé
| Caractéristique | Valeur |
|----------------|--------|
| Patients | 55 500 |
| Attributs | 15 |
| Doublons détectés | 534 |
| Conditions médicales | 6 types |
| Hôpitaux uniques | 39 876 |

### Problèmes identifiés
- ❌ Données plates (CSV) difficiles à interroger
- ❌ Pas d'indexation = recherches lentes
- ❌ Aucune validation automatique
- ❌ Pas de scalabilité horizontale

---

## SLIDE 4 - Objectifs du Projet

### 1. Migration Automatisée
- Script Python robuste avec validation
- Détection et gestion des doublons
- Tests d'intégrité automatiques

### 2. Infrastructure Conteneurisée
- Docker pour portabilité
- MongoDB avec authentification
- Déploiement reproductible

### 3. Architecture Cloud
- Étude des options AWS
- Recommandation sur mesure
- Plan de migration

---

## SLIDE 5 - Architecture Technique

```
┌────────────────────────────────────────────────┐
│            ARCHITECTURE CIBLE                  │
├────────────────────────────────────────────────┤
│                                                │
│   CSV Dataset  ──►  Migration Service  ──►    │
│   (55k patients)    (Python/Docker)           │
│                            │                   │
│                            ▼                   │
│                    ┌──────────────┐            │
│                    │   MongoDB    │            │
│                    │  (Docker)    │            │
│                    │              │            │
│                    │ • patients   │            │
│                    │ • indexes    │            │
│                    │ • auth       │            │
│                    └──────────────┘            │
│                           │                    │
│                    ┌──────┴──────┐             │
│                    │  Persistance │             │
│                    │   (Volume)   │             │
│                    └──────────────┘             │
└────────────────────────────────────────────────┘
```

---

## SLIDE 6 - Schéma de la Base de Données

### Collection : `patients`

```json
{
  "_id": ObjectId,
  "patient_id": "string (unique)",
  "name": "string",
  "age": "int",
  "gender": "string",
  "blood_type": "string",
  "medical_condition": "string",
  "admission": {
    "date": "ISODate",
    "type": "string",
    "room_number": "int"
  },
  "billing_amount": "double",
  "doctor": "string",
  "hospital": "string",
  "medication": "string",
  "test_results": "string"
}
```

### Indexes stratégiques
- `patient_id` : Unique
- `medical_condition` : Recherches par pathologie
- `admission.date` : Analyses temporelles
- `hospital` : Regroupements

---

## SLIDE 7 - Script de Migration

### Caractéristiques
| Aspect | Implémentation |
|--------|----------------|
| Validation | 15 contrôles par patient |
| Batch size | 1000 documents |
| Débit | ~1 850 docs/seconde |
| Doublons gérés | Clé MD5 (nom+âge+date) |

### Processus
1. **Lecture** : Parsing CSV avec validation types
2. **Validation** : Age, genre, groupe sanguin, dates...
3. **Dédoublonnage** : Clé unique générée
4. **Insertion** : Batch de 1000 pour performance
5. **Vérification** : Count + intégrité post-migration

---

## SLIDE 8 - Sécurité & Authentification

### Modèle RBAC (Role-Based Access Control)

| Utilisateur | Rôle | Permissions |
|-------------|------|-------------|
| `admin` | root | Full access |
| `migrate_user` | dbAdmin | Read/Write + Index |
| `analyst_user` | read + write analysis | Lecture + analyses |
| `readonly_user` | read | Lecture seule |

### Sécurité implémentée
- ✅ Authentification SCRAM-SHA-256
- ✅ Isolation réseau (Docker network)
- ✅ Variables d'environnement pour secrets
- ✅ Pas de données sensibles en dur

---

## SLIDE 9 - Tests & Validation

### Couverture de tests
```
✅ Tests unitaires (pytest)
   ├── Validation données (15 cas)
   ├── Connexion MongoDB
   └── Structure document

✅ Tests d'intégrité
   ├── Count documents
   ├── Unicité patient_id
   ├── Types de données
   └── Performance requêtes
```

### Résultats migration
| Métrique | Résultat |
|----------|----------|
| Documents insérés | 55 500 |
| Doublons ignorés | 534 |
| Temps total | ~30 secondes |
| Erreurs | 0 |

---

## SLIDE 10 - Options Cloud AWS

### Comparatif solutions

| Solution | Type | Coût/mois | Gestion |
|----------|------|-----------|---------|
| DocumentDB | Managé | 300-400€ | AWS |
| MongoDB Atlas | DBaaS | 400-600€ | MongoDB |
| **EC2 + Docker** | **Self-hosted** | **150-250€** | **Client** |
| ECS Fargate | Container | 200-350€ | AWS |

### Notre recommandation : **MongoDB Atlas**

**Pourquoi ?**
- HIPAA compliance native (santé)
- Aucune maintenance Ops
- Sharding automatique
- Backup continu
- Support professionnel

---

## SLIDE 11 - Architecture Cloud Recommandée

```
┌─────────────────────────────────────────────────────────┐
│                    AWS + MongoDB Atlas                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │         MongoDB Atlas Cluster M10               │   │
│   │    ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │
│   │    │Primary  │  │Secondary│  │Secondary│       │   │
│   │    │eu-west  │  │eu-west  │  │eu-west  │       │   │
│   │    └─────────┘  └─────────┘  └─────────┘       │   │
│   └─────────────────────────────────────────────────┘   │
│                      │                                  │
│         ┌────────────┼────────────┐                    │
│         ▼            ▼            ▼                    │
│    ┌────────┐   ┌────────┐   ┌────────┐               │
│    │  App   │   │  App   │   │  BI    │               │
│    │  Web   │   │ Mobile │   │ Tools  │               │
│    └────────┘   └────────┘   └────────┘               │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │           Amazon S3 (Snapshots)                 │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## SLIDE 12 - Avantages de la Solution

### Performance
- ⚡ Requêtes 10x plus rapides (indexes)
- ⚡ Scalabilité horizontale (sharding)
- ⚡ Batch processing efficace

### Sécurité
- 🔒 Chiffrement at rest & in transit
- 🔒 Authentification multi-niveaux
- 🔒 Audit trails complets
- 🔒 HIPAA ready

### Maintenabilité
- 🛠️ Infrastructure as Code (Docker)
- 🛠️ Tests automatisés
- 🛠️ Documentation complète
- 🛠️ Monitoring intégré

---

## SLIDE 13 - Roadmap & Prochaines Étapes

### Court terme (1-2 semaines)
- [ ] Déployer sur environnement de test
- [ ] Valider performances avec client
- [ ] Configurer monitoring

### Moyen terme (1-2 mois)
- [ ] Migration production
- [ ] Formation équipe client
- [ ] Mise en place backups

### Long terme (3-6 mois)
- [ ] Migration vers cloud AWS
- [ ] Sharding si volume augmente
- [ ] Analytics avancés (aggregation)

---

## SLIDE 14 - Investissement

### Développement (réalisé)
- Analyse & architecture : ✅
- Script migration : ✅
- Docker + tests : ✅
- Documentation : ✅

### Infrastructure (mensuel)
| Phase | Solution | Coût |
|-------|----------|------|
| Test | Docker local | 0€ |
| Production | MongoDB Atlas | ~485€ |
| Optimisé | EC2 + Docker | ~180€ |

---

## SLIDE 15 - Questions & Discussion

### Récapitulatif
✅ Architecture scalable et cloud-ready  
✅ Migration automatisée et testée  
✅ Sécurité renforcée (RBAC + auth)  
✅ Plan de déploiement AWS détaillé  

### Contact
📧 **Questions techniques** : Équipe Data Engineering  
📊 **Démonstration** : Script + Docker disponibles  
☁️ **Cloud** : Architecture AWS flexible

---

**Merci pour votre attention !**

*Des questions ?*
