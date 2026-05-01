// Initialisation MongoDB - Création des utilisateurs
// Exécuté automatiquement au premier démarrage du container
// Les mots de passe sont passés via variables d'environnement

db = db.getSiblingDB('healthcare');

// Récupération des mots de passe depuis les variables d'environnement
var migratePassword = process.env.MONGO_PASSWORD || 'changeme';
var readonlyPassword = process.env.MONGO_READONLY_PASSWORD || 'changeme';

// Utilisateur de migration (lecture/écriture + administration DB)
db.createUser({
    user: "migrate_user",
    pwd: migratePassword,
    roles: [
        { role: "readWrite", db: "healthcare" },
        { role: "dbAdmin", db: "healthcare" }
    ]
});

// Utilisateur lecture seule (consultation)
db.createUser({
    user: "readonly_user",
    pwd: readonlyPassword,
    roles: [
        { role: "read", db: "healthcare" }
    ]
});

print("Users créés avec succès");
