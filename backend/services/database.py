from connection_DB import db
from pymongo.collection import ReturnDocument

#Database function to get the next sequence number for a given ID name
def get_next_sequence(id_name: str) -> int:
    """
    Returns the next sequence number for the given ID name.
    Increments the counter in the counters_primary_key_collection.
    """
    counter = db.counters_primary_key_collection.find_one_and_update(
        {"_id": id_name},
        {"$inc": {"sequence_value": 1}},
        return_document=ReturnDocument.AFTER,
        upsert=True
    )

    if not counter:
        raise ValueError(f"Counter for {id_name} not found or could not be created.")

    return counter["sequence_value"]
