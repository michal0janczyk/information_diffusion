"""
  Get live tweets and save to disk
"""

import os
import datetime
from twitter import Twitter, OAuth

RAW_TWEET_DIR = 'raw_tweet'

# maybe create raw_tweet dir
if not os.path.exists(RAW_TWEET_DIR):
    os.makedirs(RAW_TWEET_DIR)

# retrieve credentials
# twitter dev api
config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)

# Create twitter API object
api = Twitter(auth=OAuth(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"],
                         config["CONSUMER_KEY"], config["CONSUMER_SECRET"]))


def datetime_filename(prefix='output_'):
    outputName = prefix + '{:%Y%m%d%H%M%S}utc.txt'.format(datetime.datetime.utcnow())
    return outputName


def scrape(tweets_per_file=10000):
    f = open(datetime_filename(prefix='{0}/en_tweet_'.format(RAW_TWEET_DIR)), 'w')
    tweet_count = 0
    try:
        for line in api.GetStreamSample():
            if 'text' in line and line['lang'] == u'en':
                text = line['text'].encode('utf-8').replace('\n', ' ')
                f.write('{}\n'.format(text))
                tweet_count += 1
                if tweet_count % tweets_per_file == 0:  # start new batch
                    f.close()
                    f = open(datetime_filename(prefix=RAW_TWEET_DIR+'/en_tweet_'), 'w')
                    continue
    except KeyboardInterrupt:
        print 'Twitter stream collection aborted'
    finally:
        f.close()
        return tweet_count


def main():

    tweet_count = scrape(100)
    print 'A total of {} tweets collected'.format(tweet_count)


if __name__ == '__main__':
    main()
