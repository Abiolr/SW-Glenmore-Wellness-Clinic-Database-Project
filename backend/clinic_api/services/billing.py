from typing import List, Optional
from ..database import Database
from ..models import Insurer, InsurerCreate

class InsurerCRUD:
    collection_name = "Insurer"
    
    @classmethod
    def create(cls, insurer: InsurerCreate) -> Insurer:
        collection = Database.get_collection(cls.collection_name)
        insurer_id = Database.get_next_sequence("insurer_id")
        
        insurer_dict = insurer.model_dump()
        insurer_dict["insurer_id"] = insurer_id
        
        collection.insert_one(insurer_dict)
        return Insurer(**insurer_dict)

    @classmethod
    def get_all(cls) -> List[Insurer]:
        collection = Database.get_collection(cls.collection_name)
        return [Insurer(**data) for data in collection.find({}, {"_id": 0})]