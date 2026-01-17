from pymongo import MongoClient
from urllib.parse import quote_plus

def conectaBanco(password):
    password_encoded = quote_plus(password)

    uri = (
        f"mongodb+srv://admin:{password_encoded}"
        "@joy.lhvpeiz.mongodb.net/?retryWrites=true&w=majority"
    )

    client = MongoClient(uri)
    db = client["joy"]
    return db
