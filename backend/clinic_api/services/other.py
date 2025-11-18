from typing import List, Optional
from datetime import datetime
from ..database import Database
from ..models import (
    Diagnosis, DiagnosisCreate,
    Procedure, ProcedureCreate,
    Drug, DrugCreate,
    Prescription, PrescriptionCreate,
    LabTestOrder, LabTestOrderCreate,
    Delivery, DeliveryCreate,
    RecoveryStay, RecoveryStayCreate,
    RecoveryObservation, RecoveryObservationCreate
)


class DiagnosisCRUD:
    collection_name = "Diagnosis"
    
    @classmethod
    def create(cls, diagnosis: DiagnosisCreate) -> Diagnosis:
        """Create a new diagnosis"""
        collection = Database.get_collection(cls.collection_name)
        
        diagnosis_id = Database.get_next_sequence("diagnosis_id")
        
        diagnosis_dict = diagnosis.model_dump()
        diagnosis_dict["diagnosis_id"] = diagnosis_id
        
        collection.insert_one(diagnosis_dict)
        
        return Diagnosis(**diagnosis_dict)
    
    @classmethod
    def get(cls, diagnosis_id: int) -> Optional[Diagnosis]:
        """Get a diagnosis by ID"""
        collection = Database.get_collection(cls.collection_name)
        diagnosis_data = collection.find_one({"diagnosis_id": diagnosis_id}, {"_id": 0})
        
        if diagnosis_data:
            return Diagnosis(**diagnosis_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Diagnosis]:
        """Get all diagnoses"""
        collection = Database.get_collection(cls.collection_name)
        diagnoses_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        return [Diagnosis(**data) for data in diagnoses_data]
    
    @classmethod
    def search_by_code(cls, code: str) -> List[Diagnosis]:
        """Search diagnoses by code"""
        collection = Database.get_collection(cls.collection_name)
        diagnoses_data = collection.find({"code": {"$regex": code, "$options": "i"}}, {"_id": 0})
        
        return [Diagnosis(**data) for data in diagnoses_data]


class ProcedureCRUD:
    collection_name = "Procedure"
    
    @classmethod
    def create(cls, procedure: ProcedureCreate) -> Procedure:
        """Create a new procedure"""
        collection = Database.get_collection(cls.collection_name)
        
        procedure_id = Database.get_next_sequence("procedure_id")
        
        procedure_dict = procedure.model_dump()
        procedure_dict["procedure_id"] = procedure_id
        
        collection.insert_one(procedure_dict)
        
        return Procedure(**procedure_dict)
    
    @classmethod
    def get(cls, procedure_id: int) -> Optional[Procedure]:
        """Get a procedure by ID"""
        collection = Database.get_collection(cls.collection_name)
        procedure_data = collection.find_one({"procedure_id": procedure_id}, {"_id": 0})
        
        if procedure_data:
            return Procedure(**procedure_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Procedure]:
        """Get all procedures"""
        collection = Database.get_collection(cls.collection_name)
        procedures_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        return [Procedure(**data) for data in procedures_data]


class DrugCRUD:
    collection_name = "Drug"
    
    @classmethod
    def create(cls, drug: DrugCreate) -> Drug:
        """Create a new drug"""
        collection = Database.get_collection(cls.collection_name)
        
        drug_id = Database.get_next_sequence("drug_id")
        
        drug_dict = drug.model_dump()
        drug_dict["drug_id"] = drug_id
        
        collection.insert_one(drug_dict)
        
        return Drug(**drug_dict)
    
    @classmethod
    def get(cls, drug_id: int) -> Optional[Drug]:
        """Get a drug by ID"""
        collection = Database.get_collection(cls.collection_name)
        drug_data = collection.find_one({"drug_id": drug_id}, {"_id": 0})
        
        if drug_data:
            return Drug(**drug_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Drug]:
        """Get all drugs"""
        collection = Database.get_collection(cls.collection_name)
        drugs_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        return [Drug(**data) for data in drugs_data]
    
    @classmethod
    def search_by_name(cls, name: str) -> List[Drug]:
        """Search drugs by brand name"""
        collection = Database.get_collection(cls.collection_name)
        drugs_data = collection.find({"brand_name": {"$regex": name, "$options": "i"}}, {"_id": 0})
        
        return [Drug(**data) for data in drugs_data]


class PrescriptionCRUD:
    collection_name = "Prescription"
    
    @classmethod
    def create(cls, prescription: PrescriptionCreate) -> Prescription:
        """Create a new prescription"""
        collection = Database.get_collection(cls.collection_name)
        
        prescription_id = Database.get_next_sequence("prescription_id")
        
        prescription_dict = prescription.model_dump()
        prescription_dict["prescription_id"] = prescription_id
        
        if prescription_dict.get("dispensed_at"):
            prescription_dict["dispensed_at"] = prescription_dict["dispensed_at"].isoformat()
        
        collection.insert_one(prescription_dict)
        
        return Prescription(**prescription_dict)
    
    @classmethod
    def get(cls, prescription_id: int) -> Optional[Prescription]:
        """Get a prescription by ID"""
        collection = Database.get_collection(cls.collection_name)
        prescription_data = collection.find_one({"prescription_id": prescription_id}, {"_id": 0})
        
        if prescription_data:
            if prescription_data.get("dispensed_at"):
                prescription_data["dispensed_at"] = datetime.fromisoformat(prescription_data["dispensed_at"])
            return Prescription(**prescription_data)
        return None
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> List[Prescription]:
        """Get all prescriptions for a visit"""
        collection = Database.get_collection(cls.collection_name)
        prescriptions_data = collection.find({"visit_id": visit_id}, {"_id": 0})
        
        prescriptions = []
        for data in prescriptions_data:
            if data.get("dispensed_at"):
                data["dispensed_at"] = datetime.fromisoformat(data["dispensed_at"])
            prescriptions.append(Prescription(**data))
        
        return prescriptions


