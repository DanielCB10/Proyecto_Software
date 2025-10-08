from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["divisas"]

db.rates_cache.update_one(
    {"key": "GBP_USD"},
    {"$set": {"rate": 1.27, "createdAt": datetime.now(timezone.utc)}},
    upsert=True
)

db.conversions.insert_one({
    "from": "GBP",
    "to": "USD",
    "amount": 50,
    "rate": 1.27,
    "converted": 63.5,
    "createdAt": datetime.now(timezone.utc)
})

print("Dato insertado")
