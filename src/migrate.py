#!/usr/bin/env python3
"""
Script de migration Healthcare Dataset vers MongoDB
Validation des données, insertion par batch, création d'indexes
"""

import csv
import os
import sys
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dateutil import parser as date_parser

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure, BulkWriteError

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration MongoDB
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', 'localhost'),
    'port': int(os.getenv('MONGO_PORT', '27017')),
    'username': os.getenv('MONGO_USER', 'migrate_user'),
    'password': os.getenv('MONGO_PASSWORD', 'migrate_pass'),
    'auth_db': os.getenv('MONGO_AUTH_DB', 'healthcare'),
    'database': os.getenv('MONGO_DB', 'healthcare'),
    'collection': 'patients'
}

CSV_PATH = os.getenv('CSV_PATH', '/app/data/healthcare_dataset.csv')
BATCH_SIZE = 1000


class DataValidator:
    """Validation des données médicales"""
    
    VALID_BLOOD_TYPES = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
    VALID_GENDERS = {'Male', 'Female'}
    VALID_ADMISSION_TYPES = {'Elective', 'Emergency', 'Urgent'}
    VALID_TEST_RESULTS = {'Normal', 'Abnormal', 'Inconclusive'}
    VALID_CONDITIONS = {'Cancer', 'Obesity', 'Diabetes', 'Asthma', 'Hypertension', 'Arthritis'}
    
    @classmethod
    def validate_patient(cls, row: Dict) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Valide une ligne de données patient
        Returns: (is_valid, error_message, cleaned_data)
        """
        errors = []
        
        # Validation Age
        try:
            age = int(row['Age'])
            if not (0 <= age <= 120):
                errors.append(f"Age invalide: {age}")
        except ValueError:
            errors.append(f"Age non numérique: {row['Age']}")
            age = None
        
        # Validation Genre
        gender = row['Gender']
        if gender not in cls.VALID_GENDERS:
            errors.append(f"Genre invalide: {gender}")
        
        # Validation Groupe sanguin
        blood_type = row['Blood Type']
        if blood_type not in cls.VALID_BLOOD_TYPES:
            errors.append(f"Groupe sanguin invalide: {blood_type}")
        
        # Validation Condition médicale
        condition = row['Medical Condition']
        if condition not in cls.VALID_CONDITIONS:
            errors.append(f"Condition invalide: {condition}")
        
        # Validation Type d'admission
        admission_type = row['Admission Type']
        if admission_type not in cls.VALID_ADMISSION_TYPES:
            errors.append(f"Type d'admission invalide: {admission_type}")
        
        # Validation Résultats tests
        test_results = row['Test Results']
        if test_results not in cls.VALID_TEST_RESULTS:
            errors.append(f"Résultat test invalide: {test_results}")
        
        # Validation dates
        try:
            admission_date = date_parser.parse(row['Date of Admission']).date()
        except (ValueError, TypeError):
            errors.append(f"Date d'admission invalide: {row['Date of Admission']}")
            admission_date = None
        
        try:
            discharge_date = date_parser.parse(row['Discharge Date']).date()
        except (ValueError, TypeError):
            errors.append(f"Date de sortie invalide: {row['Discharge Date']}")
            discharge_date = None
        
        # Validation montant
        try:
            billing_amount = float(row['Billing Amount'])
            if billing_amount < 0:
                errors.append(f"Montant négatif: {billing_amount}")
        except ValueError:
            errors.append(f"Montant invalide: {row['Billing Amount']}")
            billing_amount = None
        
        # Validation numéro chambre
        try:
            room_number = int(row['Room Number'])
        except ValueError:
            errors.append(f"Numéro chambre invalide: {row['Room Number']}")
            room_number = None
        
        if errors:
            return False, "; ".join(errors), None
        
        # Création du document nettoyé
        cleaned_data = {
            'patient_id': cls._generate_patient_id(row),
            'name': row['Name'].strip(),
            'age': age,
            'gender': gender,
            'blood_type': blood_type,
            'medical_condition': condition,
            'admission': {
                'date': datetime.combine(admission_date, datetime.min.time()),
                'type': admission_type,
                'room_number': room_number
            },
            'discharge_date': datetime.combine(discharge_date, datetime.min.time()),
            'doctor': row['Doctor'].strip(),
            'hospital': row['Hospital'].strip(),
            'insurance_provider': row['Insurance Provider'].strip(),
            'billing_amount': round(billing_amount, 2),
            'medication': row['Medication'].strip(),
            'test_results': test_results,
            'metadata': {
                'imported_at': datetime.utcnow(),
                'batch_id': None,
                'validation_status': 'valid'
            }
        }
        
        return True, None, cleaned_data
    
    @staticmethod
    def _generate_patient_id(row: Dict) -> str:
        """Génère un ID unique basé sur les données"""
        unique_string = f"{row['Name']}_{row['Age']}_{row['Date of Admission']}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]


class MongoDBMigration:
    """Gestion de la migration vers MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.stats = {
            'total_read': 0,
            'valid': 0,
            'invalid': 0,
            'duplicates': 0,
            'inserted': 0,
            'errors': 0
        }
    
    def connect(self) -> bool:
        """Établit la connexion à MongoDB"""
        try:
            uri = f"mongodb://{MONGO_CONFIG['username']}:{MONGO_CONFIG['password']}@" \
                  f"{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/{MONGO_CONFIG['auth_db']}?authSource=healthcare"
            
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            
            self.db = self.client[MONGO_CONFIG['database']]
            self.collection = self.db[MONGO_CONFIG['collection']]
            
            logger.info(f"✅ Connecté à MongoDB: {MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Connexion MongoDB échouée: {e}")
            return False
    
    def setup_indexes(self):
        """Crée les indexes nécessaires"""
        logger.info("📊 Création des indexes...")
        
        indexes = [
            {'keys': [('patient_id', ASCENDING)], 'unique': True, 'name': 'idx_patient_id'},
            {'keys': [('medical_condition', ASCENDING)], 'name': 'idx_condition'},
            {'keys': [('admission.date', DESCENDING)], 'name': 'idx_admission_date'},
            {'keys': [('hospital', ASCENDING)], 'name': 'idx_hospital'},
            {'keys': [('doctor', ASCENDING)], 'name': 'idx_doctor'},
            {'keys': [('blood_type', ASCENDING)], 'name': 'idx_blood_type'},
        ]
        
        for idx_config in indexes:
            try:
                self.collection.create_index(
                    idx_config['keys'],
                    unique=idx_config.get('unique', False),
                    name=idx_config['name']
                )
                logger.info(f"   ✓ Index créé: {idx_config['name']}")
            except Exception as e:
                logger.warning(f"   ⚠️ Index {idx_config['name']}: {e}")
    
    def migrate(self, csv_path: str) -> Dict:
        """Exécute la migration complète"""
        logger.info(f"🚀 Début migration: {csv_path}")
        start_time = datetime.now()
        
        if not os.path.exists(csv_path):
            logger.error(f"❌ Fichier non trouvé: {csv_path}")
            return self.stats
        
        batch = []
        batch_id = 0
        seen_ids = set()
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                self.stats['total_read'] += 1
                
                # Validation
                is_valid, error, cleaned_data = DataValidator.validate_patient(row)
                
                if not is_valid:
                    self.stats['invalid'] += 1
                    logger.debug(f"Ligne invalide: {error}")
                    continue
                
                # Check doublons
                if cleaned_data['patient_id'] in seen_ids:
                    self.stats['duplicates'] += 1
                    continue
                
                seen_ids.add(cleaned_data['patient_id'])
                cleaned_data['metadata']['batch_id'] = batch_id
                batch.append(cleaned_data)
                self.stats['valid'] += 1
                
                # Insertion par batch
                if len(batch) >= BATCH_SIZE:
                    self._insert_batch(batch, batch_id)
                    batch = []
                    batch_id += 1
                    
                    if self.stats['valid'] % 5000 == 0:
                        logger.info(f"   Progression: {self.stats['valid']} patients traités...")
            
            # Dernier batch
            if batch:
                self._insert_batch(batch, batch_id)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("\n" + "="*50)
        logger.info("📊 RÉSULTATS DE LA MIGRATION")
        logger.info("="*50)
        logger.info(f"📁 Total lu:           {self.stats['total_read']:,}")
        logger.info(f"✅ Validés:            {self.stats['valid']:,}")
        logger.info(f"❌ Invalides:          {self.stats['invalid']:,}")
        logger.info(f"🔁 Doublons ignorés:   {self.stats['duplicates']:,}")
        logger.info(f"💾 Insérés:            {self.stats['inserted']:,}")
        logger.info(f"⏱️  Durée:             {duration:.2f}s")
        logger.info(f"🚀 Débit:              {self.stats['inserted']/duration:.0f} docs/s")
        logger.info("="*50)
        
        return self.stats
    
    def _insert_batch(self, batch: List[Dict], batch_id: int):
        """Insère un batch de documents"""
        try:
            result = self.collection.insert_many(batch, ordered=False)
            self.stats['inserted'] += len(result.inserted_ids)
        except BulkWriteError as e:
            # Gère les doublons détectés par l'index unique
            write_errors = e.details.get('writeErrors', [])
            inserted = e.details.get('nInserted', 0)
            self.stats['inserted'] += inserted
            self.stats['duplicates'] += len(write_errors)
        except Exception as e:
            logger.error(f"❌ Erreur batch {batch_id}: {e}")
            self.stats['errors'] += len(batch)
    
    def verify_migration(self) -> bool:
        """Vérifie l'intégrité post-migration"""
        logger.info("\n🔍 Vérification post-migration...")
        
        checks = {
            'count': self.collection.count_documents({}),
            'indexes': len(self.collection.list_indexes().to_list()),
            'conditions': len(self.collection.distinct('medical_condition')),
            'blood_types': len(self.collection.distinct('blood_type')),
            'avg_billing': None
        }
        
        # Calcul moyenne billing
        pipeline = [{'$group': {'_id': None, 'avg': {'$avg': '$billing_amount'}}}]
        avg_result = list(self.collection.aggregate(pipeline))
        checks['avg_billing'] = avg_result[0]['avg'] if avg_result else 0
        
        logger.info(f"   ✓ Documents: {checks['count']:,}")
        logger.info(f"   ✓ Indexes: {checks['indexes']}")
        logger.info(f"   ✓ Conditions: {checks['conditions']}")
        logger.info(f"   ✓ Blood types: {checks['blood_types']}")
        logger.info(f"   ✓ Billing moyen: ${checks['avg_billing']:,.2f}")
        
        return checks['count'] == self.stats['inserted']
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            logger.info("🔌 Connexion MongoDB fermée")


def main():
    """Point d'entrée principal"""
    logger.info("🏥 HEALTHCARE MONGODB MIGRATION")
    logger.info("="*50)
    
    migration = MongoDBMigration()
    
    # Connexion
    if not migration.connect():
        sys.exit(1)
    
    # Setup indexes
    migration.setup_indexes()
    
    # Migration
    stats = migration.migrate(CSV_PATH)
    
    # Vérification
    if migration.verify_migration():
        logger.info("\n✅ Migration réussie! Toutes les vérifications OK.")
    else:
        logger.warning("\n⚠️  Vérifications post-migration: écarts détectés")
    
    migration.close()


if __name__ == '__main__':
    main()
