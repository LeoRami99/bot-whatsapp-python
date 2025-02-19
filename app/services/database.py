from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.whatsapp_bot
bots_collection = db.bots
responses_collection = db.responses

def get_bot_credentials(bot_id):
    return bots_collection.find_one({"bot_id": bot_id})

def get_bot_response(bot_id, text):
    response = responses_collection.find_one({"bot_id": bot_id, "trigger": text})
    
    if response:
        return response
    else:
        return {"response": {"type": "text", "body": "Lo siento, no tengo una respuesta para eso.", "try_ai": True}}