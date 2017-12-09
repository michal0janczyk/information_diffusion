import codecs
import pdb
import simplejson
import glob
import json
import csv
import collections
import re
from collections import Counter


def getData():
    tweets = []
    files = ['nazi_tweets.json']

    for file in files:
        with codecs.open('/home/mike/Documents/repoo/information_diffusion/tweet_data/' + file, 'r', encoding='utf-8') as f:
            data = f.readlines()
            for line in data:
                tweet_full = simplejson.loads(line)
                tweets.append({
               'id': tweet_full[id],
                'text': tweet_full['text'].lower(),
                'label': tweet_full['Annotation'],
                'name': tweet_full['user']['name'].split()[0]
                })

    #pdb.set_trace()
    return tweets

params = {
    'data_files': '/home/mike/Documents/repoo/information_diffusion/tweet_data/nazi_tweets.json',
    'geo_output': 'dnd_tip_tweets_geo.csv',
    'text_output': 'dnd_tip_tweets.txt',
    'json_output': 'dnd_tip_tweets.json',
    'bff_output': 'dnd_tip_bffs.csv',
    'csv_output': 'dnd_tip_tweets.csv',
    'sqlite3_output': 'dnd_tip_tweets.sqlite3',
    'html_output': 'dnd_tip_tweets.html',
    'twitter_user_id': 'slyflourish',
}


def load_data (files):
    items = []
    files = glob.glob( files )
    for file in files:
        with open( file ) as f:
            d = f.readlines()[1:]  # Twitter's JSON first line is bogus
            d = "".join( d )
            j = json.dumps( d )
            for tweet in j:
                r = 1
                # Comment out above and uncomment below to filter tweets by an re match.
                #r = re.compile("^#dnd tip:").match(tweet['text'])
                if r:
                    items.append( tweet )
    return sorted( items, key=lambda k: k['id'] )


def get_bffs (d):
    words = []
    for item in d:
        item_words = item['text'].split()
        for word in item_words:
            if '@' in word:
                words.append( word.replace( ':', '' ).lower().encode( 'utf-8' ) )
    return collections.Counter( words ).most_common( 50 )


def get_bigrams (d):
    words = []
    for item in d:
        item_words = re.findall( '\w+', item['text'] )
        words += item_words
    output = (Counter( zip( words, words[1:] ) ).most_common( 100 ))
    for item in output:
        print item


def get_csv_output (d):
    output = [('id', 'date', 'tweet')]
    for item in d:
        output.append( (
            item['id_str'],
            item['created_at'],
            item['text'].encode( 'utf-8' )
        ) )
    return output


def get_geo (d):
    output = [('date', 'tweet', 'lat', 'long')]
    for item in d:
        try:
            lat = item['geo']['coordinates'][0]
            long = item['geo']['coordinates'][1]
            date = item['created_at']
            text = item['text'].encode( 'utf-8' )
            output.append( (date, text, lat, long) )
        except:
            error = "no coordinates"
    return output



def write_text (tweets, output_file):
    text_output = ''
    for item in tweets:
        text_output += '%s\n%s\n%s\n\n'%(item['id'],
                                         item['created_at'],
                                         item['text'])
    with open( output_file, "w" ) as f:
        f.write( text_output.encode( 'utf-8' ) )


def write_csv (d, csv_file):
    with open( csv_file, 'w' ) as f:
        writer = csv.writer( f )
        writer.writerows( d )


def write_json (json_data, output_file):
    with open( output_file, 'w' ) as f:
        f.write( json.dumps( json_data, indent=4 ) )

if __name__=="__main__":
    tweets = load_data(params['data_files'])

    write_csv(get_bffs(tweets), params['bff_output'])
    write_csv(get_geo(tweets), params['geo_output'])
    write_csv(get_csv_output(tweets), params['csv_output'])
    write_text(tweets, params['text_output'])
    write_json(tweets, params['json_output'])


    # tweets = getData()
    # males, females = {}, {}
    # with open('./tweet_data/males.txt') as f:
    #     males = set([w.strip() for w in f.readlines()])
    # with open('./tweet_data/females.txt') as f:
    #     females = set([w.strip() for w in f.readlines()])
    #
    # males_c, females_c, not_found = 0, 0, 0
    # for t in tweets:
    #     if t['name'] in males:
    #         males_c += 1
    #     elif t['name'] in females:
    #         females_c += 1
    #     else:
    #         not_found += 1
    # print males_c, females_c, not_found
    pdb.set_trace()