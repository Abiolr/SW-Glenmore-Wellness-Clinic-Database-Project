from typing import List, Optional
from datetime import datetime
from pymongo import ReturnDocument
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
        
        # Auto-populate patient_id from visit if not provided
        if not prescription_dict.get("patient_id") and prescription_dict.get("visit_id"):
            db = Database.connect_db()
            visit = db.Visit.find_one({"visit_id": prescription_dict["visit_id"]}, {"patient_id": 1, "_id": 0})
            if visit and visit.get("patient_id"):
                prescription_dict["patient_id"] = visit["patient_id"]
        
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
        # Try canonical key first, then common legacy variants
        lab_test_data = collection.find_one({"labtest_id": labtest_id}, {"_id": 0})
        if not lab_test_data:
            lab_test_data = collection.find_one({"LabTest_Id": labtest_id}, {"_id": 0})
        if not lab_test_data:
            lab_test_data = collection.find_one({"Labtest_Id": labtest_id}, {"_id": 0})
        
        if lab_test_data:
            # Normalize legacy keys into canonical shape for the model
            norm = {
                'labtest_id': lab_test_data.get('labtest_id') or lab_test_data.get('LabTest_Id') or lab_test_data.get('Labtest_Id'),
                'visit_id': lab_test_data.get('visit_id') or lab_test_data.get('Visit_Id'),
                'ordered_by': lab_test_data.get('ordered_by') or lab_test_data.get('Ordered_By'),
                'test_name': lab_test_data.get('test_name') or lab_test_data.get('Test_Name'),
                'performed_by': lab_test_data.get('performed_by') or lab_test_data.get('Performed_By') or lab_test_data.get('performedBy'),
                'result_at': lab_test_data.get('result_at') or lab_test_data.get('Result_At'),
                'notes': lab_test_data.get('notes') or lab_test_data.get('Result_Text') or lab_test_data.get('Notes') or ''
            }

            if norm.get('result_at') and isinstance(norm.get('result_at'), str):
                try:
                    norm['result_at'] = datetime.fromisoformat(norm['result_at'])
                except Exception:
                    pass

            return LabTestOrder(**norm)
        return None
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> List[LabTestOrder]:
        """Get all lab tests for a visit.

        Tolerant of legacy field names/casing in the DB such as `Visit_Id`,
        `LabTest_Id`, `Ordered_By`, `Test_Name`, `Result_At`, `Notes`.
        Normalizes returned documents into the `LabTestOrder` model shape.
        """
        collection = Database.get_collection(cls.collection_name)

        # Query for either canonical `visit_id` or legacy `Visit_Id`
        cursor = collection.find({"$or": [{"visit_id": visit_id}, {"Visit_Id": visit_id}]}, {"_id": 0})

        lab_tests: List[LabTestOrder] = []
        for data in cursor:
            # Build normalized dict mapping legacy keys to canonical keys
            norm = {
                'labtest_id': data.get('labtest_id') or data.get('LabTest_Id') or data.get('labtestId'),
                'visit_id': data.get('visit_id') or data.get('Visit_Id'),
                'ordered_by': data.get('ordered_by') or data.get('Ordered_By') or data.get('orderedBy'),
                'test_name': data.get('test_name') or data.get('Test_Name') or data.get('testName') or data.get('test'),
                'performed_by': data.get('performed_by') or data.get('performed_by_id') or data.get('performedBy'),
                'result_at': data.get('result_at') or data.get('Result_At') or data.get('resultAt'),
                'notes': data.get('notes') or data.get('Notes') or ''
            }

            # parse ISO strings into datetimes when possible
            if norm.get('result_at') and isinstance(norm.get('result_at'), str):
                try:
                    norm['result_at'] = datetime.fromisoformat(norm['result_at'])
                except Exception:
                    # leave as-is if parsing fails
                    pass

            try:
                lab_tests.append(LabTestOrder(**norm))
            except Exception:
                # skip malformed docs rather than raise
                continue

        return lab_tests

    @classmethod
    def get_by_date(cls, date_str: str) -> List[dict]:
        """Get lab tests that have results on a given date (ISO date 'YYYY-MM-DD').

        Returns normalized dicts with canonical keys so the frontend can consume them
        regardless of legacy field name capitalization in the DB.
        """
        collection = Database.get_collection(cls.collection_name)
        results: List[dict] = []

        # Query for common timestamp fields that start with the date
        query = {
            "$or": [
                {"result_at": {"$regex": f"^{date_str}"}},
                {"Result_At": {"$regex": f"^{date_str}"}},
            ]
        }

        cursor = collection.find(query, {"_id": 0})
        for d in cursor:
            norm = {
                'labtest_id': d.get('labtest_id') or d.get('LabTest_Id') or d.get('Labtest_Id'),
                'visit_id': d.get('visit_id') or d.get('Visit_Id'),
                'ordered_by': d.get('ordered_by') or d.get('Ordered_By'),
                'test_name': d.get('test_name') or d.get('Test_Name') or d.get('Test') or d.get('test'),
                'performed_by': d.get('performed_by') or d.get('Performed_By') or d.get('performedBy'),
                'result_at': d.get('result_at') or d.get('Result_At'),
                'notes': d.get('notes') or d.get('Result_Text') or d.get('Notes') or ''
            }

            # convert to ISO string for JSON safety if datetime present
            if isinstance(norm.get('result_at'), datetime):
                norm['result_at'] = norm['result_at'].isoformat()

            results.append(norm)

        return results


