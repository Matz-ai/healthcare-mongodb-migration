#!/usr/bin/env python3
"""
Script de migration Healthcare Dataset (CSV → MongoDB)
- Détection des doublons
- Insertion par batch
- Vérification post-migration
"""

import csv
import os
import hashlib
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError

# Configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_USER = os.getenv('MONGO_USER', 'migrate_user')
MONGO_PASS = os.getenv('MONGO_PASSWORD', 'migrate_pass')
MONGO_DB = os.getenv('MONGO_DB', 'healthcare')
CSV_PATH = os.getenv('CSV_PATH', '/app/data/healthcare_dataset.csv')
BATCH_SIZE = 1000


def connect():
    """Connexion à MongoDB"""
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=healthcare"
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connecté à MongoDB")
    return client


def generate_id(row):
    """Génère un ID unique pour détecter les doublons"""
    unique = f"{row['Name']}_{row['Age']}_{row['Date of Admission']}"
    return hashlib.md5(unique.encode()).hexdigest()[:12]


def transform_row(row):
    """Transforme une ligne CSV en document MongoDB"""
    return {
        'patient_id': generate_id(row),
        'name': row['Name'].strip(),
        'age': int(row['Age']),
        'gender': row['Gender'],
        'blood_type': row['Blood Type'],
        'medical_condition': row['Medical Condition'],
        'admission_date': row['Date of Admission'],
        'admission_type': row['Admission Type'],
        'discharge_date': row['Discharge Date'],
        'room_number': int(row['Room Number']),
        'doctor': row['Doctor'].strip(),
        'hospital': row['Hospital'].strip(),
        'insurance_provider': row['Insurance Provider'].strip(),
        'billing_amount': round(float(row['Billing Amount']), 2),
        'medication': row['Medication'],
        'test_results': row['Test Results']
    }


def migrate(collection, csv_path):
    """Lit le CSV, dédoublonne et insère par batch"""
    # Index unique pour empêcher les doublons côté MongoDB aussi
    collection.create_index('patient_id', unique=True, name='idx_patient_id')

    batch = []
    seen_ids = set()
    total = 0
    duplicates = 0
    inserted = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total += 1
            doc = transform_row(row)

            # Détection doublon
            if doc['patient_id'] in seen_ids:
                duplicates += 1
                continue

            seen_ids.add(doc['patient_id'])
            batch.append(doc)

            # Insertion par paquet
            if len(batch) >= BATCH_SIZE:
                inserted += insert_batch(collection, batch)
                batch = []

                if total % 5000 == 0:
                    print(f"   ⏳ {total} lignes traitées...")

        # Dernier paquet
        if batch:
            inserted += insert_batch(collection, batch)

    print(f"\n📊 Résultats :")
    print(f"   Total lu :     {total}")
    print(f"   Doublons :     {duplicates}")
    print(f"   Insérés :      {inserted}")

    return total, duplicates, inserted


def insert_batch(collection, batch):
    """Insère un paquet de documents, ignore les doublons"""
    try:
        result = collection.insert_many(batch, ordered=False)
        return len(result.inserted_ids)
    except BulkWriteError as e:
        return e.details.get('nInserted', 0)


def verify(collection, expected):
    """Vérifie que la migration s'est bien passée"""
    count = collection.count_documents({})
    print(f"\n🔍 Vérification :")
    print(f"   Documents en base : {count}")
    print(f"   Attendu :           {expected}")

    if count == expected:
        print("   ✅ Migration OK !")
    else:
        print("   ⚠️  Écart détecté")

    return count == expected


def main():
    print("🏥 Migration Healthcare → MongoDB")
    print("=" * 40)

    client = connect()
    db = client[MONGO_DB]
    collection = db['patients']

    total, duplicates, inserted = migrate(collection, CSV_PATH)
    verify(collection, inserted)

    client.close()
    print("\n🔌 Connexion fermée")


if __name__ == '__main__':
    main()
