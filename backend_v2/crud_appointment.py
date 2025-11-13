from typing import List, Optional
from datetime import datetime, date
from database import Database
from models import Appointment, AppointmentCreate


class AppointmentCRUD:
    collection_name = "Appointment"
    
    @classmethod
    def create(cls, appointment: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next appointment ID
        appointment_id = Database.get_next_sequence("appointment_id")
        
        appointment_dict = appointment.model_dump()
        appointment_dict["appointment_id"] = appointment_id
        appointment_dict["created_at"] = datetime.now()
        
        # Convert datetime to ISO format strings
        appointment_dict["scheduled_start"] = appointment_dict["scheduled_start"].isoformat()
        appointment_dict["scheduled_end"] = appointment_dict["scheduled_end"].isoformat()
        appointment_dict["created_at"] = appointment_dict["created_at"].isoformat()
        
        collection.insert_one(appointment_dict)
        
        return Appointment(**appointment_dict)
    
    @classmethod
    def get(cls, appointment_id: int) -> Optional[Appointment]:
        """Get an appointment by ID"""
        collection = Database.get_collection(cls.collection_name)
        appointment_data = collection.find_one({"appointment_id": appointment_id}, {"_id": 0})
        
        if appointment_data:
            appointment_data["scheduled_start"] = datetime.fromisoformat(appointment_data["scheduled_start"])
            appointment_data["scheduled_end"] = datetime.fromisoformat(appointment_data["scheduled_end"])
            if appointment_data.get("created_at"):
                appointment_data["created_at"] = datetime.fromisoformat(appointment_data["created_at"])
            return Appointment(**appointment_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Appointment]:
        """Get all appointments with pagination"""
        collection = Database.get_collection(cls.collection_name)
        appointments_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        appointments = []
        for data in appointments_data:
            data["scheduled_start"] = datetime.fromisoformat(data["scheduled_start"])
            data["scheduled_end"] = datetime.fromisoformat(data["scheduled_end"])
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            appointments.append(Appointment(**data))
        
        return appointments
    
    @classmethod
    def get_by_patient(cls, patient_id: int) -> List[Appointment]:
        """Get all appointments for a specific patient"""
        collection = Database.get_collection(cls.collection_name)
        appointments_data = collection.find({"patient_id": patient_id}, {"_id": 0})
        
        appointments = []
        for data in appointments_data:
            data["scheduled_start"] = datetime.fromisoformat(data["scheduled_start"])
            data["scheduled_end"] = datetime.fromisoformat(data["scheduled_end"])
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            appointments.append(Appointment(**data))
        
        return appointments
    
    @classmethod
    def get_by_staff(cls, staff_id: int, date_filter: Optional[date] = None) -> List[Appointment]:
        """Get all appointments for a specific staff member, optionally filtered by date"""
        collection = Database.get_collection(cls.collection_name)
        
        query = {"staff_id": staff_id}
        
        if date_filter:
            start_of_day = datetime.combine(date_filter, datetime.min.time())
            end_of_day = datetime.combine(date_filter, datetime.max.time())
            query["scheduled_start"] = {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            }
        
        appointments_data = collection.find(query, {"_id": 0}).sort("scheduled_start", 1)
        
        appointments = []
        for data in appointments_data:
            data["scheduled_start"] = datetime.fromisoformat(data["scheduled_start"])
            data["scheduled_end"] = datetime.fromisoformat(data["scheduled_end"])
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            appointments.append(Appointment(**data))
        
        return appointments
    
    @classmethod
    def get_by_date_range(cls, start_date: datetime, end_date: datetime) -> List[Appointment]:
        """Get all appointments within a date range"""
        collection = Database.get_collection(cls.collection_name)
        
        query = {
            "scheduled_start": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
        
        appointments_data = collection.find(query, {"_id": 0}).sort("scheduled_start", 1)
        
        appointments = []
        for data in appointments_data:
            data["scheduled_start"] = datetime.fromisoformat(data["scheduled_start"])
            data["scheduled_end"] = datetime.fromisoformat(data["scheduled_end"])
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            appointments.append(Appointment(**data))
        
        return appointments
    
    @classmethod
    def update(cls, appointment_id: int, appointment: AppointmentCreate) -> Optional[Appointment]:
        """Update an appointment"""
        collection = Database.get_collection(cls.collection_name)
        
        appointment_dict = appointment.model_dump()
        appointment_dict["scheduled_start"] = appointment_dict["scheduled_start"].isoformat()
        appointment_dict["scheduled_end"] = appointment_dict["scheduled_end"].isoformat()
        
        result = collection.update_one(
            {"appointment_id": appointment_id},
            {"$set": appointment_dict}
        )
        
        if result.modified_count > 0:
            return cls.get(appointment_id)
        return None
    
    @classmethod
    def delete(cls, appointment_id: int) -> bool:
        """Delete an appointment"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"appointment_id": appointment_id})
        return result.deleted_count > 0
