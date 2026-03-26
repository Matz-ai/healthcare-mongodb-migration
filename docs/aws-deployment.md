# Déploiement MongoDB sur AWS

## 🎯 Objectif

Identifier la meilleure solution pour déployer MongoDB sur AWS pour notre client healthcare, en considérant :
- Scalabilité horizontale
- Haute disponibilité
- Sécurité des données médicales (HIPAA)
- Coût optimisé

---

## 📊 Comparaison des Options

### 1. Amazon DocumentDB

**Description** : Service managé compatible MongoDB (sous-ensemble de fonctionnalités)

| Avantages | Inconvénients |
|-----------|---------------|
| ✅ Fully managed (pas de maintenance) | ❌ Compatibilité partielle avec MongoDB |
| ✅ HA intégrée (multi-AZ) | ❌ Pas d'aggregation pipeline complète |
| ✅ Backup automatique | ❌ Coût plus élevé |
| ✅ Intégration AWS native | ❌ Pas de sharding natif |
| ✅ HIPAA eligible | ❌ Version MongoDB souvent en retard |

**Use case** : Applications simples, compatibilité MongoDB non critique

**Coût estimé** (db.r5.large, multi-AZ) : ~300-400€/mois

---

### 2. MongoDB Atlas sur AWS

**Description** : Service DBaaS officiel MongoDB, hébergé sur AWS

| Avantages | Inconvénients |
|-----------|---------------|
| ✅ MongoDB 100% natif | ❌ Vendor lock-in MongoDB |
| ✅ Toutes les fonctionnalités | ❌ Coût élevé |
| ✅ Sharding automatique | ❌ Dépendance tierce |
| ✅ Monitoring avancé | ❌ Moins d'intégration AWS native |
| ✅ HIPAA compliant | |
| ✅ Global clusters | |

**Use case** : Applications complexes, besoin features MongoDB avancées

**Coût estimé** (M10, 3 nodes) : ~400-600€/mois

---

### 3. Amazon EC2 + MongoDB Self-Hosted

**Description** : Installation MongoDB manuelle sur instances EC2

| Avantages | Inconvénients |
|-----------|---------------|
| ✅ Contrôle total | ❌ Maintenance manuelle (patches, backups) |
| ✅ MongoDB 100% natif | ❌ Configuration HA complexe |
| ✅ Coût maîtrisé | ❌ Expertise ops nécessaire |
| ✅ Flexible | ❌ Temps d'ingénierie important |
| ✅ Docker-friendly | ❌ Monitoring à configurer |

**Use case** : Équipe technique expérimentée, contrôle total requis

**Coût estimé** (3x t3.medium, EBS, ELB) : ~150-250€/mois

---

### 4. Amazon ECS/EKS + MongoDB (Containers)

**Description** : MongoDB conteneurisé avec orchestration AWS

| Avantages | Inconvénients |
|-----------|---------------|
| ✅ Scalabilité automatique | ❌ Complexité opérationnelle |
| ✅ Infrastructure as Code | ❌ Stateful containers = complexe |
| ✅ Intégration CI/CD | ❌ Expertise Kubernetes/ECS |
| ✅ Portable | ❌ Coût de l'orchestrateur |
| ✅ Docker natif | |

**Use case** : Architecture microservices, DevOps mature

**Coût estimé** (ECS Fargate + EBS) : ~200-350€/mois

---

## 🏆 Recommandation

### Pour ce client Healthcare : **MongoDB Atlas sur AWS**

**Justification** :

1. **Sécurité** : HIPAA compliance certifiée, chiffrement end-to-end
2. **Simplicité** : Pas de maintenance Ops, l'équipe se concentre sur le métier
3. **Scalabilité** : Sharding automatique quand le volume augmentera
4. **Backup** : Point-in-time recovery inclus
5. **Support** : Support MongoDB professionnel

**Architecture recommandée** :

