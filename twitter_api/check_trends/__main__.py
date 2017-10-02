#!/usr/bin/python

from twitter import *
import dateutil.parser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import re

# XXX: Go to http://dev.twitter.com/apps/new to create an app and get values
# for these credentials, which you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information 
# on Twitter's OAuth implementation.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
CONSUMER_KEY = '2zqaRrlnTi7AQrk6gD1lqsoqo'
CONSUMER_SECRET = 'EvGH0LPCjC7lyjt4uszT4s2lQmnd2om7rArDftYibtJ6yoRl8z'

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
ACCESS_TOKEN = '4415191522-OuA6gF4Zub4c0bTn4UwunHO2GSH8w1aYEdY9ZHf'
ACCESS_TOKEN_SECRET = 'N1jVLY2szClSxJ0zIpkREThkuSWYiiY3ItNKxTN8MJydx'


#-----------------------------------------------------------------------
# twitter-trends
#  - lists the current global trending topics
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# load our API credentials 
#-----------------------------------------------------------------------
config = {}
execfile("config.py", config)

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
twitter = Twitter(
		        auth = OAuth(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"], config["CONSUMER_KEY"], config["CONSUMER_SECRET"]))


#-----------------------------------------------------------------------
# retrieve global trends.
# other localised trends can be specified by looking up WOE IDs:
#   http://developer.yahoo.com/geo/geoplanet/
# twitter API docs: https://dev.twitter.com/rest/reference/get/trends/place
#-----------------------------------------------------------------------
WORLD_WOE_ID = 1
US_WOE_ID = 23424977
UK_WOE_ID = 23424975

results = twitter.trends.place(_id = US_WOE_ID)
for location in results:
	for trend in location["trends"]:
		res = " - %s" % trend["name"]
		print res
		with open('tweets_trends.data', 'a') as f:
			f.write(res)


# for location in results:
# 	for trend in location["trends"]:

			



