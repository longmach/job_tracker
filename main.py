''' 
Long Mach
A Restful API 
'''

import re
from urllib import response
from google.cloud import datastore
from flask import Flask, make_response, request, current_app, jsonify
import json
import constants

app = Flask(__name__)
client = datastore.Client()


@app.route('/')
def index():
    return "Please navigate to /jobs to use this API"\

''' Jobs Requests '''
# Add a job or get all jobs
@app.route('/jobs', methods=['POST','GET'])
def jobs_get_post():
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    if request.method == 'POST':
        content = request.get_json()
        if content["company"] and content["job_title"] and content["job_link"]:
            new_job = datastore.entity.Entity(key=client.key(constants.jobs))
            new_job.update({"company": content["company"], "job_title": content["job_title"],
            "job_link": content["job_link"]})
            client.put(new_job)
            new_job["id"] = new_job.key.id
            new_job['self'] = url + 'jobs/'+ str(new_job["id"])
            response = jsonify(new_job)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return (response, 200)
            #return (json.dumps(new_job), 201)
            '''try: 
            if content["name"] and content["type"] and content["length"]:
                new_job = datastore.entity.Entity(key=client.key(constants.jobs))
                new_job.update({"name": content["name"], "type": content["type"],
                "length": content["length"]})
                client.put(new_job)
                new_job["id"] = new_job.key.id
                new_job['self'] = url + 'jobs/'+ str(new_job["id"]) 
                return (json.dumps(new_job), 201)
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)'''
    elif request.method == 'GET':
        query = client.query(kind=constants.jobs)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e['self'] = url + 'jobs/'+ str(e.key.id) 
        response = jsonify(results)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return (response, 200)
        #return (json.dumps(results), 200)
    else:
        return 'Method not recognized'

# Get, edit or delete a job
'''@app.route('/jobs/<id>', methods=['DELETE','GET','PATCH'])
def jobs_patch_delete(id):
    if request.method == 'PATCH':
        content = request.get_json()
        try: 
            if content["name"] and content["type"] and content["length"]:
                try:       
                    job_key = client.key(constants.jobs, int(id))
                    job = client.get(key=job_key)
                    job.update({"name": content["name"], "type": content["type"],
                "length": content["length"]})
                    client.put(job)
                    job["id"] = job.key.id
                    job['self'] = url + 'jobs/'+ str(job["id"]) 
                    return (json.dumps(job), 200)
                except: 
                    return (json.dumps({"Error": "No job with this job_id exists"}), 404)
        except:
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
    elif request.method == 'DELETE':
        try:
            #delete job
            job_key = client.key(constants.jobs, int(id))
            job = client.get(key=job_key)
            client.delete(job)
            #remove job from contact
            contact_query = client.query(kind=constants.contacts)
            contact_results = list(contact_query.fetch())
            for i in contact_results:
                if i['current_job'] == int(id):
                    i['current_job'] = None
                    client.put(i)
            return ('',204)
        except:
            return (json.dumps({"Error": "No job with this job_id exists"}), 404)
    elif request.method == 'GET':
        try:
            job_key = client.key(constants.jobs, int(id))
            job = client.get(key=job_key)
            job["id"] = job.key.id
            job['self'] = url + 'jobs/'+ str(job["id"]) 
            return (json.dumps(job), 200)
        except:
            return (json.dumps({"Error": "No job with this job_id exists"}), 404)
    else:
        return 'Method not recognized'
    '''

''' contacts Requests '''
'''# Add a contact or get all contacts
@app.route('/contacts', methods=['POST','GET'])
def contacts_get_post():
    if request.method == 'POST':
        content = request.get_json()
        try: 
            if content["number"]:
                new_contact = datastore.entity.Entity(key=client.key(constants.contacts))
                new_contact.update({"number": content["number"], "current_job": None})
                client.put(new_contact)
                new_contact["id"] = new_contact.key.id
                new_contact['self'] = url + 'contacts/' + str(new_contact["id"]) 
                return (json.dumps(new_contact), 201)
        except:
            return (json.dumps({"Error": "The request object is missing the required number"}), 400)
    elif request.method == 'GET':
        contact_query = client.query(kind=constants.contacts)
        contact_results = list(contact_query.fetch())
        for i in contact_results:
            i["id"] = i.key.id
            i['self'] = url + 'contacts/' + str(i.key.id) 
        #return dict(contact_results)
        return (json.dumps(contact_results), 200)
    else:
        return 'Method not recognized'

# get or delete a contact
@app.route('/contacts/<id>', methods=['DELETE','GET'])
def contacts_get_delete(id):
    if request.method == 'DELETE':
        try:
            contact_key = client.key(constants.contacts, int(id))
            contact = client.get(key=contact_key)
            client.delete(contact)
            return ('',204)
        except:
            return (json.dumps({"Error": "No contact with this contact_id exists"}), 404)
    elif request.method == 'GET':
        try:
            contact_key = client.key(constants.contacts, int(id))
            contact = client.get(key=contact_key)
            contact["id"] = contact.key.id
            contact['self'] = url + 'contacts/' + str(contact["id"]) 
            return (json.dumps(contact), 200)
        except:
            return (json.dumps({"Error": "No contact with this contact_id exists"}), 404)
    else:
        return 'Method not recognized'

# a job arrive or depart a contact
@app.route('/contacts/<contact_id>/<job_id>', methods=['PUT', 'DELETE'])
def arrive_put_delete(contact_id, job_id):
    if request.method == 'PUT':
        try: 
            contact_key = client.key(constants.contacts, int(contact_id))
            contact = client.get(key=contact_key)
            job_key = client.key(constants.jobs, int(job_id))
            job = client.get(key=job_key)
            if job == None:
                return (json.dumps({"Error": "The specified job and/or contact does not exist"}), 404)
            if contact['current_job'] == None:       
                contact.update({"current_job": int(job_id)})
                client.put(contact)
                return ('', 204)
            else:
                return (json.dumps({"Error": "The contact is not empty"}), 403)
        except:
            return (json.dumps({"Error": "The specified job and/or contact does not exist"}), 404)
    elif request.method == 'DELETE':
        try: 
            contact_key = client.key(constants.contacts, int(contact_id))
            contact = client.get(key=contact_key)
            job_key = client.key(constants.jobs, int(job_id))
            if contact['current_job'] == int(job_id):       
                contact.update({"current_job": None})
                client.put(contact)
                return ('', 204)
            else:
                return (json.dumps({"Error": "No job with this job_id is at the contact with this contact_id"}), 404)
        except:
            return (json.dumps({"Error": "No job with this job_id is at the contact with this contact_id"}), 404)
'''

if __name__ == '__main__':
    url = "http://localhost:8000/"
    app.run(host='0.0.0.0', port=8000, debug=True)
else:
    url = "https://project3-long-mach.ue.r.appspot.com/"
