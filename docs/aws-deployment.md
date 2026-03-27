# Déploiement MongoDB sur AWS — Étude comparative

## Objectif

Documenter les options disponibles pour héberger MongoDB sur AWS dans le cadre du projet de migration healthcare, couvrant les services managés, le stockage, la conteneurisation, les sauvegardes et les coûts.

---

## 1. Amazon S3

**Rôle** : Stockage objet pour les données brutes, backups et exports.

S3 n'est pas une base de données mais joue un rôle clé dans l'écosystème de données :

| Utilisation | Description |
|---|---|
| **Stockage CSV source** | Héberger le dataset d'origine (8 Mo) de manière durable |
| **Backups MongoDB** | Stocker les dumps `mongodump` ou snapshots automatiques |
| **Exports analytiques** | Exporter des résultats d'agrégation pour d'autres outils BI |
| **Logs d'audit** | Archiver les logs d'accès pour conformité HIPAA |

**Classes de stockage recommandées** :
- `S3 Standard` : Pour les backups récents (accès fréquent)
- `S3 Glacier` : Pour les archives long terme (rétention HIPAA 7 ans)

**Coût estimé** : ~0.023 $/Go/mois (Standard), ~0.004 $/Go/mois (Glacier)

---

## 2. Amazon DocumentDB (compatible MongoDB)

**Description** : Service de base de données managé par AWS, compatible avec l'API MongoDB (jusqu'à la version 5.0).

| Avantages | Inconvénients |
|---|---|
| Fully managed (pas de maintenance serveur) | Compatibilité MongoDB partielle |
| Haute disponibilité multi-AZ intégrée | Aggregation pipeline limitée |
| Backup automatique (jusqu'à 35 jours) | Pas de sharding natif |
| Intégration native AWS (IAM, CloudWatch) | Version MongoDB en retard |
| HIPAA eligible | Coût plus élevé qu'un self-hosted |

> **Note** : Amazon RDS ne supporte **pas** MongoDB nativement. RDS est conçu pour les bases relationnelles (MySQL, PostgreSQL, etc.). Pour un équivalent managé MongoDB sur AWS, la solution officielle est **DocumentDB** ou **MongoDB Atlas** hébergé sur infrastructure AWS.

**Coût estimé** (instance `db.r5.large`, multi-AZ) :

| Ressource | Coût mensuel |
|---|---|
| Instance (2 nœuds) | ~280 € |
| Stockage (50 Go) | ~5 € |
| I/O | ~15 € |
| **Total** | **~300 €/mois** |

---

## 3. Amazon ECS — MongoDB conteneurisé

**Description** : Déploiement de MongoDB dans des conteneurs Docker orchestrés par ECS (Elastic Container Service), reproduisant l'architecture locale du projet.

### Architecture proposée

```
┌──────────────────────────────────────────────┐
│              Amazon ECS Cluster              │
├──────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────────┐  │
│  │  Task MongoDB  │  │  Task Migration    │  │
│  │  (mongo:7.0)   │  │  (python:3.11)     │  │
│  │  Port 27017    │  │  Script migrate.py │  │
│  └───────┬────────┘  └────────────────────┘  │
│          │                                    │
│  ┌───────┴────────┐                          │
│  │  EBS Volume    │  (persistance données)   │
│  └────────────────┘                          │
└──────────────────────────────────────────────┘
```

| Avantages | Inconvénients |
|---|---|
| Même `docker-compose.yml` qu'en local | Complexité opérationnelle |
| Scalabilité automatique (Fargate) | Gestion stateful containers délicate |
| Intégration CI/CD avec ECR | Expertise ECS/Fargate requise |
| Portable et reproductible | Monitoring à configurer manuellement |

**Mode de lancement recommandé** : **Fargate** (serverless, pas de gestion d'instances EC2)

**Coût estimé** (Fargate, 2 vCPU, 4 Go RAM) :

| Ressource | Coût mensuel |
|---|---|
| Compute Fargate | ~120 € |
| Stockage EBS (50 Go) | ~5 € |
| NAT Gateway | ~35 € |
| **Total** | **~160 €/mois** |

---

## 4. Sauvegardes et surveillance

### Stratégie de sauvegarde

| Méthode | Fréquence | Rétention | Stockage |
|---|---|---|---|
| Snapshots automatiques (DocumentDB) | Quotidien | 35 jours | Inclus |
| `mongodump` planifié (ECS) | Quotidien | 90 jours | S3 Standard |
| Export CSV archivage | Mensuel | 7 ans (HIPAA) | S3 Glacier |

### Surveillance avec CloudWatch

| Métrique | Seuil d'alerte | Action |
|---|---|---|
| CPU utilisation | > 80 % | Scale up instance |
| Connexions actives | > 500 | Vérifier les connexions orphelines |
| Espace disque | > 85 % | Augmenter le volume EBS |
| Latence requêtes | > 100 ms | Vérifier les indexes |
| Réplication lag | > 10 s | Vérifier la santé du replica set |

**Outils de surveillance** :
- **CloudWatch** : Métriques infrastructure et alertes SNS
- **MongoDB Atlas** (si Atlas) : Dashboard intégré avec Performance Advisor
- **CloudTrail** : Audit des accès API pour conformité HIPAA

---

## 5. Tarifications AWS — Synthèse comparative

| Solution | Type | Coût mensuel | Maintenance | Recommandé pour |
|---|---|---|---|---|
| **DocumentDB** | Managé | ~300 € | Faible | Équipe réduite, besoins simples |
| **MongoDB Atlas sur AWS** | DBaaS | ~450 € | Nulle | Besoin features MongoDB complètes |
| **ECS + Fargate** | Conteneur | ~160 € | Moyenne | Architecture microservices existante |
| **EC2 self-hosted** | Manuel | ~150 € | Élevée | Budget serré, équipe ops expérimentée |

### Détail des coûts cachés à anticiper

| Poste | Estimation |
|---|---|
| Data transfer sortant | ~0.09 $/Go après 1 Go gratuit |
| Backup S3 (100 Go) | ~2.30 $/mois |
| CloudWatch Logs | ~0.50 $/Go ingéré |
| NAT Gateway | ~35 $/mois (si VPC privé) |

---

## Recommandation

Pour ce projet healthcare, **MongoDB Atlas sur AWS** est la solution recommandée :

1. **HIPAA compliance** certifiée nativement
2. **Zéro maintenance** — l'équipe se concentre sur le métier
3. **Backup continu** avec point-in-time recovery
4. **Sharding automatique** si le volume de données augmente
5. **Monitoring intégré** sans configuration supplémentaire

**Alternative budget** : ECS + Fargate (~160 €/mois) avec backups `mongodump` vers S3, acceptable si l'équipe a les compétences DevOps.

---

## Références

- [Amazon DocumentDB](https://aws.amazon.com/documentdb/)
- [Amazon ECS](https://aws.amazon.com/ecs/)
- [Tarification S3](https://aws.amazon.com/s3/pricing/)

.
