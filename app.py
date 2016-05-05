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
category_map = {'chill':['sleep','relax','focus'],'party':['pregame','dance','late_night'],'workout':['warm_up','gym','cardio'],'hangout':['dinner','feel_good','bbq']}

def categorizeTracks(tracks,category,ntracks=5):
	category_results = {}
	for subcat in category_map[category]:
		scores = []
		used_artists = {}
		track_num = 0
		for track in tracks:
			track_score = track_model.similarity('T_'+track['id'],subcat)
			if track['artist'] not in used_artists:
				scores.append({'score':track_score,'id':track['id'],'artist':track['artist']})
				used_artists[track['artist']] = (track_score,track_num)
				track_num += 1
			else:
				if track_score > used_artists[track['artist']][0]:
					old_track_num = used_artists[track['artist']][1]
					used_artists[track['artist']] = (track_score,old_track_num)
					scores[old_track_num] = {'score':track_score,'id':track['id'],'artist':track['artist']}

		category_results[subcat] = sorted(scores, key=itemgetter('score'), reverse=True)[:ntracks]
	return category_results

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

@app.route('/tune')
def tune():
	pl_type = request.args.get('pl');

	if pl_type == 'chill':
	    tuners = ["Sleep","Relax","Focus"];
	elif pl_type == 'party':
		tuners = ["Pre-game","Dance","Late Night"];
	elif pl_type == 'workout':
		tuners = ["Warm Up","Gym","Cardio"];
	elif pl_type == 'hangout':
		tuners = ["Dinner","Feel Good","BBQ"];
	else:
		tuners = ["","",""];

	return render_template('tune.html', type=pl_type, tuners=tuners);

@app.route('/playlist')
def pl():
	return render_template('playlist.html')

@app.route('/login',methods=['GET','POST'])
def login():
	state = generateRandomString(16)
	pl = request.args.get('pl')

	scope = 'user-top-read user-read-email playlist-modify-public playlist-modify-private'
	params ={'state':state,'scope':scope,'response_type':'code','client_id':app.config['SPOTIFY_CLIENT_ID'],'redirect_uri':app.config['REDIRECT_URI']}

	response = make_response(redirect('https://accounts.spotify.com/authorize?'+urllib.urlencode(params)))
	response.set_cookie(stateKey, state)
	response.set_cookie('pl', pl)

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
			pl = request.cookies.get('pl')

			# session['access_token'] = access_token
			response = make_response(redirect('/tune?'+urllib.urlencode({'access_token':access_token,'refresh_token':refresh_token,'pl':pl})))
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
	tracks = request.json['tracks']
	category = request.json['category']

	validTracks = validateTracks(tracks)
	relevantTracks = categorizeTracks(validTracks,category)

	return jsonify({'status':'ok','tracks':relevantTracks})

if __name__ == '__main__':
	app.run()
