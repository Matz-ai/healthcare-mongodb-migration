#!/usr/bin/env python3
"""
Tests unitaires pour la migration MongoDB
"""

import pytest
import os
import sys
from datetime import datetime

# Ajoute le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from migrate import DataValidator, MongoDBMigration


class TestDataValidator:
    """Tests de validation des données"""
    
    def test_valid_patient(self):
        """Test une ligne valide"""
        row = {
            'Name': 'John Doe',
            'Age': '45',
            'Gender': 'Male',
            'Blood Type': 'A+',
            'Medical Condition': 'Diabetes',
            'Date of Admission': '2024-01-15',
            'Doctor': 'Dr. Smith',
            'Hospital': 'General Hospital',
            'Insurance Provider': 'Blue Cross',
            'Billing Amount': '12345.67',
            'Room Number': '101',
            'Admission Type': 'Elective',
            'Discharge Date': '2024-01-20',
            'Medication': 'Insulin',
            'Test Results': 'Normal'
        }
        
        is_valid, error, data = DataValidator.validate_patient(row)
        
        assert is_valid is True
        assert error is None
        assert data is not None
        assert data['name'] == 'John Doe'
        assert data['age'] == 45
        assert data['gender'] == 'Male'
    
    def test_invalid_age(self):
        """Test âge invalide"""
        row = {
            'Name': 'Test',
            'Age': 'invalid',
            'Gender': 'Male',
            'Blood Type': 'A+',
            'Medical Condition': 'Diabetes',
            'Date of Admission': '2024-01-15',
            'Doctor': 'Dr. X',
            'Hospital': 'Hospital',
            'Insurance Provider': 'Insurance',
            'Billing Amount': '1000',
            'Room Number': '101',
            'Admission Type': 'Elective',
            'Discharge Date': '2024-01-20',
            'Medication': 'Med',
            'Test Results': 'Normal'
        }
        
        is_valid, error, data = DataValidator.validate_patient(row)
        
        assert is_valid is False
        assert 'Age' in error or 'non numérique' in error
    
    def test_invalid_gender(self):
        """Test genre invalide"""
        row = {
            'Name': 'Test',
            'Age': '30',
            'Gender': 'Invalid',
            'Blood Type': 'A+',
            'Medical Condition': 'Diabetes',
            'Date of Admission': '2024-01-15',
            'Doctor': 'Dr. X',
            'Hospital': 'Hospital',
            'Insurance Provider': 'Insurance',
            'Billing Amount': '1000',
            'Room Number': '101',
            'Admission Type': 'Elective',
            'Discharge Date': '2024-01-20',
            'Medication': 'Med',
            'Test Results': 'Normal'
        }
        
        is_valid, error, data = DataValidator.validate_patient(row)
        
        assert is_valid is False
        assert 'Genre' in error
    
    def test_invalid_blood_type(self):
        """Test groupe sanguin invalide"""
        row = {
            'Name': 'Test',
            'Age': '30',
            'Gender': 'Male',
            'Blood Type': 'Z+',
            'Medical Condition': 'Diabetes',
            'Date of Admission': '2024-01-15',
            'Doctor': 'Dr. X',
            'Hospital': 'Hospital',
            'Insurance Provider': 'Insurance',
            'Billing Amount': '1000',
            'Room Number': '101',
            'Admission Type': 'Elective',
            'Discharge Date': '2024-01-20',
            'Medication': 'Med',
            'Test Results': 'Normal'
        }
        
        is_valid, error, data = DataValidator.validate_patient(row)
        
        assert is_valid is False
        assert 'sanguin' in error


class TestMongoDBMigration:
    """Tests de la classe de migration"""
    
    @pytest.fixture
    def migration(self):
        """Fixture pour créer une instance de migration"""
        return MongoDBMigration()
    
    def test_initialization(self, migration):
        """Test l'initialisation"""
        assert migration.client is None
        assert migration.db is None
        assert migration.collection is None
        assert migration.stats['total_read'] == 0
    
    def test_stats_structure(self, migration):
        """Test la structure des stats"""
        expected_keys = ['total_read', 'valid', 'invalid', 'duplicates', 'inserted', 'errors']
        for key in expected_keys:
            assert key in migration.stats


def test_environment_variables():
    """Test que les variables d'environnement sont définies (ou valeurs par défaut)"""
    from migrate import MONGO_CONFIG
    
    assert 'host' in MONGO_CONFIG
    assert 'port' in MONGO_CONFIG
    assert 'username' in MONGO_CONFIG
    assert 'password' in MONGO_CONFIG
    assert 'database' in MONGO_CONFIG


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
