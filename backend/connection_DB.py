import os
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pymongo.collection import ReturnDocument
# Load environment variables from .env file
load_dotenv()
uri = os.getenv('MONGODB_URI')

# Database name from environment
db_name = os.getenv('DB_NAME')

# Create client with TLS and system CA bundle from certifi for Atlas connections
client = MongoClient(
    uri,
    server_api=ServerApi('1'),
    tls=True,
    tlsCAFile=certifi.where()
)

# Select database handle
db = client[db_name]
# Send a ping to confirm a successful connection


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)