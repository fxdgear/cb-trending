#!/usr/bin/env python

from flask import Flask, jsonify, request
import json
import redis

config = {
		'redis': {
				'server': '127.0.0.1',
				'port': 6379,
				'db': 0
			}
	}

app = Flask(__name__)

r = redis.StrictRedis(host=config['redis']['server'],
	port=config['redis']['port'],
	db=config['redis']['db'])

class Site:
	def __init__(self, host, store):
		self.host = host
		self.store = store
		self.pages = self.loadPages()
	
	def loadPages(self):
		return self.store.lrange('sites/' + self.host, 0, -1)
	
	def checkPage(self, page):
		return (page in self.pages)

	def addPage(self, page, title):
		self.pages.append(page)
		self.store.set('pages/titles/' + self.host + page, title)
		return self.store.rpush('sites/' + self.host, page)

class Concurrents:
	trends = ['increasing', 'decreasing']
	sorts = ['desc', 'asc']
	
	def __init__(self, site):
		self.site = site
			
	def post(self, page, title, count):
		if not self.site.checkPage(page):
			self.site.addPage(page, title)
		
		return self.site.store.rpush('pages/concurrents/' + self.site.host + page, count)

	def get(self, limit=None, sort='desc', trend=None):
		pages_trend = [] 
		
		for page in self.site.pages:
			concurrents = self.site.store.lrange('pages/concurrents/' + self.site.host + page, -2, -1)
			
			if len(concurrents) < 2:
				continue
			
			diff = int(concurrents[0]) - int(concurrents[1])

			if trend == 'increasing' and diff <= 0:
				continue
			elif trend == 'decreasing' and diff >= 0:
				continue
			
			pages_trend.append((diff, page))
		
		if sort == 'desc':
			reverse = True
		else:
			reverse = False

		pages_trend.sort(reverse=reverse)
		
		if limit > 0:
			pages_trend = pages_trend[:limit]
		
		pages_trend_complete = []

		for page in pages_trend:
			pages_trend_complete.append({
				'i': self.site.store.get('pages/titles/' + self.site.host + page[1]),
				'path': page[1],
				'change': page[0]
			})

		return pages_trend_complete

@app.before_request
def check_redis():
	try:
		r.ping()
	except Exception as e:
		raise Exception('Check Redis server configuration in app.py ({message})'.format(message=str(e)))

@app.route('/api/1/trending', methods=['POST'])
def concurrents_post():
	if 'host' not in request.form:
		raise Exception('Missing "host" attribute')
	if 'pages' not in request.form:
		raise Exception('Missing "pages" attribute')
	
	print request.form['pages']
	pages = json.loads(request.form['pages'])

	site = Site(request.form['host'], r)
	concurrents = Concurrents(site)

	for page in pages:
		concurrents.post(page['path'], page['i'], page['visitors'])
	
	return jsonify(status=200, count=len(pages))

@app.route('/api/1/trending', methods=['GET'])
def concurrents_get():
	get_kwargs = {}
	
	if 'host' not in request.args:
		raise Exception('Missing "host" attribute')

	if 'limit' in request.args:
		get_kwargs['limit'] = int(request.args['limit'])

	if 'trend' in request.args:
		get_kwargs['trend'] = request.args['trend']
	
	if 'sort' in request.args:
		get_kwargs['sort'] = request.args['sort']
	
	site = Site(request.args['host'], r)
	concurrents = Concurrents(site)
	pages = concurrents.get(**get_kwargs)
	
	return jsonify(status=200, pages=pages, count=len(pages))

@app.errorhandler(500)
def exception_response_500(e):
	return jsonify(status=500, error=str(e))

@app.errorhandler(404)
def exception_response_404(e):
	return jsonify(status=404, error='No endpoint exists here')

if __name__ == '__main__':
	#app.debug = True
	app.run()
