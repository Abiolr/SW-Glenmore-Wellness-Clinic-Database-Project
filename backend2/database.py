from pymongo import MongoClient
from .config import settings

# Basic MongoDB client; replace with async or connection pool if desired
client = MongoClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]
