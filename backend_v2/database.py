from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client = None
    db = None
    
    @classmethod
    def connect_db(cls):
        """Connect to MongoDB database"""
        try:
            mongodb_url = os.getenv("MONGODB_URL")
            db_name = os.getenv("MONGODB_DB_NAME", "GlenmoreWellnessDB")
            
            cls.client = MongoClient(mongodb_url)
            cls.db = cls.client[db_name]
            
            # Test the connection
            cls.client.admin.command('ping')
            print(f"Successfully connected to MongoDB database: {db_name}")
            
            return cls.db
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")
    
    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls.db is None:
            cls.connect_db()
        return cls.db
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection"""
        db = cls.get_db()
        return db[collection_name]
    
    @classmethod
    def get_next_sequence(cls, sequence_name: str) -> int:
        """Get next sequence number for auto-increment IDs"""
        db = cls.get_db()
        counters = db["counters_primary_key_collection"]
        
        result = counters.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=True
        )
        
        return result["sequence_value"]
