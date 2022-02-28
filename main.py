''' 
Long Mach
A RESTful API
'''

#For boats
from google.cloud import datastore
import constants
import job
import contact
import user

#For OAuth 2.0
import json
import uuid
import flask
import requests
import os

#libraries
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from flask import render_template, request, redirect, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests

from user import users_post, user_exist

from helper import verify_token

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret_28219897965-jeqt0p1igsicv2mcfr5cni309cia1agb.apps.googleusercontent.com.json"

# This OAuth 2.0 access scope allows for access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']
API_SERVICE_NAME = 'people'
API_VERSION = 'v1'

app = flask.Flask(__name__)
app.register_blueprint(job.bp)
app.register_blueprint(user.bp)
app.register_blueprint(contact.bp)
client = datastore.Client()


url = "https://jobtracker-341220.uw.r.appspot.com/"

app.secret_key = str(uuid.uuid4()) 

REDIRECT_URI = 'https://jobtracker-341220.uw.r.appspot.com/oauth'
#REDIRECT_URI = 'http://localhost:8080/oauth'

@app.route('/')
def index():
    return redirect(REDIRECT_URI, code=302)

@app.route('/oauth')
def test():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  people_service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  profile = people_service.people().get(resourceName='people/me', personFields='names').execute()

  names = profile['names'][0]
  firstName = names['givenName']
  lastName = names['familyName']

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  
  flask.session['credentials'] = credentials_to_dict(credentials)
  
  #register the user to database
  userID = verify_token(flask.session['credentials']['id_token'])
  
  #check if user exists
  result = user_exist(userID)
  if not result:
    users_post(userID, firstName, lastName)

  result = {
    "first_name": firstName,
    "last_name": lastName,
    "jwt": flask.session['credentials']['id_token'],
    "unique_ID": userID
  }

  response = jsonify(result)
  response.headers.add('Access-Control-Allow-Origin', '*')
  
  return (response, 200)

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes,
          'id_token': credentials.id_token}

def person_to_dict(person):
  return {'firstName': person.names.givenName}


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run(host='0.0.0.0', port=8080, debug=True)
  url = "http://localhost:8080/"
else:
  url = "https://jobtracker-341220.uw.r.appspot.com/"