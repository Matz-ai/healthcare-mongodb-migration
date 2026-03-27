// Initialisation MongoDB - Création des utilisateurs
// Exécuté automatiquement au premier démarrage du container

db = db.getSiblingDB('healthcare');

// Utilisateur de migration (lecture/écriture + administration DB)
db.createUser({
    user: "migrate_user",
    pwd: "migrate_pass",
    roles: [
        { role: "readWrite", db: "healthcare" },
        { role: "dbAdmin", db: "healthcare" }
    ]
});

// Utilisateur lecture seule (consultation)
db.createUser({
    user: "readonly_user",
    pwd: "readonly_pass",
    roles: [
        { role: "read", db: "healthcare" }
    ]
});

print("✅ Users créés avec succès");
print("   - migrate_user (readWrite + dbAdmin)");
print("   - readonly_user (read)");
