from typing import List, Optional
from datetime import datetime, date
from ..database import Database
from ..models import StaffShift, StaffShiftCreate

class StaffShiftCRUD:
    collection_name = "StaffShift"
    
    @classmethod
    def create(cls, shift: StaffShiftCreate) -> StaffShift:
        collection = Database.get_collection(cls.collection_name)
        shift_id = Database.get_next_sequence("shift_id")
        
        shift_dict = shift.model_dump()
        shift_dict["shift_id"] = shift_id
        shift_dict["start_time"] = shift_dict["start_time"].isoformat()
        shift_dict["end_time"] = shift_dict["end_time"].isoformat()
        shift_dict["date"] = shift_dict["date"].isoformat()
        
        collection.insert_one(shift_dict)
        return StaffShift(**shift_dict)

    @classmethod
    def get_daily_master_schedule(cls, target_date: date) -> List[StaffShift]:
        """Get all staff working on a specific day"""
        collection = Database.get_collection(cls.collection_name)
        
        shifts_data = collection.find({
            "date": target_date.isoformat()
        }, {"_id": 0}).sort("start_time", 1)
        
        shifts = []
        for data in shifts_data:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
            data["end_time"] = datetime.fromisoformat(data["end_time"])
            data["date"] = date.fromisoformat(data["date"])
            shifts.append(StaffShift(**data))
            
        return shifts