#!/usr/bin/env python3
"""Import du dataset healthcare vers MongoDB Atlas avec déduplication"""

import csv
import hashlib
import os
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_ATLAS_URI")
CSV_PATH = os.getenv("CSV_PATH", "data/healthcare_dataset.csv")
BATCH_SIZE = 1000


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


def main():
    client = MongoClient(MONGO_URI)
    db = client["healthcare"]
    collection = db["patients"]

    # Nettoyage complet (supprime aussi les index)
    collection.drop()
    collection = db["patients"]

    # Index unique pour empêcher les doublons
    collection.create_index('patient_id', unique=True)

    # Lecture et insertion
    batch = []
    seen_ids = set()
    total = 0
    duplicates = 0
    inserted = 0

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            doc = transform_row(row)

            if doc['patient_id'] in seen_ids:
                duplicates += 1
                continue

            seen_ids.add(doc['patient_id'])
            batch.append(doc)

            if len(batch) >= BATCH_SIZE:
                try:
                    result = collection.insert_many(batch, ordered=False)
                    inserted += len(result.inserted_ids)
                except BulkWriteError as e:
                    inserted += e.details.get('nInserted', 0)
                batch = []

        if batch:
            try:
                result = collection.insert_many(batch, ordered=False)
                inserted += len(result.inserted_ids)
            except BulkWriteError as e:
                inserted += e.details.get('nInserted', 0)

    count = collection.count_documents({})
    print(f"Total lu: {total}, Doublons: {duplicates}, Insérés: {inserted}, En base: {count}")

    client.close()


if __name__ == '__main__':
    main()
