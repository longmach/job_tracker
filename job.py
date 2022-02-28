import flask

#original
from flask import Blueprint, request, current_app, jsonify
from google.cloud import datastore
import json
import constants
from google.oauth2 import id_token
from google.auth.transport import requests

from helper import verify_token, return_json

encoding = 'utf-8'
client = datastore.Client()

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

url = "https://jobtracker-341220.uw.r.appspot.com/"

#CLIENT_SECRETS_FILE = "client_secret_20622882585-21t3vgioii64ufuiadvm2f30okhj2vc9.apps.googleusercontent.com.json"

''' Jobs Requests '''
@bp.route('', methods=['POST','GET'])
# Create a job
def jobs_get_post():
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
            if content["company"] and content["job_title"] and content["job_link"] and content["salary"] and content["skill"]:
                
                #create new datastore entity
                new_job = datastore.entity.Entity(key=client.key(constants.jobs))
                
                application_date = ""
                status = ""
                interview_date = ""
                address = ""

                if "application_date" in content:
                    application_date = content["application_date"]
                if "status" in content:
                    status = content["status"]
                if "interview_date" in content:
                    interview_date = content["interview_date"]
                if "address" in content:
                    address = content["address"]

                #update it with attributes from request
                new_job.update({"user_ID": userid, "company": content["company"], "job_title": content["job_title"], "job_link": content["job_link"], 
                "salary": content["salary"], "application_date": application_date, "status": status, 
                "interview_date": interview_date, "address": address, "skill": content["skill"]})

                #put it to the database
                client.put(new_job)
                
                #prepare the response
                new_job["id"] = new_job.key.id
                new_job['self'] = url + 'jobs/'+ str(new_job["id"])
                response = jsonify(new_job)
                
                #add header to the response for CORS
                response.headers.add('Access-Control-Allow-Origin', '*')
                return (response, 201)
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    
    elif request.method == 'GET':
        #fetch all jobs
        query = client.query(kind=constants.jobs)
        query.add_filter("user_ID", "=", userid)          #filter the owner according to sub in jwt
        
        results = list(query.fetch())
        
        #prepare the response
        for e in results:
            e["id"] = e.key.id
            e['self'] = url + 'jobs/'+ str(e.key.id) 
        response = jsonify(results)

        #add header to response for CORS
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)
    else:
        return return_json({"Error": "Method not recogonized"}, 405)

# Get, edit or delete a job
@bp.route('/<id>', methods=['DELETE','GET','PATCH'])
def jobs_patch_delete(id):
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
            if content["company"] and content["job_title"] and content["job_link"] and content["salary"] and content["skill"]:
                
                #try to see job_id is valid
                try:       
                    job_key = client.key(constants.jobs, int(id))
                    job = client.get(key=job_key)
                    if job["user_ID"] == userid:
                        application_date = ""
                        status = ""
                        interview_date = ""
                        address = ""

                        if "application_date" in content:
                            application_date = content["application_date"]
                        if "status" in content:
                            status = content["status"]
                        if "interview_date" in content:
                            interview_date = content["interview_date"]
                        if "address" in content:
                            address = content["address"]

                        #update job
                        job.update({"company": content["company"], "job_title": content["job_title"], "job_link": content["job_link"], 
                        "salary": content["salary"], "application_date": application_date, "status": status, 
                        "interview_date": interview_date, "address": address, "skill": content["skill"]})
                        
                        #put to database
                        client.put(job)

                        #prepare the response
                        job["id"] = job.key.id
                        job['self'] = url + 'jobs/'+ str(job["id"]) 
                        response = jsonify(job)
                        
                        #add header to the response for CORS
                        response.headers.add('Access-Control-Allow-Origin', '*')
                        return (response, 201)
                    else:
                        return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
                except: 
                    return (json.dumps({"Error": "No job with this job_id exists"}), 404)
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    
    #delete job
    elif request.method == 'DELETE':
        try:
            
            job_key = client.key(constants.jobs, int(id))
            job = client.get(key=job_key)
            if userid == job['user_ID']:
                #client.delete(job)
                client.delete(job_key)
                return return_json('',204)
            else:
                return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
        except:
            return (json.dumps({"Error": "No job with this job_id exists"}), 404)
    elif request.method == 'GET':
        try:
            job_key = client.key(constants.jobs, int(id))
            job = client.get(key=job_key)
            if userid == job['user_ID']:
                job["id"] = job.key.id
                job['self'] = url + 'jobs/'+ str(job["id"]) 
                response = jsonify(job)
                        
                #add header to the response for CORS
                response.headers.add('Access-Control-Allow-Origin', '*')
                return (response, 200)
            else:
                return return_json({"Error": "JWT is valid but job_id is owned by someone else"}, 403)
        except:
            return (json.dumps({"Error": "No job with this job_id exists"}), 404)
    else:
        return 'Method not recognized'