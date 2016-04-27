from flask import Flask, render_template, request, redirect, jsonify, make_response, session
import numpy as np
import sys,urllib,json,time,re,random,string
import os,base64,requests
from datetime import date
from operator import itemgetter

stateKey = 'spotify_auth_state'

def generateRandomString(N):
	possible = string.ascii_uppercase + string.digits + string.ascii_lowercase
	return ''.join(random.SystemRandom().choice(possible) for _ in range(N))

# product_model = dill.load(open('static/recommender/cbr_model.p','rb'))

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

def sumSessionCounter():
	try:
		session['counter'] += 1
	except KeyError:
		session['counter'] = 1

@app.route('/page1')
def p1():
	sumSessionCounter()
	return str(session['counter'])

@app.route('/page2')
def p2():
	sumSessionCounter()
	session['counter'] = session['counter']+1
	return str(session['counter'])

@app.route('/')
def index():
	return render_template('index.html',status="Ribbon Gift Curation")


@app.route('/login',methods=['GET','POST'])
def login():
	state = generateRandomString(16)
	scope = 'user-read-private user-read-email'
	params ={'state':state,'scope':scope,'response_type':'code','client_id':app.config['SPOTIFY_CLIENT_ID'],'redirect_uri':app.config['REDIRECT_URI']}

	response = make_response(redirect('https://accounts.spotify.com/authorize?'+urllib.urlencode(params)))
	response.set_cookie(stateKey, state)
	sys.stdout.flush()



	return response


@app.route('/callback',methods=['GET','POST'])
def callback():
	code = request.args.get('code')
	state = request.args.get('state')
	storedState = request.cookies.get(stateKey)

	if state is None or state != storedState:
		return redirect('/#error=state_mismatch')
	else:
		url = 'https://accounts.spotify.com/api/token'

		values = {'grant_type' : 'authorization_code','redirect_uri':app.config['REDIRECT_URI'],'code':code}
		headers = {'Authorization': 'Basic ' + base64.b64encode(app.config['SPOTIFY_CLIENT_ID'] + ':' + app.config['SPOTIFY_CLIENT_SECRET'])}
		try:
			r = requests.post(url, data=values, headers=headers)
			D = json.loads(r.text)
			access_token = D['access_token']
			refresh_token = D['refresh_token']

			# session['access_token'] = access_token
			response = make_response(redirect('/#'+urllib.urlencode({'access_token':access_token,'refresh_token':refresh_token})))
			response.set_cookie(stateKey, '', expires=0)

			return response
		except requests.exceptions.RequestException as e:    # This is the correct syntax
			print e
			return redirect('/#error=invalid_token')


	return 'called back'


if __name__ == '__main__':
	app.run()
