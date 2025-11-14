from typing import List, Optional
from database import Database
from models import Staff, StaffCreate


class StaffCRUD:
    collection_name = "Staff"
    
    @classmethod
    def create(cls, staff: StaffCreate) -> Staff:
        """Create a new staff member"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next staff ID
        staff_id = Database.get_next_sequence("staff_id")
        
        staff_dict = staff.model_dump()
        staff_dict["staff_id"] = staff_id
        
        collection.insert_one(staff_dict)
        
        return Staff(**staff_dict)
    
    @classmethod
    def get(cls, staff_id: int) -> Optional[Staff]:
        """Get a staff member by ID"""
        collection = Database.get_collection(cls.collection_name)
        staff_data = collection.find_one({"staff_id": staff_id}, {"_id": 0})
        
        if staff_data:
            return Staff(**staff_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Staff]:
        """Get all staff members with pagination"""
        collection = Database.get_collection(cls.collection_name)
        
        query = {}
        if active_only:
            query["active"] = True
        
        staff_data = collection.find(query, {"_id": 0}).skip(skip).limit(limit)
        
        return [Staff(**data) for data in staff_data]
    
    @classmethod
    def update(cls, staff_id: int, staff: StaffCreate) -> Optional[Staff]:
        """Update a staff member"""
        collection = Database.get_collection(cls.collection_name)
        
        staff_dict = staff.model_dump()
        
        result = collection.update_one(
            {"staff_id": staff_id},
            {"$set": staff_dict}
        )
        
        if result.modified_count > 0:
            return cls.get(staff_id)
        return None
    
    @classmethod
    def delete(cls, staff_id: int) -> bool:
        """Delete a staff member"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"staff_id": staff_id})
        return result.deleted_count > 0
    
    @classmethod
    def deactivate(cls, staff_id: int) -> Optional[Staff]:
        """Deactivate a staff member instead of deleting"""
        collection = Database.get_collection(cls.collection_name)
        
        result = collection.update_one(
            {"staff_id": staff_id},
            {"$set": {"active": False}}
        )
        
        if result.modified_count > 0:
            return cls.get(staff_id)
        return None
