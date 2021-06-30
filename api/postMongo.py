import pymongo
from pymongo import MongoClient
from bson import ObjectId
import json
import datetime
from .usersMongo import getUsersByArea
import os

dbURL = os.environ.get('COVIDDB')
if dbURL == None:
    print("Database URL Not Found!");

client = MongoClient(dbURL)

db = client.get_database('hackcovid')
posts = db.posts

LIMIT = 10 # Posts to show per page

def addPost(post):
    post['createdAt'] = datetime.datetime.utcnow()
    post['user'] = ObjectId(post['user'])
    newPost = posts.insert_one(post)
    try:
        id = newPost.inserted_id
        return {
            'status': 200,
            'id': id
        }
    except Exception as e:
        return {
            'status': 500,
            'error': "Server Error"
        }

def getPostwithPage(query, pageNo):
    query['deleted'] = {
        '$ne': True
    }
    allPosts = posts.find(query).sort('createdAt', pymongo.DESCENDING).skip(LIMIT*(pageNo - 1)).limit(LIMIT)
    return {
        'count': allPosts.count(),
        'data': allPosts
    }

def delPost(id):
    field = {
        '$set': {
            'deleted': True
        }
    }

    query = {
        '_id': ObjectId(id)
    }
    posts.update_one(query, field)
    return {
        'status': 200
    }
