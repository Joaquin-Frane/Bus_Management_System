import firebase_admin
from firebase_config import db

def get_firestore_structure(collection_ref, depth=0):
    collections = collection_ref.collections()
    for collection in collections:
        print(" " * depth * 2 + f"Collection: {collection.id}")
        docs = collection.stream()
        
        for doc in docs:
            print(" " * (depth + 1) * 2 + f"Document: {doc.id}")
            get_firestore_structure(doc.reference, depth + 2)  # Recursive call for subcollections

get_firestore_structure(db)