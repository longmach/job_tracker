import flask

#original
from flask import Blueprint, request, current_app, make_response
from google.cloud import datastore
import json
import constants
from google.oauth2 import id_token
from google.auth.transport import requests

encoding = 'utf-8'
client = datastore.Client()

CLIENT_SECRETS_FILE = "client_secret_28219897965-jeqt0p1igsicv2mcfr5cni309cia1agb.apps.googleusercontent.com.json"

def verify_token(token):
    #get client_id from client_secret file
    with open(CLIENT_SECRETS_FILE) as f:
        data = json.load(f)
    client_id = data['web']['client_id']

    #verify token
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
    userid = idinfo['sub']
    return userid

def return_json(result, status_code):
    res = make_response(json.dumps(result))
    res.mimetype = 'application/json'
    res.status_code = status_code
    return res
