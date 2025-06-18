# db.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["quizmaster"]

# Collections
users_col = db["users"]
quizzes_col = db["quizzes"]
scores_col = db["scores"]

