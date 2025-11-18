from typing import List, Optional
from datetime import date
from ..database import Database
from ..models import StaffAssignment, StaffAssignmentCreate, StaffAssignmentUpdate

class StaffAssignmentCRUD:
    collection_name = "WeeklyCoverage"
    
    @classmethod
    def create(cls, assignment: StaffAssignmentCreate) -> StaffAssignment:
        """Create a new staff assignment"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next assignment ID
        assignment_id = Database.get_next_sequence("assignment_id")
        
        assignment_dict = assignment.model_dump()
        assignment_dict["assignment_id"] = assignment_id
        # Convert date to ISO string for MongoDB storage
        assignment_dict["date"] = assignment_dict["date"].isoformat()
        
        collection.insert_one(assignment_dict)
        
        # Return object with the ID
        return StaffAssignment(**assignment_dict)
    
    @classmethod
    def get(cls, assignment_id: int) -> Optional[StaffAssignment]:
        """Get an assignment by ID"""
        collection = Database.get_collection(cls.collection_name)
        data = collection.find_one({"assignment_id": assignment_id}, {"_id": 0})
        
        if data:
            data["date"] = date.fromisoformat(data["date"])
            return StaffAssignment(**data)
        return None
    
    @classmethod
    def get_all(cls) -> List[StaffAssignment]:
        """
        Get all assignments.
        Requirement: Sorted by date, then start time.
        """
        collection = Database.get_collection(cls.collection_name)
        
        # Sort by date (ascending), then on_call_start (ascending)
        data_cursor = collection.find({}, {"_id": 0}).sort([
            ("date", 1), 
            ("on_call_start", 1)
        ])
        
        assignments = []
        for data in data_cursor:
            data["date"] = date.fromisoformat(data["date"])
            assignments.append(StaffAssignment(**data))
        
        return assignments
    
    @classmethod
    def update(cls, assignment_id: int, update_data: StaffAssignmentUpdate) -> Optional[StaffAssignment]:
        """Update an existing assignment"""
        collection = Database.get_collection(cls.collection_name)
        
        # Filter out None values to only update provided fields
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
        
        if "date" in update_dict:
            update_dict["date"] = update_dict["date"].isoformat()
            
        if not update_dict:
            return cls.get(assignment_id)
            
        result = collection.update_one(
            {"assignment_id": assignment_id},
            {"$set": update_dict}
        )
        
        if result.matched_count > 0:
            return cls.get(assignment_id)
        return None
    
    @classmethod
    def delete(cls, assignment_id: int) -> bool:
        """Delete an assignment"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"assignment_id": assignment_id})
        return result.deleted_count > 0