from typing import List, Optional
from datetime import datetime, date
from database import Database
from models import (
    Visit, VisitCreate, 
    VisitDiagnosis, VisitDiagnosisCreate,
    VisitProcedure, VisitProcedureCreate
)


class VisitCRUD:
    collection_name = "Visit"
    
    @classmethod
    def create(cls, visit: VisitCreate) -> Visit:
        """Create a new visit"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next visit ID
        visit_id = Database.get_next_sequence("visit_id")
        
        visit_dict = visit.model_dump()
        visit_dict["visit_id"] = visit_id
        
        # Convert datetime to ISO format strings
        visit_dict["start_time"] = visit_dict["start_time"].isoformat()
        if visit_dict.get("end_time"):
            visit_dict["end_time"] = visit_dict["end_time"].isoformat()
        
        collection.insert_one(visit_dict)
        
        return Visit(**visit_dict)
    
    @classmethod
    def get(cls, visit_id: int) -> Optional[Visit]:
        """Get a visit by ID"""
        collection = Database.get_collection(cls.collection_name)
        visit_data = collection.find_one({"visit_id": visit_id}, {"_id": 0})
        
        if visit_data:
            visit_data["start_time"] = datetime.fromisoformat(visit_data["start_time"])
            if visit_data.get("end_time"):
                visit_data["end_time"] = datetime.fromisoformat(visit_data["end_time"])
            return Visit(**visit_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Visit]:
        """Get all visits with pagination"""
        collection = Database.get_collection(cls.collection_name)
        visits_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        visits = []
        for data in visits_data:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
            if data.get("end_time"):
                data["end_time"] = datetime.fromisoformat(data["end_time"])
            visits.append(Visit(**data))
        
        return visits
    
    @classmethod
    def get_by_patient(cls, patient_id: int) -> List[Visit]:
        """Get all visits for a specific patient"""
        collection = Database.get_collection(cls.collection_name)
        visits_data = collection.find({"patient_id": patient_id}, {"_id": 0}).sort("start_time", -1)
        
        visits = []
        for data in visits_data:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
            if data.get("end_time"):
                data["end_time"] = datetime.fromisoformat(data["end_time"])
            visits.append(Visit(**data))
        
        return visits
    
    @classmethod
    def update(cls, visit_id: int, visit: VisitCreate) -> Optional[Visit]:
        """Update a visit"""
        collection = Database.get_collection(cls.collection_name)
        
        visit_dict = visit.model_dump()
        visit_dict["start_time"] = visit_dict["start_time"].isoformat()
        if visit_dict.get("end_time"):
            visit_dict["end_time"] = visit_dict["end_time"].isoformat()
        
        result = collection.update_one(
            {"visit_id": visit_id},
            {"$set": visit_dict}
        )
        
        if result.modified_count > 0:
            return cls.get(visit_id)
        return None
    
    @classmethod
    def delete(cls, visit_id: int) -> bool:
        """Delete a visit"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"visit_id": visit_id})
        return result.deleted_count > 0


class VisitDiagnosisCRUD:
    collection_name = "VisitDiagnosis"
    
    @classmethod
    def create(cls, visit_diagnosis: VisitDiagnosisCreate) -> VisitDiagnosis:
        """Link a diagnosis to a visit"""
        collection = Database.get_collection(cls.collection_name)
        
        visit_diagnosis_dict = visit_diagnosis.model_dump()
        collection.insert_one(visit_diagnosis_dict)
        
        return VisitDiagnosis(**visit_diagnosis_dict)
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> List[VisitDiagnosis]:
        """Get all diagnoses for a specific visit"""
        collection = Database.get_collection(cls.collection_name)
        diagnoses_data = collection.find({"visit_id": visit_id}, {"_id": 0})
        
        return [VisitDiagnosis(**data) for data in diagnoses_data]
    
    @classmethod
    def delete(cls, visit_id: int, diagnosis_id: int) -> bool:
        """Remove a diagnosis from a visit"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"visit_id": visit_id, "diagnosis_id": diagnosis_id})
        return result.deleted_count > 0


class VisitProcedureCRUD:
    collection_name = "VisitProcedure"
    
    @classmethod
    def create(cls, visit_procedure: VisitProcedureCreate) -> VisitProcedure:
        """Link a procedure to a visit"""
        collection = Database.get_collection(cls.collection_name)
        
        visit_procedure_dict = visit_procedure.model_dump()
        collection.insert_one(visit_procedure_dict)
        
        return VisitProcedure(**visit_procedure_dict)
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> List[VisitProcedure]:
        """Get all procedures for a specific visit"""
        collection = Database.get_collection(cls.collection_name)
        procedures_data = collection.find({"visit_id": visit_id}, {"_id": 0})
        
        return [VisitProcedure(**data) for data in procedures_data]
    
    @classmethod
    def delete(cls, visit_id: int, procedure_id: int) -> bool:
        """Remove a procedure from a visit"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"visit_id": visit_id, "procedure_id": procedure_id})
        return result.deleted_count > 0
