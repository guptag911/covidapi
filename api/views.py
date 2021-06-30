from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, Http404, HttpResponse
from .encryption import getKeyToken, validatePassword

from .testimonialMongo import create, get
from .usersMongo  import getUsersByArea, get_user, insert_user, updateUser
from .postMongo import addPost, delPost, getPostwithPage, delPost

from bson import ObjectId, json_util
import json

DEAULT_FILTER = [{}]

def parse_json(data):
    return json.loads(json_util.dumps(data))

def filterHandler(allFilter):
    query = {}
    for filter in allFilter:
        if 'type' in filter and  filter['type'] == 'area' :
            users = getUsersByArea(filter['zip'])
            if users['status'] == 404:
                user = []
            else:
                user = [u['_id'] for u in users['data']]
            query = {
                'user': {
                    '$in': user
                }
            }
        if 'type' in filter and  filter['type'] == 'category' :
            query = {
                'tag': int(filter['tag'])
            }
        if 'type' in filter and filter['type'] == 'mine' :
            query = {
                'user': ObjectId(filter['id'])
            }
    return query

@api_view(['POST'])
def signup(request):
    if (request.data):
        myUser = request.data
    else:
        myUser = {}

    userQuery = {
        'email': myUser['email']
    }
    user_details = get_user(userQuery)
    if (user_details['status'] == 404):
        # Add this user
        token, key = getKeyToken(myUser['pass'])
        newUser = {
            'name': myUser['name'],
            'address': myUser['address'],
            'zip': myUser['zip'],
            'email': myUser['email'],
            'number': myUser['number'],
            'token': token,
            'key': key
        }
        newUserId = insert_user(newUser)
        return Response(parse_json(newUserId))
    else:
        # User Already Exists
        return Response({
            'status': 500, 
            'error': 'User Already Exists'
        })

@api_view(['POST'])
def signin(request):
    if (request.data):
        myUser = request.data
    else:
        myUser = {}
    
    userQuery = {
        'email': myUser['email']
    }
    user_details = get_user(userQuery)
    if (user_details['status'] == 404):
        return Response({
            'status': 500,
            'error': 'User not found!'
        })
    else:
        user_details = user_details['data']
        if validatePassword(myUser['pass'], user_details['key'], user_details['token']):
            userId = str(user_details['_id'])
            return Response({
                'status': 200,
                'data': userId
            })
        else:
            return Response({
                'status': 500,
                'error': "Wrong User Password!"
            })

@api_view(['POST'])
def UpdateUser(request):
    uid = ''
    fields = {}
    payload = request.data
    if 'id' in payload:
        uid = payload['id']
        if 'fields' in payload:
            fields = payload['fields']
        else:
            return Response({
                'status': 200,
                'data': 'No fields to update'
            })
        newUser = updateUser(uid, fields)
        return Response(parse_json(newUser));
    else:
        return Response({
            'status': 500,
            'error': 'No Id Found!'
        })

@api_view(['POST'])
def user(request):
    if (request.data):
        id = request.data['id']
    else:
        id = ''
    userQuery =  {
        '_id': ObjectId(id)
    }
    userDetails = get_user(userQuery)
    if (userDetails['status'] == 404):
        return Response({
            'status': 500,
            'error': "User Not Found"
        })
    else:
        del userDetails['data']['key']
        del userDetails['data']['token']
        result = {
            'status': 200,
            'data': parse_json(userDetails)
        }
        return Response(result)

@api_view(['GET'])
def myUser(request, id):
    userQuery = {
        '_id': ObjectId(id)
    }
    userDetails = get_user(userQuery)

    if (userDetails['status'] == 404):
        return Response({
            'status': 404,
            'error': "User Not Found"
        })
    else:
        del userDetails['data']['key']
        del userDetails['data']['token']
        
        return Response({
            'status': 200,
            'data': parse_json(userDetails)
        })

@api_view(['POST'])
def addpost(request):
    data = request.data

    if 'user' not in data:
        return Response({
            'status': 403,
            'error': "Permission Denied"
        })
    
    newPostId = addPost(data)

    return Response(parse_json(newPostId))

@api_view(['GET'])
def post(request, page, filter):
    if page <= 0:
        return Response({
            'status': 404,
            'error': "Does Not exist"
        })
    else:
        query = {}
        filter = json.loads(filter)
        if filter != DEAULT_FILTER:
            query = filterHandler(filter)
        posts = getPostwithPage(query , page)
        return Response(parse_json(posts))

@api_view(['POST'])
def deletePost(request):
    data = request.data
    postId = data['id']
    return Response(delPost(postId))

@api_view(['POST'])
def newTestimonial(request):
    data = request.data
    if 'uid' not in data or data['uid'] == '':
        return Response({
            'status': 500,
            'error': "You must login to create testimonial"
        })
    else:
        res = create(data)
        return Response(parse_json(res))

@api_view(['GET'])
def getTestimonials(request):
    myTestimonials = get({})
    return Response(parse_json(myTestimonials));