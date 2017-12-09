#!/usr/bin/env python

# Copyright 2007-2016 The Python-Twitter Developers

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ----------------------------------------------------------------------

# This file demonstrates how to track mentions of a specific set of users in
# english language and archive those mentions to a local file. The output
# file will contain one JSON string per line per Tweet.

# To use this example, replace the W/X/Y/Zs with your keys obtained from
# Twitter, or uncomment the lines for getting an environment variable. If you
# are using a virtualenv on Linux, you can set environment variables in the
# ~/VIRTUALENVDIR/bin/activate script.

# If you need assistance with obtaining keys from Twitter, see the instructions
# in doc/getting_started.rst.

import os
import json

import tweepy
import pprint
# Either specify a set of keys here or use os.getenv('CONSUMER_KEY') style
# assignment:

# Users to watch for should be a list. This will be joined by Twitter and the
# data returned will be for any tweet mentioning:
# @twitter *OR* @twitterapi *OR* @support.
USERS = ['@twitter']

# Languages to filter tweets by is a list. This will be joined by Twitter
# to return data mentioning tweets only in the english language.
LANGUAGES = ['en']
config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)

# Since we're going to be using a streaming endpoint, there is no need to worry
# about rate limits.
# Create twitter API object

auth = tweepy.OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth, wait_on_rate_limit=True)
me = api.me()

pprint.pprint(api.rate_limit_status())

def main():
    while True:
        try:
            for follower in tweepy.Cursor( api.followers, id=me.id, count=50 ).items():
                print follower
                for friend in tweepy.Cursor( api.friends, follower.id ).items():
                    if friend.name != me.name:
                        api.create_friendship( id=friend.id )
        except tweepy.TweepError, e:
            print "TweepError raised, ignoring and continuing."
            print e
            continue

    # with open('output.txt', 'a') as f:
    #     # api.GetStreamFilter will return a generator that yields one status
    #     # message (i.e., Tweet) at a time as a JSON dictionary.
    #     for follower in tweepy.Cursor( api.followers, id=me, count=50 ).items():
    #         print follower
    #         #for line in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
    #         f.write(json.dumps(follower))
    #         f.write('\n')


if __name__ == '__main__':
    main()