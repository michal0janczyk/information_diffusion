#!/usr/bin/python
# -*- coding: utf-8 -*-
# Use Python 2.7+
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

import dateutil.parser
from twitter import *
from tweepy import *
import re

# XXX: Go to http://dev.twitter.com/apps/new to create an app and get values
# for these credentials, which you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation.

config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)
# create twitter API object
twitter = Twitter(
    auth=OAuth(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"],
               config["CONSUMER_KEY"], config["CONSUMER_SECRET"]))

# retrieve global trends.
# other localised trends can be specified by looking up WOE IDs:
#   http://developer.yahoo.com/geo/geoplanet/
# twitter API docs: https://dev.twitter.com/rest/reference/get/trends/place

WORLD_WOE_ID = 1
US_WOE_ID = 23424977
UK_WOE_ID = 23424975

results = twitter.trends.place(_id=US_WOE_ID)
for location in results:
    for trend in location["trends"]:
        res = " - %s" % trend["name"]
        print res
        with open('tweets_trends.data', 'a') as f:
            f.write(res)
