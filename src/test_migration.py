#!/usr/bin/env python3
"""
Tests pour la migration MongoDB
"""

import pytest
from migrate import generate_id, transform_row


class TestTransformRow:
    """Test de la transformation CSV → document"""

    SAMPLE_ROW = {
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

    def test_transform_types(self):
        """Vérifie les types après transformation"""
        doc = transform_row(self.SAMPLE_ROW)
        assert isinstance(doc['age'], int)
        assert isinstance(doc['billing_amount'], float)
        assert isinstance(doc['room_number'], int)
        assert isinstance(doc['name'], str)

    def test_transform_values(self):
        """Vérifie les valeurs après transformation"""
        doc = transform_row(self.SAMPLE_ROW)
        assert doc['name'] == 'John Doe'
        assert doc['age'] == 45
        assert doc['billing_amount'] == 12345.67
        assert doc['gender'] == 'Male'

    def test_patient_id_generated(self):
        """Vérifie qu'un patient_id est bien généré"""
        doc = transform_row(self.SAMPLE_ROW)
        assert 'patient_id' in doc
        assert len(doc['patient_id']) == 12


class TestDuplicateDetection:
    """Test de la détection de doublons"""

    def test_same_patient_same_id(self):
        """Deux lignes identiques donnent le même ID"""
        row = {'Name': 'Test', 'Age': '30', 'Date of Admission': '2024-01-01'}
        assert generate_id(row) == generate_id(row)

    def test_different_patients_different_ids(self):
        """Deux patients différents donnent des IDs différents"""
        row1 = {'Name': 'Alice', 'Age': '30', 'Date of Admission': '2024-01-01'}
        row2 = {'Name': 'Bob', 'Age': '25', 'Date of Admission': '2024-02-01'}
        assert generate_id(row1) != generate_id(row2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
