from pymongo import MongoClient
from bson import ObjectId
import json
import os

dbURL = os.environ.get('COVIDDB')
if dbURL == None:
    print("Database URL Not Found!");

client = MongoClient(dbURL)

db = client.get_database('hackcovid')
users = db.users

def get_user(query):
    user = users.find_one(query)
    if user == None:
        return {
            'status': 404
        }
    else:
        return {
            'status': 200,
            'data': user
        }

def insert_user(query):
    user = users.insert_one(query)
    try:
        id = user.inserted_id
        return {
            'status': 200,
            'id': id 
        }
    except Exception as e:
        return {
            'status': 500,
            'error': e
        }

def getUsersByArea(zip):
    query = {
        'zip': zip,
    }
    user = users.find(query)
    if (user == None):
        return {
            'status': 404,
            'error': "No user's found"
        }
    else:
        return {
            'status': 200,
            'data': user 
        }

def updateUser(id, fields):
    userQuery = {
        '_id': ObjectId(id)
    }
    user = get_user(userQuery)
    if (user['status'] == 404):
        return {
            'status': 404,
            'error': "user does not exist"
        }
    else:
        newFields = {
            "$set": fields
        }
        users.update_one(userQuery, newFields)
        return {
            'status': 200
        }

