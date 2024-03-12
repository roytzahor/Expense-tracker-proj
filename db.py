from pymongo import MongoClient
from pymongo.errors import PyMongoError
import logging
import os
from datetime import datetime
from bson import ObjectId
import uuid

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the default MongoDB URI
default_mongo_uri = "mongodb://host.docker.internal:27017/expenses_tracker_db"

# Initialize the MongoDB client with environment variables or use the default
mongo_uri = os.getenv('MONGO_URI', default_mongo_uri)
client = MongoClient(mongo_uri)
db = client["expenses_tracker_db"]

# Define your collections
users_collection = db["users"]
expenses_collection = db["expenses"]

def register_user(username, password):
    """
    Register a new user in the database.
    Returns 'success', 'exists', or 'error'.
    """
    try:
        if users_collection.find_one({"username": username}):
            return 'exists'
        users_collection.insert_one({"username": username, "password": password})
        return 'success'
    except PyMongoError as e:
        logger.error("An error occurred during user registration: %s", e)
        return 'error'
    
def find_user_by_username(username):
    """
    Find a user by username.
    """
    try:
        return users_collection.find_one({"username": username})
    except Exception as e:
        logger.error("An error occurred while finding user by username: %s", e)
        return None

def get_user_id(username):
    """
    Retrieve the user's ID using their username.
    """
    try:
        user = users_collection.find_one({"username": username})
        return user['_id'] if user else None
    except Exception as e:
        logger.error("An error occurred while retrieving the user ID: %s", e)
        return None

def get_user_expenses(user_id):
    """
    Fetches expenses for the current month for a specific user.
    """
    now = datetime.now()
    query = {
        'user_id': ObjectId(user_id),
        'date': {
            '$gte': datetime(now.year, now.month, 1),
            '$lt': datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        }
    }
    return list(expenses_collection.find(query))

def add_expense_to_db(user_id, category, amount, date, notes=''):
    """
    Adds a new expense to the database.
    """
    try:
        expense_id = str(uuid.uuid4())
        expense_document = {
            '_id': expense_id,
            'user_id': user_id,
            'category': category,
            'amount': amount,
            'date': date,
            'notes': notes
        }
        expenses_collection.insert_one(expense_document)
        return expense_id
    except Exception as e:
        logger.error("An error occurred while inserting an expense: %s", e)
        return None

def remove_expense_from_db(expense_id):
    """
    Removes an expense from the database.
    """
    try:
        result = expenses_collection.delete_one({'_id': expense_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error("An error occurred while deleting an expense: %s", e)
        return False

def get_current_month_expenses(user_id):
    """
    Retrieves expenses for the current month for a specified user.
    """
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
    query = {
        'user_id': user_id,
        'date': {'$gte': start_date, '$lt': end_date}
    }
    return list(expenses_collection.find(query).sort("date", -1))
