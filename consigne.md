# Résumé de mission — Migration de données médicales vers MongoDB

## Contexte

Un client dispose d'un dataset de données médicales de patients (format CSV). Il rencontre des problèmes de scalabilité et souhaite migrer vers une solution Big Data scalable horizontalement. La mission consiste à orchestrer cette migration vers MongoDB via Docker, puis à documenter les options de déploiement cloud sur AWS.

---

## Livrables attendus

### 1. Script de migration des données

Un script Python qui transfère automatiquement les données du fichier CSV vers une base de données MongoDB. Ce script doit inclure des tests d'intégrité des données (colonnes, types, doublons, valeurs manquantes) avant et après la migration. Les tests doivent être automatisés.

### 2. Conteneurisation avec Docker

Un fichier `docker-compose.yml` permettant de déployer MongoDB et le script de migration dans des conteneurs distincts. La configuration doit utiliser au minimum deux volumes : un pour le fichier CSV source, un pour la base de données MongoDB. L'ensemble doit être portable et fonctionnel.

### 3. Documentation GitHub (README)

Un README détaillé publié sur le dépôt GitHub du projet, contenant :
- La logique et le fonctionnement du script de migration
- Le schéma de la base de données MongoDB
- La description du système d'authentification et des rôles utilisateurs créés

Un fichier `requirements.txt` listant toutes les dépendances Python nécessaires avec leurs versions.

### 4. Recherches sur le déploiement AWS

Une documentation (sans déploiement réel) sur les options disponibles pour héberger MongoDB sur AWS, couvrant :
- Amazon S3
- Amazon RDS pour MongoDB et Amazon DocumentDB
- Amazon ECS (déploiement MongoDB dans un conteneur Docker)
- La configuration des sauvegardes et de la surveillance
- Les tarifications AWS

### 5. Présentation PowerPoint

Une présentation destinée au client couvrant :
- Le contexte de la mission
- La démarche technique complète (de la migration aux recherches cloud)
- La justification des choix techniques effectués

---

## Contraintes et exigences

- Le travail doit être versionné sur GitHub.
- La base MongoDB doit être accessible et fonctionnelle depuis les conteneurs Docker.
- Le schéma de la base de données doit respecter les types des champs et inclure des index pertinents.
- La migration doit pouvoir être démontrée en live.
