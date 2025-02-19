from pymongo import MongoClient
import os
import urllib.parse

MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASS = os.getenv("MONGO_PASS", "")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB   = os.getenv("MONGO_DB", "whatsapp_bot")

username_encoded = urllib.parse.quote_plus(MONGO_USER)
password_encoded = urllib.parse.quote_plus(MONGO_PASS)

MONGO_URI = f"mongodb://{username_encoded}:{password_encoded}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin&authMechanism=SCRAM-SHA-256"


client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
bots_collection = db.bots
responses_collection = db.responses

def get_bot_credentials(bot_id):
    return bots_collection.find_one({"bot_id": bot_id})

def get_bot_response(bot_id, text):
    response = responses_collection.find_one({"bot_id": bot_id, "trigger": text})
    if response:
        return response
    else:
        return {
            "response": {
                "type": "text",
                "body": "Lo siento, no tengo una respuesta para eso.",
                "try_ai": True
            }
        }