from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
# Initialize MongoDB client

mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client["my_database"]
collection = db["my_collection"]

# Define route to handle insert requests


@app.post("/insert")
async def insert_data(data: dict):
    try:
        # Perform the insert operation asynchronously
        result = await collection.insert_one(data)
        # Return the inserted document ID
        return {"inserted_id": str(result.inserted_id)}
    except DuplicateKeyError:
        # Handle duplicate key errors
        return {"error": "Duplicate key error."}