class DeliveryCRUD:
    collection_name = "Delivery"
    
    @classmethod
    def create(cls, delivery: DeliveryCreate) -> Delivery:
        """Create a new delivery record"""
        collection = Database.get_collection(cls.collection_name)
        
        delivery_id = Database.get_next_sequence("delivery_id")
        
        delivery_dict = delivery.model_dump()
        delivery_dict["delivery_id"] = delivery_id
        # normalize delivery_date if provided (store as ISO string)
        if delivery_dict.get("delivery_date") and isinstance(delivery_dict.get("delivery_date"), datetime):
            delivery_dict["delivery_date"] = delivery_dict["delivery_date"].isoformat()

        collection.insert_one(delivery_dict)
        
        return Delivery(**delivery_dict)
    
    @classmethod
    def get_by_visit(cls, visit_id: int) -> Optional[Delivery]:
        """Get delivery record by visit ID"""
        collection = Database.get_collection(cls.collection_name)
        # try canonical key first, then legacy `Visit_Id`
        delivery_data = collection.find_one({"visit_id": visit_id}, {"_id": 0})
        if not delivery_data:
            delivery_data = collection.find_one({"Visit_Id": visit_id}, {"_id": 0})

        if delivery_data:
            norm = cls._normalize_delivery_doc(delivery_data)
            try:
                return Delivery(**norm)
            except Exception:
                # If model coercion fails, return None so caller can handle
                return None
        return None

    @staticmethod
    def _normalize_delivery_doc(d: dict) -> dict:
        """Normalize raw delivery document keys to the expected names.
        Supports legacy keys: Delivery_Id, Visit_Id, Delivered_By, Start_Time, End_Time, Notes
        Returns dict with keys: delivery_id, visit_id, performed_by, delivery_date, end_time, notes
        """
        out: dict = {}
        out['delivery_id'] = d.get('delivery_id') or d.get('Delivery_Id') or d.get('DeliveryId') or d.get('_id')
        out['visit_id'] = d.get('visit_id') or d.get('Visit_Id') or d.get('VisitId')
        out['performed_by'] = d.get('performed_by') or d.get('performed_by_id') or d.get('Delivered_By') or d.get('DeliveredBy') or d.get('practitioner_id')
        # choose Start_Time or delivery_date
        out['delivery_date'] = d.get('delivery_date') or d.get('Start_Time') or d.get('start_time')
        out['end_time'] = d.get('End_Time') or d.get('end_time') or None
        out['notes'] = d.get('notes') or d.get('Notes') or ''
        out['_raw'] = d
        return out

    @classmethod
    def get_by_date(cls, date_str: str) -> List[dict]:
        """Get deliveries that occurred on a given date (ISO date 'YYYY-MM-DD').
        Returns normalized dicts so frontend receives consistent keys even if DB uses legacy field names.
        """
        collection = Database.get_collection(cls.collection_name)
        results: List[dict] = []
        # Query for common timestamp fields that start with the date
        query = {
            "$or": [
                {"delivery_date": {"$regex": f"^{date_str}"}},
                {"Start_Time": {"$regex": f"^{date_str}"}},
                {"start_time": {"$regex": f"^{date_str}"}}
            ]
        }
        cursor = collection.find(query, {"_id": 0})
        for d in cursor:
            results.append(cls._normalize_delivery_doc(d))
        return results


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

    @classmethod
    def update(cls, stay_id: int, updates: dict) -> Optional[RecoveryStay]:
        """Update fields on a recovery stay (e.g., discharge_time, discharged_by)"""
        collection = Database.get_collection(cls.collection_name)

        # If discharge_time is a datetime, convert to isoformat
        if updates.get('discharge_time') and isinstance(updates.get('discharge_time'), datetime):
            updates['discharge_time'] = updates['discharge_time'].isoformat()

        result = collection.find_one_and_update(
            {'stay_id': stay_id},
            {'$set': updates},
            projection={'_id': 0},
            return_document=ReturnDocument.AFTER
        )

        if result:
            # convert stored iso strings back to datetimes for model
            result['admit_time'] = datetime.fromisoformat(result['admit_time'])
            if result.get('discharge_time'):
                result['discharge_time'] = datetime.fromisoformat(result['discharge_time'])
            return RecoveryStay(**result)

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
