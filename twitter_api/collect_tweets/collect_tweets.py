#!/usr/bin/python
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import re
import sys
import json
import dateutil.parser
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

config = {}
configPath = "/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py"
exec(open(configPath).read(), config)

auth = OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])

sgtz = timezone('Asia/Singapore')
utc = pytz.timezone('UTC')

api = tweepy.API(auth)
trendsAPI = api.trends_place(23424977)
# trendsAPI is a list with only one element in it,
# which is a dict which we'll put in data.
dictTrends = trendsAPI[0]
trends = dictTrends['trends']


def get_hashtags(listOfTrends, order=False):
    tags = set([item.strip("#.,-\"\'&*^!") for item in listOfTrends.split() if (item.startswith("#") and len(item) < 256)])
    return sorted(tags) if order else tags

def strip_links(text):
    link_regex    = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links         = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], ', ')
    return text

def strip_all_entities(text):
    entity_prefixes = ['@','#']
    for separator in  string.punctuation:
        if separator not in entity_prefixes :
            text = text.replace(separator,' ')
    words = []
    for word in text.split():
        word = word.strip()
        if word:
            if word[0] not in entity_prefixes:
                words.append(word)
    return ' '.join(words)

STATIONS = [
        'Admiralty MRT',
        'Aljunied MRT',
        'Ang Mo Kio MRT',
        'Bartley MRT',
        'Bayfront MRT',
        'Bedok MRT',
        'Bishan MRT',
        'Bras Basah MRT',
        'Botanic Gardens MRT',
        'Braddell MRT',
        'Bukit Batok MRT',
        'Bukit Gombak MRT',
        'Caldecott MRT',
        'Choa Chu Kang MRT',
        'Boon Keng MRT',
        'Boon Lay MRT',
        'Buangkok  MRT',
        'Bugis MRT',
        'Buona Vista MRT',
        'Changi Airport MRT',
        'Chinatown MRT',
        'Clarke Quay MRT',
        'Chinese Garden MRT',
        'City Hall MRT',
        'Clementi MRT',
        'Commonwealth MRT',
        'Dakota MRT',
        'Dhoby Ghaut MRT',
        'Dover MRT',
        'Esplanade MRT',
        'Eunos MRT',
        'Expo MRT',
        'Farrer Park MRT',
        'Farrer Road MRT',
        'HarbourFront MRT',
        'Haw Par Villa MRT',
        'Holland Village MRT',
        'Hougang MRT',
        'Joo Koon MRT',
        'Jurong East MRT',
        'Kallang MRT',
        'Kovan MRT',
        'Kembangan MRT',
        'Kent Ridge MRT',
        'Khatib MRT',
        'Kranji MRT',
        'Lakeside MRT',
        'Labrador Park MRT',
        'Lavender MRT',
        'Little India MRT',
        'Lorong Chuan MRT',
        'Marina Bay MRT',
        'Marsiling MRT',
        'MacPherson MRT',
        'Marymount MRT',
        'Mountbatten MRT',
        'Newton MRT',
        'Nicoll Highway MRT',
        'one-north MRT',
        'Novena MRT',
        'Orchard MRT',
        'Outram Park MRT',
        'Pasir Ris MRT',
        'Pasir Panjang MRT',
        'Paya Lebar MRT',
        'Pioneer MRT',
        'Potong Pasir MRT',
        'Promenade MRT',
        'Punggol MRT',
        'Queenstown MRT',
        'Raffles Place MRT',
        'Redhill MRT',
        'Sembawang MRT',
        'Sengkang MRT',
        'Serangoon MRT',
        'Simei MRT',
        'Somerset MRT',
        'Stadium MRT',
        'Tampines MRT',
        'Tai Seng MRT',
        'Tanah Merah MRT',
        'Tanjong Pagar MRT',
        'Tiong Bahru MRT',
        'Telok Blangah MRT',
        'Toa Payoh MRT',
        'Woodlands MRT',
        'Woodleigh MRT',
        'Yew Tree MRT',
        'Yio Chu Kang MRT',
        'Yishun MRT'
        ]
regex = re.compile('|'.join(STATIONS).lower())
linenum_re = re.compile(r'([A-Z][A-Z]\d+)')
retweets_re = re.compile(r'^RT\s')

enc = lambda x: x.encode('latin1', errors='ignore')

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
            # collect location of mrt station
            coords = geo['coordinates']
            ln = re.search(linenum_re, text)
            if ln:
                with open('mrt_station_locations.csv', 'a+') as mrtgeo:
                    print("Found geo coords for MRT Station (%s) '%s': (%f, %f)\n" %
                            (ln.group(), matches.group(), coords[1], coords[0]))
                    mrtgeo.write("%f\t%f\t%s\t%s\n" %
                            (coords[1], coords[0], matches.group(), ln.group()))

        # print summary of tweet
        print('%s\n%s\n%s\n%s\n%s\n\n ----------------\n' % (user, location, source, tmstr, text))


        return True

    def on_error(self, status):
        print('status: %s' % status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    stream = Stream(auth, l, timeout=60)

    print("Listening to filter stream...")
    for t in trends:
        strip_all_entities(strip_links(t))

    print(t)

    print("\n".join(get_hashtags(trends, True)))
    # stream.filter(track=TREDNS)