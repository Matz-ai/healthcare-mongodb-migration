// Initialisation MongoDB - Création users, roles et indexes
// Exécuté automatiquement au premier démarrage du container

db = db.getSiblingDB('healthcare');

// Création des rôles personnalisés (si besoin spécifique)
db.createRole({
    role: "dataValidator",
    privileges: [
        {
            resource: { db: "healthcare", collection: "patients" },
            actions: ["find", "insert", "update", "remove", "createIndex"]
        }
    ],
    roles: []
});

// Création de l'utilisateur de migration (readWrite)
db.createUser({
    user: "migrate_user",
    pwd: "migrate_pass",
    roles: [
        { role: "readWrite", db: "healthcare" },
        { role: "dbAdmin", db: "healthcare" }
    ]
});

// Création de l'utilisateur lecture seule
db.createUser({
    user: "readonly_user",
    pwd: "readonly_pass",
    roles: [
        { role: "read", db: "healthcare" }
    ]
});

// Création de l'utilisateur analyste (lecture + création d'indexes)
db.createUser({
    user: "analyst_user",
    pwd: "analyst_pass",
    roles: [
        { role: "read", db: "healthcare" },
        { role: "readWrite", db: "healthcare", collection: "analysis_results" }
    ]
});

print("✅ Users créés avec succès");
print("   - migrate_user (readWrite + dbAdmin)");
print("   - readonly_user (read)");
print("   - analyst_user (read + write analysis_results)");
