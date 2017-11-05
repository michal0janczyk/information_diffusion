# !/usr/bin/python
# -*- coding: utf-8 -*-
# Use Python 2.7+
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

# import dateutil.parser
import json
from tweepy import *
import tweepy
import pytz
import re
import sys

#######
# PARAMETERS END
#######

# Retrieve global trends.
# Other localised trends can be specified by looking up WOE IDs:
# http://developer.yahoo.com/geo/geoplanet/
# Twitter API docs: https://dev.twitter.com/rest/reference/get/trends/place
WORLD_WOE_ID = 1
US_WOE_ID = 23424977
UK_WOE_ID = 23424975
TREDNS = []

# Config Twitter API
config = {}
configPath = "/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py"
exec(open(configPath).read(), config)
# execfile(configPath, config)

# Go to http://dev.twitter.com/apps/new to create an app and get values
# for these credentials, which you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation.
# Create twitter API object
auth = OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth)

# Time zone
sgtz = pytz.timezone('US/Pacific')
utc = pytz.timezone('UTC')

#######
# PARAMETERS END
#######

trendsAPI = api.trends_place(23424977)
# trendsAPI is a list with only one element in it,
# which is a dict which we'll put in data.
dictTrends = trendsAPI[0]
trends = dictTrends['trends']

for iT in trends:
    TREDNS = "%s" % iT['name']
    print(TREDNS)

reTrends = re.compile('|'.join(TREDNS).lower())
reLexically = re.compile(r'([A-Z][A-Z]\d+)')
reRetweets = re.compile(r'^RT\s')

enc = lambda x: x.encode('latin1', errors='ignore')


class NewStreamListener(tweepy.StreamListener):
    def __init__(self, api=None):
        self.api = api or API()

    def _run(self):
        # Authenticate
        url = "https://%s%s" % (self.host, self.url)

        # Connect and process the stream
        error_counter = 0
        resp = None
        exception = None
        while self.running:
            if self.retry_count is not None:
                if error_counter > self.retry_count:
                    # quit if error count greater than retry count
                    break
            try:
                auth = self.auth.apply_auth()
                resp = self.session.request(
                    'POST',
                    url,
                    data=self.body,
                    timeout=self.timeout,
                    stream=True,
                    auth=auth,
                    verify=self.verify)
                if resp.status_code != 200:
                    if self.listener.on_error(resp.status_code) is False:
                        break
                    error_counter += 1
                    if resp.status_code == 420:
                        self.retry_time = max(self.retry_420_start,
                                              self.retry_time)
                    sleep(self.retry_time)
                    self.retry_time = min(self.retry_time * 2,
                                          self.retry_time_cap)
                else:
                    error_counter = 0
                    self.retry_time = self.retry_time_start
                    self.snooze_time = self.snooze_time_step
                    self.listener.on_connect()
                    self._read_loop(resp)
            except (Timeout, ssl.SSLError) as exc:
                # This is still necessary, as a SSLError can actually be
                # thrown when using Requests
                # If it's not time out treat it like any other exception
                if isinstance(exc, ssl.SSLError):
                    if not (exc.args and 'timed out' in str(exc.args[0])):
                        exception = exc
                        break
                if self.listener.on_timeout() is False:
                    break
                if self.running is False:
                    break
                sleep(self.snooze_time)
                self.snooze_time = min(
                    self.snooze_time + self.snooze_time_step,
                    self.snooze_time_cap)
            except Exception as exc:
                exception = exc
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        if resp:
            resp.close()

        self.new_session()

        if exception:
            # call a handler first so that the exception can be logged.
            self.listener.on_exception(exception)
            raise

    def on_error(self, status):
        print('status: %s' % status)
        if status_code == 420:
            # Returning False in on_data disconnects the stream
            return False

    def on_data(self, data):
        tweet = json.loads(data)

        if not tweet['user']:
            print('No user data - ignoring tweet.')
            return True

        user = enc(tweet['user']['name'])
        text = enc(tweet['text'])

        # Ignore text that doesn't contain one of the keywords
        matchesKeywords = re.search(reTrends, text.lower()).decode('utf-8')
        if not matchesKeywords:
            return True

        # ignore retweets
        if re.search(reRetweets, text):
            return True

        userLocation = enc(tweet['user']['location'])
        source = enc(tweet['source'])
        createTime = dateutil.parser.parse(enc(tweet['created_at']))

        # localize time
        timeZone = utc.normalize(createTime)
        localTime = createTime.astimezone(sgtz)
        tmstr = localTime.strftime("%Y%m%d-%H:%M:%S")

        # append the hourly tweet file
        with open('tweets-%s.data' % tmstr.split(':')[0], 'a+') as f:
            f.write(data)

        geoPoint = tweet['geo']
        if geoPoint and geoPoint['type'] == 'Point':
            # collect location
            coordinatesPoint = geoPoint['coordinates']
            line = re.search(reLexically, text)
            if line:
                with open('twitter_data.csv', 'a+') as mrtgeo:
                    print("Found geo coords for (%s) '%s': (%f, %f)\n" %
                          (line.group(), matchesKeywords.group(),
                           coordinatesPoint[1], coordinatesPoint[0]))
                    mrtgeo.write("%f\t%f\t%s\t%s\n" %
                                 (coordinatesPoint[1], coordinatesPoint[0],
                                  matchesKeywords.group(), line.group()))

        # Print summary of tweet
        print('%s\n%s\n%s\n%s\n%s\n\n ----------------\n' %
              (user, userLocation, source, tmstr, text))
        return True


def main():
    print(api.me().name)
    twitterListener = NewStreamListener()
    stream = Stream(auth, twitterListener, timeout=60)
    print("Listening to filter stream...")
    stream.filter(track=TREDNS)


if __name__ == '__main__':
    main()
