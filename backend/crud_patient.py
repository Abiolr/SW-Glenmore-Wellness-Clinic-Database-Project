from typing import List, Optional
from datetime import date
from database import Database
from models import Patient, PatientCreate


class PatientCRUD:
    collection_name = "Patient"
    
    @classmethod
    def create(cls, patient: PatientCreate) -> Patient:
        """Create a new patient"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next patient ID
        patient_id = Database.get_next_sequence("patient_id")
        
        patient_dict = patient.model_dump()
        patient_dict["patient_id"] = patient_id
        patient_dict["date_of_birth"] = patient_dict["date_of_birth"].isoformat()
        
        collection.insert_one(patient_dict)
        
        return Patient(**patient_dict)
    
    @classmethod
    def get(cls, patient_id: int) -> Optional[Patient]:
        """Get a patient by ID"""
        collection = Database.get_collection(cls.collection_name)
        patient_data = collection.find_one({"patient_id": patient_id}, {"_id": 0})
        
        if patient_data:
            patient_data["date_of_birth"] = date.fromisoformat(patient_data["date_of_birth"])
            return Patient(**patient_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Get all patients with pagination"""
        collection = Database.get_collection(cls.collection_name)
        patients_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        patients = []
        for patient_data in patients_data:
            patient_data["date_of_birth"] = date.fromisoformat(patient_data["date_of_birth"])
            patients.append(Patient(**patient_data))
        
        return patients
    
    @classmethod
    def update(cls, patient_id: int, patient: PatientCreate) -> Optional[Patient]:
        """Update a patient"""
        collection = Database.get_collection(cls.collection_name)
        
        patient_dict = patient.model_dump()
        patient_dict["date_of_birth"] = patient_dict["date_of_birth"].isoformat()
        
        result = collection.update_one(
            {"patient_id": patient_id},
            {"$set": patient_dict}
        )
        
        if result.modified_count > 0:
            return cls.get(patient_id)
        return None
    
    @classmethod
    def delete(cls, patient_id: int) -> bool:
        """Delete a patient"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"patient_id": patient_id})
        return result.deleted_count > 0
    
    @classmethod
    def search_by_name(cls, first_name: Optional[str] = None, last_name: Optional[str] = None) -> List[Patient]:
        """Search patients by name"""
        collection = Database.get_collection(cls.collection_name)
        query = {}
        
        if first_name:
            query["first_name"] = {"$regex": first_name, "$options": "i"}
        if last_name:
            query["last_name"] = {"$regex": last_name, "$options": "i"}
        
        patients_data = collection.find(query, {"_id": 0})
        
        patients = []
        for patient_data in patients_data:
            patient_data["date_of_birth"] = date.fromisoformat(patient_data["date_of_birth"])
            patients.append(Patient(**patient_data))
        
        return patients
