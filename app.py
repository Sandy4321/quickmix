from flask import Flask, render_template, request, redirect, jsonify, make_response, session
from flask.ext.basicauth import BasicAuth
import numpy as np
import sys,urllib,json,time,re,random,string,math
import os,base64,requests
from datetime import date
from operator import itemgetter
import gensim
from models import Playlist,Track

stateKey = 'spotify_auth_state'

def generateRandomString(N):
	possible = string.ascii_uppercase + string.digits + string.ascii_lowercase
	return ''.join(random.SystemRandom().choice(possible) for _ in range(N))

track_model = gensim.models.Word2Vec.load('static/w2v/sample_shuffle2.w2v')

def validateTracks(tracks):
	output = []
	for track in tracks:
		if 'T_'+track['id'] in track_model:
			output.append(track)
	return output


def sampleTracks(tracks,n):
	output = []
	spent_artists = {}

	random.shuffle(tracks)
	k = 0
	while k < n:
		try:
			t = tracks.pop()
			if t['artist'] in spent_artists:
				continue
			else:
				output.append(t['id'])
				spent_artists[t['artist']] = 0
				k += 1
		except:
			print 'not enough songs!'
			sys.stdout.flush()
			break
	return output

def buildPlaylist(tracks,activity='run',n_songs=15,n_influencers=5,validate=True):
	running_sample_size = 15
	plist = []
	if validate:
		tracks = validateTracks(tracks)


	tracksSampled = sampleTracks(tracks,n_influencers)

	n_influencers = len(tracksSampled) ## must be as many tracks as influencers
	
	tracks_per_track = int(math.ceil(1.*n_songs/n_influencers)) ## number of tracks to pull per influencer

	for track in tracksSampled:
		results = [{'id':w[0][2:],'score':w[1],'influencer':track} for w in track_model.most_similar(positive=[activity,'T_'+track],topn=100) if (re.match('T_',w[0]))]
		plist.extend(random.sample(results[:running_sample_size],tracks_per_track))
	output = {'playlist':plist[:n_songs],'influencers':tracksSampled}
	return output





app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

basic_auth = BasicAuth(app)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
	state = generateRandomString(16)
	scope = 'user-top-read user-read-email playlist-modify-public playlist-modify-private'
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



@app.route('/api/build',methods=['POST'])
def build():
	tracks = request.json['tracks']
	t = time.time()
	data = buildPlaylist(tracks,validate=True)
	print time.time()-t
	sys.stdout.flush()

	return jsonify({'status':'ok','data':data})

@app.route('/api/validate',methods=['POST'])
def validate():
	return jsonify({'status':'ok','tracks':validateTracks(data['tracks'])})

if __name__ == '__main__':
	app.run()
