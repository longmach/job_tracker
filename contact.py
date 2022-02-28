''' 
Long Mach

'''

import flask

#original
from flask import Blueprint, request, current_app, jsonify
from google.cloud import datastore
import json
import constants
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import date

from helper import verify_token, return_json

encoding = 'utf-8'

client = datastore.Client()

bp = Blueprint('contacts', __name__, url_prefix='/contacts')

url = "https://jobtracker-341220.uw.r.appspot.com/"

@bp.route('', methods=['POST','GET'])
def contacts_get_post():
    # get token
    try:
        content = dict(request.headers)
        breakdown = content['Authorization'].split(' ')
        token = breakdown[1]
        userid = verify_token(token)
    except:
        return return_json({"Error": "Missing or invalid JWTs"}, 401)

    if request.method == 'POST':
        content = request.get_json()
        try: 
            #check if missing any attributes
            if content["email"] and content["name"] and content["company"] and content["position"]:
                
                #create new datastore entity
                new_contact = datastore.entity.Entity(key=client.key(constants.contacts))
                
                phone_number = ""

                if "phone_number" in content:
                    phone_number = content["phone_number"]

                #update it with attributes from request
                new_contact.update({"user_ID": userid, "email": content["email"], "name": content["name"], "company": content["company"], 
                "position": content["position"], "phone_number": phone_number})

                #put it to the database
                client.put(new_contact)
                
                #prepare the response
                new_contact["id"] = new_contact.key.id
                new_contact['self'] = url + 'contacts/'+ str(new_contact["id"])
                response = jsonify(new_contact)
                
                #add header to the response for CORS
                response.headers.add('Access-Control-Allow-Origin', '*')
                return (response, 201)
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    elif request.method == 'GET':
        #fetch all jobs
        query = client.query(kind=constants.contacts)
        query.add_filter("user_ID", "=", userid)          #filter the owner according to sub in jwt
        results = list(query.fetch())
        
        #prepare the response
        for e in results:
            e["id"] = e.key.id
            e['self'] = url + 'contacts/'+ str(e.key.id) 
        response = jsonify(results)

        #add header to response for CORS
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)
    else:
        return 'Method not recognized'

@bp.route('/<id>', methods=['PATCH','DELETE','GET'])
def contacts_get_delete(id):
    # get token
    try:
        content = dict(request.headers)
        breakdown = content['Authorization'].split(' ')
        token = breakdown[1]
        userid = verify_token(token)
    except:
        return return_json({"Error": "Missing or invalid JWTs"}, 401) 

    if request.method == 'PATCH':
        content = request.get_json()
        try:
            #check if missing any attributes
            if content["email"] and content["name"] and content["company"] and content["position"]:
                
                #try to see contact_id is valid
                try:       
                    contact_key = client.key(constants.contacts, int(id))
                    contact = client.get(key=contact_key)
                    
                    if contact["user_ID"] == userid:
                        phone_number = ""

                        if "phone_number" in content:
                            phone_number = content["phone_number"]

                        #update it with attributes from request
                        contact.update({"email": content["email"], "name": content["name"], "company": content["company"], 
                        "position": content["position"], "phone_number": phone_number})

                        #put it to the database
                        client.put(contact)
                        
                        #prepare the response
                        contact["id"] = contact.key.id
                        contact['self'] = url + 'jobs/'+ str(contact["id"])
                        response = jsonify(contact)
                        
                        #add header to the response for CORS
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return (response, 201)
                    else:
                        return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
                except: 
                    return (json.dumps({"Error": "No job with this job_id exists"}), 404) 
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    elif request.method == 'DELETE':
        try:
            contact_key = client.key(constants.contacts, int(id))
            contact = client.get(key=contact_key)
            if userid == contact['user_ID']:
                #client.delete(contact)
                client.delete(contact_key)
                return ('',204)
            else:
                return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
        except:
            return (json.dumps({"Error": "No contact with this contact_id exists"}), 404)
    elif request.method == 'GET':
        try:
            contact_key = client.key(constants.contacts, int(id))
            contact = client.get(key=contact_key)
            if userid == contact['user_ID']:
                contact["id"] = contact.key.id
                contact['self'] = url + 'contacts/' + str(contact["id"]) 
                response = jsonify(contact)
                        
                #add header to the response for CORS
                response.headers.add('Access-Control-Allow-Origin', '*')
                return (response, 200)
            else:
                return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
        except:
            return (json.dumps({"Error": "No contact with this contact_id exists"}), 404)
    else:
        return 'Method not recognized'

    