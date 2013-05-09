#!/usr/bin/env python

import argparse, requests

parser = argparse.ArgumentParser(description='Submit trending POST requests with Chartbeat toppages data.')
parser.add_argument('hosts', metavar='DOMAIN NAME', type=str, nargs='+', help='hosts to gather (e.g., "gizmodo.com")')
args = parser.parse_args()

for host in args.hosts:
	print 'Retrieving {host}...'.format(host=host)

	params = {
		'apikey': '317a25eccba186e0f6b558f45214c0e7',
		'host': host,
		'limit': '100',
	}
	
	r = requests.get('http://api.chartbeat.com/live/toppages', params=params)

	data = {
		'host': host,
		'pages': r.text
	}

	r2 = requests.post('http://127.0.0.1:5000/api/1/trending', data=data)
	info = r2.json()

	if info['status'] == 200:
		print 'Successfully posted {host} to local server.'.format(host=host)
	else:
		print 'Failed to post {host} to local server ({error}).'.format(host=host, error=info['error'])
