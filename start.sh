#!/bin/bash
# Script de démarrage rapide

echo "🏥 Healthcare MongoDB Migration - Démarrage rapide"
echo "=================================================="

# Vérification Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi

echo "✅ Docker trouvé"
echo ""

# Démarrage MongoDB
echo "🚀 Démarrage de MongoDB..."
docker-compose up -d mongo

# Attente
echo "⏳ Attente initialisation (15s)..."
sleep 15

# Vérification
echo "🔍 Vérification du service..."
if docker-compose ps | grep -q "Up.*mongo"; then
    echo "✅ MongoDB est démarré"
else
    echo "❌ Problème avec MongoDB"
    docker-compose logs mongo
    exit 1
fi

echo ""
echo "📊 Lancement de la migration..."
docker-compose run --rm migration

echo ""
echo "✨ Terminé !"
echo ""
echo "Commandes utiles :"
echo "  - Voir les logs : docker-compose logs -f mongo"
echo "  - Shell MongoDB : docker-compose exec mongo mongosh -u migrate_user -p migrate_pass --authenticationDatabase healthcare"
echo "  - Arrêter : docker-compose down"
echo "  - Tests : docker-compose run --rm migration pytest src/test_migration.py -v"
