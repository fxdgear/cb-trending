# Setup

Prerequisites: Your machine should already have Python 2.7.x (including [virtualenv](http://www.virtualenv.org/en/latest/)) and Redis 2.x.

1. Download the archive of the master branch from GitHub.
	- If you're running Redis on anything but the standard port (or already accumulated data within the default store), check and modify the configuration at the top of `app.py`.
2. Unarchive and `cd` into the root of the project directory. From the command line, on *nix-like environments, install the environment and run the server locally:
		
		virtualenv venv --distribute
		source venv/bin/activate
		pip install -r requirements.txt
		python app.py

3. Double-check Redis is running on your local machine.
4. Also at the command line, populate the data store:
	
		python populate.py gizmodo.com avc.com someecards.com
		
	Run this command at least twice, 5-20 seconds apart. (The further apart, the more interesting the results. See the note below.)
	
5. Download and use an HTTP request simular like [Postman](https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en) to test the API (or enjoy the raw data in any Web browser): [http://127.0.0.1:5000/api/1/trending?host=gizmodo.com](http://127.0.0.1:5000/api/1/trending?host=gizmodo.com)

# API

## Trending (/api/1/trending)
### GET
- Required parameters: `host`
- Optional parameters: `sort=(desc|asc)`, `trend=(increasing|decreasing)`, `limit=N`

To get the 10 most trending pages from Gizmodo:

	GET /api/1/trending?host=gizmodo.com&sort=desc&trend=increasing&limit=10
	
This will return the results of a comparison between the last two data sets `POST`ed to the API.

### POST
- Required data: `host`, `pages` (JSON)

Post the current page, title, and visitor data:
	
	POST /api/1/trending
	
(Don't do this by hand! Let `populate.py` do this for you.)

# Notes

> For bonus points, discuss why this is bad and implement a better one that is more useful to a Chartbeat user.

Trends over very small intervals may not representative of trends over larger intervals (just like a small sample size can skew a survey). Running `populate.py` at intervals further apart (e.g., 1 minute, 5 minutes) produces more dramatic results, since the API computes the difference between the last two concurrent user values. You could also run the simulation just as frequently, and modify the Redis LRANGE retrieval in `app.py` to retrieve a larger list, and then compute the difference between the first and last of that list.