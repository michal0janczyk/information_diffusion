#!/usr/bin/python
# -*- coding: utf-8 -*-

import dateutil.parser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import re
import sys
import json
from pytz import timezone
import pytz

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
CONSUMER_KEY = '2zqaRrlnTi7AQrk6gD1lqsoqo'
CONSUMER_SECRET = 'EvGH0LPCjC7lyjt4uszT4s2lQmnd2om7rArDftYibtJ6yoRl8z'

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
ACCESS_TOKEN = '4415191522-OuA6gF4Zub4c0bTn4UwunHO2GSH8w1aYEdY9ZHf'
ACCESS_TOKEN_SECRET = 'N1jVLY2szClSxJ0zIpkREThkuSWYiiY3ItNKxTN8MJydx'

sgtz = timezone('US/Pacific')
utc = pytz.timezone('UTC')

TREDNS = [
        '#THEVOICEOFPOLAND'
        ]

regex = re.compile('|'.join(TREDNS).lower())
linenum_re = re.compile(r'([A-Z][A-Z]\d+)')
retweets_re = re.compile(r'^RT\s')

enc = lambda x: x.encode("ascii", "ignore")

class StdOutListener(StreamListener):
    def on_data(self, data):

        tweet = json.loads(data)

        if not tweet.has_key('user'):
            print 'No user data - ignoring tweet.'
            return True

        user = enc(tweet['user']['name'])
        text = enc(tweet['text'])

        # ignore text that doesn't contain one of the keywords
        matches = re.search(regex, text.lower())
        if not matches:
            return True

        # ignore retweets
        if re.search(retweets_re, text):
            return True

        location = enc(tweet['user']['location'])
        source = enc(tweet['source'])
        d = dateutil.parser.parse(enc(tweet['created_at']))

        # localize time
        d_tz = utc.normalize(d)
        localtime = d.astimezone(sgtz)
        tmstr = localtime.strftime("%Y%m%d-%H:%M:%S")

        # append the hourly tweet file
        with open('tweets-%s.data' % tmstr.split(':')[0], 'a+') as f:
            f.write(data)

        # is this a geocoded tweet?
        geo = tweet['geo']
        if geo and geo['type'] == 'Point':
            # collect location 
            coords = geo['coordinates']
            ln = re.search(linenum_re, text)
            if ln:
                with open('twitter_data.csv', 'a+') as mrtgeo:
                    print("Found geo coords for (%s) '%s': (%f, %f)\n" %
                            (ln.group(), matches.group(), coords[1], coords[0]))
                    mrtgeo.write("%f\t%f\t%s\t%s\n" %
                            (coords[1], coords[0], matches.group(), ln.group()))

        # print summary of tweet
        print('%s\n%s\n%s\n%s\n%s\n\n ----------------\n' % (user, location, source, tmstr, text))


        return True

    def on_error(self, status):
        print('status: %s' % status)

def main():

    l = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l, timeout=60)

    print("Listening to filter stream...")

    stream.filter(track=TREDNS)

if __name__ == '__main__':
	main()