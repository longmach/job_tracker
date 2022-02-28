import flask

#original
from flask import Blueprint, request, current_app, make_response
from google.cloud import datastore
import json
import constants
from google.oauth2 import id_token
from google.auth.transport import requests

from helper import return_json

encoding = 'utf-8'
client = datastore.Client()

bp = Blueprint('users', __name__, url_prefix='/users')

def users_post(userID, firstName, lastName):
    new_user = datastore.entity.Entity(key=client.key(constants.users))
    new_user.update({"userID": userID, "firstName": firstName, "lastName": lastName})
    client.put(new_user)

def user_exist(id):
    query = client.query(kind=constants.users) 
    query.add_filter("userID", "=", id)          #filter the owner according to sub in jwt
    results = list(query.fetch())
    return results