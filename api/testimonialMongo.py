import pymongo
from pymongo import MongoClient
from bson import ObjectId
import json
import os

dbURL = os.environ.get('COVIDDB')
if dbURL == None:
    print("Database URL Not Found!");

client = MongoClient(dbURL)

db = client.get_database('hackcovid')
testimonials = db.testimonials

def create(data):
    data['user'] = ObjectId(data['uid'])
    newTestimonial = testimonials.insert_one(data)
    try:
        id = newTestimonial.inserted_id
        return {
            'status': 200,
            'id': id
        }
    except Exception as e:
        return {
            'status': 500,
            'error': "Server Error"
        }

def get(query):
    allTestimonials = testimonials.find(query).sort('rdate', pymongo.DESCENDING).limit(5)
    return {
        'count': allTestimonials.count(),
        'data': allTestimonials
    }