class LabTestOrderCRUD:
    collection_name = "LabTestOrder"
    
    @classmethod
    def create(cls, lab_test: LabTestOrderCreate) -> LabTestOrder:
        """Create a new lab test order"""
        collection = Database.get_collection(cls.collection_name)
        
        labtest_id = Database.get_next_sequence("labtest_id")
        
        lab_test_dict = lab_test.model_dump()
        lab_test_dict["labtest_id"] = labtest_id
        
        if lab_test_dict.get("result_at"):
            lab_test_dict["result_at"] = lab_test_dict["result_at"].isoformat()
        
        collection.insert_one(lab_test_dict)
        
        return LabTestOrder(**lab_test_dict)
    
    @classmethod
    def get(cls, labtest_id: int) -> Optional[LabTestOrder]:
        """Get a lab test by ID"""
        collection = Database.get_collection(cls.collection_name)
        lab_test_data = collection.find_one({"labtest_id": labtest_id}, {"_id": 0})
        
        if lab_test_data:
            if lab_test_data.get("result_at"):
                lab_test_data["result_at"] = datetime.fromisoformat(lab_test_data["result_at"])
            return LabTestOrder(**lab_test_data)
        return None
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> List[LabTestOrder]:
        """Get all lab tests for a visit"""
        collection = Database.get_collection(cls.collection_name)
        lab_tests_data = collection.find({"visit_id": visit_id}, {"_id": 0})
        
        lab_tests = []
        for data in lab_tests_data:
            if data.get("result_at"):
                data["result_at"] = datetime.fromisoformat(data["result_at"])
            lab_tests.append(LabTestOrder(**data))
        
        return lab_tests


class DeliveryCRUD:
    collection_name = "Delivery"
    
    @classmethod
    def create(cls, delivery: DeliveryCreate) -> Delivery:
        """Create a new delivery record"""
        collection = Database.get_collection(cls.collection_name)
        
        delivery_id = Database.get_next_sequence("delivery_id")
        
        delivery_dict = delivery.model_dump()
        delivery_dict["delivery_id"] = delivery_id
        
        collection.insert_one(delivery_dict)
        
        return Delivery(**delivery_dict)
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> Optional[Delivery]:
        """Get delivery record by visit ID"""
        collection = Database.get_collection(cls.collection_name)
        delivery_data = collection.find_one({"visit_id": visit_id}, {"_id": 0})
        
        if delivery_data:
            return Delivery(**delivery_data)
        return None


class RecoveryStayCRUD:
    collection_name = "RecoveryStay"
    
    @classmethod
    def create(cls, recovery_stay: RecoveryStayCreate) -> RecoveryStay:
        """Create a new recovery stay"""
        collection = Database.get_collection(cls.collection_name)
        
        stay_id = Database.get_next_sequence("stay_id")
        
        recovery_stay_dict = recovery_stay.model_dump()
        recovery_stay_dict["stay_id"] = stay_id
        recovery_stay_dict["admit_time"] = recovery_stay_dict["admit_time"].isoformat()
        
        if recovery_stay_dict.get("discharge_time"):
            recovery_stay_dict["discharge_time"] = recovery_stay_dict["discharge_time"].isoformat()
        
        collection.insert_one(recovery_stay_dict)
        
        return RecoveryStay(**recovery_stay_dict)
    
    @classmethod
    def get(cls, stay_id: int) -> Optional[RecoveryStay]:
        """Get a recovery stay by ID"""
        collection = Database.get_collection(cls.collection_name)
        stay_data = collection.find_one({"stay_id": stay_id}, {"_id": 0})
        
        if stay_data:
            stay_data["admit_time"] = datetime.fromisoformat(stay_data["admit_time"])
            if stay_data.get("discharge_time"):
                stay_data["discharge_time"] = datetime.fromisoformat(stay_data["discharge_time"])
            return RecoveryStay(**stay_data)
        return None


class RecoveryObservationCRUD:
    collection_name = "RecoveryObservation"
    
    @classmethod
    def create(cls, observation: RecoveryObservationCreate) -> RecoveryObservation:
        """Create a new recovery observation"""
        collection = Database.get_collection(cls.collection_name)
        
        observation_dict = observation.model_dump()
        observation_dict["text_on"] = observation_dict["text_on"].isoformat()
        
        if observation_dict.get("observed_at"):
            observation_dict["observed_at"] = observation_dict["observed_at"].isoformat()
        
        collection.insert_one(observation_dict)
        
        return RecoveryObservation(**observation_dict)
    
    @classmethod
    def get_by_stay(cls, stay_id: int) -> List[RecoveryObservation]:
        """Get all observations for a recovery stay"""
        collection = Database.get_collection(cls.collection_name)
        observations_data = collection.find({"stay_id": stay_id}, {"_id": 0}).sort("text_on", 1)
        
        observations = []
        for data in observations_data:
            data["text_on"] = datetime.fromisoformat(data["text_on"])
            if data.get("observed_at"):
                data["observed_at"] = datetime.fromisoformat(data["observed_at"])
            observations.append(RecoveryObservation(**data))
        
        return observations
