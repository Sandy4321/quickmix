from flask import Flask, render_template, request, redirect, jsonify
import numpy as np
import sys,urllib2,json,time,re
from datetime import date
from operator import itemgetter

# product_model = dill.load(open('static/recommender/cbr_model.p','rb'))

app = Flask(__name__)

app.config['DEBUG'] = True




@app.route('/')
def index():
	return render_template('index.html',status="Ribbon Gift Curation")


@app.route('/api/cluster',methods=['GET','POST'])
def cluster():
	print 'cluster'
	if request.method == 'POST':

		X = [request.json['user_data']]

		user_cluster_stats = assign_cluster(X)
		print user_cluster_stats,type(user_cluster_stats)

		return jsonify({'status':'ok','data':user_cluster_stats})
	else:
		return jsonify({'status':'error'})


@app.route('/api/recommend',methods=['GET','POST'])
def recommender():
	if request.method == 'POST':
		product_type = request.json['product_type']

		X = [request.json['survey']]
		if product_type == 'recommend':
			products = recommend(X)
		else:
			products = allstars(X)

		gift_data =  load_gift_data([v[1] for v in products['data']])
		for stars,product,average_rating in products['data']:
			gift_data['results'][product]['predicted_rating'] = min(5.,stars)
		
		gift_data_list = [gift_data['results'][_d] for _d in gift_data['results']]
		gift_data_list = sorted(gift_data_list, key=itemgetter('predicted_rating'), reverse=True)
		

		return jsonify({'status':'ok','data':gift_data_list})
	else:
		return jsonify({'status':'error'})


if __name__ == '__main__':
	app.run()
