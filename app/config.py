import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
    DATA_DIR = os.getenv("DATA_DIR", "data/")