```
┌─────────────────────────────────────────────────────────┐
│                     AWS CLOUD                          │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐ │
│  │              MongoDB Atlas Cluster                │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │ │
│  │  │ Primary  │  │ Secondary│  │ Secondary│        │ │
│  │  │ eu-west-1│  │ eu-west-1│  │ eu-west-1│        │ │
│  │  └──────────┘  └──────────┘  └──────────┘        │ │
│  │         │              │              │           │ │
│  │         └──────────────┼──────────────┘           │ │
│  │                        │                          │ │
│  │                   ┌────┴────┐                     │ │
│  │                   │  ARBITER │                     │ │
│  │                   └─────────┘                     │ │
│  └───────────────────────────────────────────────────┘ │
│                          │                              │
│              ┌───────────┼───────────┐                  │
│              ▼           ▼           ▼                  │
│        ┌─────────┐ ┌─────────┐ ┌─────────┐             │
│        │  App 1  │ │  App 2  │ │  App 3  │             │
│        │ (EC2)   │ │ (ECS)   │ │ (Lambda)│             │
│        └─────────┘ └─────────┘ └─────────┘             │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │              AMAZON S3 (Backups)                  │ │
│  │         • Snapshots Atlas                         │ │
│  │         • Exports CSV                             │ │
│  │         • Logs d'audit                            │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Plan de Migration vers le Cloud

### Phase 1 : Préparation (1 semaine)
- [ ] Créer compte MongoDB Atlas
- [ ] Configurer VPC peering avec AWS
- [ ] Définir règles de sécurité (IP whitelist)
- [ ] Configurer encryption at rest

### Phase 2 : Déploiement (3 jours)
- [ ] Créer cluster M10 (3 nodes)
- [ ] Configurer replication (multi-AZ)
- [ ] Activer backup continu
- [ ] Créer users/roles

### Phase 3 : Migration données (1 semaine)
- [ ] Export données locales
- [ ] Import vers Atlas (mongodump/mongorestore)
- [ ] Vérifier intégrité
- [ ] Tests de performance

### Phase 4 : Cutover (1 jour)
- [ ] Basculer applications
- [ ] Vérifier connexions
- [ ] Monitorer métriques

---

## 💰 Estimation des Coûts (mensuel)

| Ressource | Config | Coût |
|-----------|--------|------|
| MongoDB Atlas | M10 (3 nodes) | ~450€ |
| Data Transfer | 100GB/mois | ~10€ |
| Backup Storage | 50GB | ~5€ |
| CloudWatch Logs | Standard | ~20€ |
| **TOTAL** | | **~485€/mois** |

---

## 🔒 Considérations Sécurité

### HIPAA Compliance
- ✅ MongoDB Atlas certifié HIPAA
- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Audit logs conservés 7 ans
- ✅ BAAs (Business Associate Agreements) disponibles

### Configuration Recommandée
```javascript
// Network Security
IP Whitelist: ["VPC CIDR", "Bureau IP"]
VPC Peering: Enabled
Private Endpoints: Enabled

// Encryption
Encryption at Rest: AWS KMS
Encryption in Transit: TLS 1.3
Field Level Encryption: Pour PII

// Access Control
Database Access: SCRAM + X.509
LDAP/AD: Intégration possible
MFA: Obligatoire pour console
```

---

## 🚀 Alternative Économique : EC2 + Docker

Si le budget est contraint, cette architecture offre 60% d'économie :

```yaml
# docker-compose.prod.yml pour AWS EC2
version: '3.8'

services:
  mongo-primary:
    image: mongo:7.0
    command: mongod --replSet rs0 --bind_ip_all
    volumes:
      - mongo_primary:/data/db
    deploy:
      resources:
        limits:
          memory: 2G
    
  mongo-secondary:
    image: mongo:7.0
    command: mongod --replSet rs0 --bind_ip_all
    volumes:
      - mongo_secondary:/data/db
      
  mongo-arbiter:
    image: mongo:7.0
    command: mongod --replSet rs0 --bind_ip_all --port 27017
    volumes:
      - mongo_arbiter:/data/db
```

**Coût** : ~180€/mois (3x t3.medium + EBS)
**Inconvénient** : Maintenance manuelle requise

---

## 📚 Références

- [MongoDB Atlas on AWS](https://www.mongodb.com/atlas/aws)
- [Amazon DocumentDB](https://aws.amazon.com/documentdb/)
- [HIPAA on AWS](https://aws.amazon.com/compliance/hipaa/)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
