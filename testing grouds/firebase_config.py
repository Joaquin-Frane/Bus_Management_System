import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key JSON file
cred = credentials.Certificate('Bus_Reservation_System2/busrvs-firebase-adminsdk-yr5bm-bbea193d41.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()