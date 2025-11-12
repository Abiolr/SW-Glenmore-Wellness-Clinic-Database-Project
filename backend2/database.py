"""Simple MongoDB client factory for backend2 (pymongo)"""
from typing import Tuple
import certifi
from pymongo import MongoClient

from .config import settings


def get_client() -> MongoClient:
    """Return a MongoClient using certifi CA bundle."""
    return MongoClient(settings.MONGO_URI, tls=True, tlsCAFile=certifi.where())


def get_db():
    client = get_client()
    return client[settings.DATABASE_NAME]
from pymongo import MongoClient
from .config import settings

# Basic MongoDB client; replace with async or connection pool if desired
client = MongoClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]
