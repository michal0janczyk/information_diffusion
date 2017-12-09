from twitter import *
import json
import simplejson
from collections import Counter

from numpy.ma import log
from prettytable import PrettyTable
import matplotlib.pyplot as plt
# Import unquote to prevent url encoding errors in next_results
from urllib import unquote

config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)

# Create twitter API object
twitterAPI = Twitter(auth=OAuth(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"],
                                config["CONSUMER_KEY"], config["CONSUMER_SECRET"]))

# Nothing to see by displaying twitter_api except that it's now a
# defined variable

print twitterAPI

# The Yahoo! Where On Earth ID for the entire world is 1.
# See https://dev.twitter.com/docs/api/1.1/get/trends/place and
# http://developer.yahoo.com/geo/geoplanet/

WORLD_WOE_ID = 1
US_WOE_ID = 23424977

# Prefix ID with the underscore for query string parametrization.
# Without the underscore, the twitter package appends the ID value
# to the URL itself as a special case keyword argument.

world_trends = twitterAPI.trends.place(_id=WORLD_WOE_ID)
us_trends = twitterAPI.trends.place(_id=US_WOE_ID)

print world_trends
print
print us_trends

print json.dumps(world_trends, indent=1)
print
print json.dumps(us_trends, indent=1)

world_trends_set = set([trend['name'] for trend in world_trends[0]['trends']])

us_trends_set = set([trend['name'] for trend in us_trends[0]['trends']])

common_trends = world_trends_set.intersection(us_trends_set)

print common_trends

# XXX: Set this variable to a trending topic,
# or anything else for that matter. The example query below
# was a trending topic when this content was being developed
# and is used throughout the remainder of this chapter.

q = '#HashTag'

count = 100

# See https://dev.twitter.com/docs/api/1.1/get/search/tweets

search_results = twitterAPI.search.tweets(q=q, count=count)

statuses = search_results['statuses']

# Iterate through 5 more batches of results by following the cursor

for _ in range(5):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e:  # No more results when next_results doesn't exist
        break

    # Create a dictionary from next_results, which has the following form:
    # ?max_id=313519052523986943&q=NCAA&include_entities=1
    kwargs = dict([kv.split('=') for kv in unquote(next_results[1:]).split("&")])

    search_results = twitterAPI.search.tweets(**kwargs)
    statuses += search_results['statuses']

# Show one sample search result by slicing the list...
print json.dumps(statuses[0], indent=1)

statuses = simplejson.loads(open('HashTag.json').read())

# The result of the list comprehension is a list with only one element that
# can be accessed by its index and set to the variable t
t = [status for status in statuses if status['id'] == 316948241264549888][0]

# Explore the variable t to get familiarized with the data structure...

print t['retweet_count']
print t['retweeted_status']

# Can you find the most retweeted tweet in your search results? Try do do it!
status_texts = [status['text'] for status in statuses]

screen_names = []
for status in statuses:
    for user_mention in status['entities']['user_mentions']:
        screen_names.append(user_mention['screen_name'])

hashtags = []
for status in statuses:
    for hashtag in status['entities']['hashtags']:
        hashtags.append(hashtag['text'])

# Compute a collection of all words from all tweets
words = [w for t in status_texts for w in t.split()]

# Explore the first 5 items for each...

print json.dumps(status_texts[0:5], indent=1)
print json.dumps(screen_names[0:5], indent=1)
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(words[0:5], indent=1)

for item in [words, screen_names, hashtags]:
    c = Counter(item)
    print c.most_common()[:10]  # top 10
    print

for label, data in (('Word', words),
                    ('Screen Name', screen_names),
                    ('Hashtag', hashtags)):
    pt = PrettyTable(field_names=[label, 'Count'])
    c = Counter(data)
    [pt.add_row(kv) for kv in c.most_common()[:10]]
    pt.align[label], pt.align['Count'] = 'l', 'r'  # Set column alignment
    print pt


# A function for computing lexical diversity
def lexical_diversity(tokens):
    return 1.0 * len(set(tokens)) / len(tokens)


# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([len(s.split()) for s in statuses])
    return 1.0 * total_words / len(statuses)


print lexical_diversity(words)
print lexical_diversity(screen_names)
print lexical_diversity(hashtags)
print average_words(status_texts)

retweets = []
for status in statuses:
    if status.has_key('retweeted_status'):
        retweets.append((status['retweet_count'],
                         status['retweeted_status']['user']['screen_name'], status['text']))

# Slice off the first 5 from the sorted results and display each item in the tuple

pt = PrettyTable(field_names=['Count', 'Screen Name', 'Text'])
[pt.add_row(row) for row in sorted(retweets, reverse=True)[:5]]
pt.max_width['Text'] = 50
pt.align = 'l'
print pt

# Get the original tweet id for a tweet from its retweeted_status node
# and insert it here in place of the sample value that is provided
# from the text of the book

_retweets = twitterAPI.statuses.retweets(id=317127304981667841)
print [r['user']['screen_name'] for r in _retweets]

word_counts = sorted(Counter(words).values(), reverse=True)

plt.loglog(word_counts)
plt.ylabel("Freq")
plt.xlabel("Word Rank")

for label, data in (('Words', words),
                    ('Screen Names', screen_names),
                    ('Hashtags', hashtags)):

    # Build a frequency map for each set of data
    # and plot the values
    c = Counter(data)
    plt.hist(c.values())

    # Add a title and y-label ...
    plt.title(label)
    plt.ylabel("Number of items in bin")
    plt.xlabel("Bins (number of times an item appeared)")

    # ... and display as a new figure
    plt.figure()

# Using underscores while unpacking values in
# a tuple is idiomatic for discarding them

counts = [count for count, _, _ in retweets]

plt.hist(counts)
plt.title("Retweets")
plt.xlabel('Bins (number of times retweeted)')
plt.ylabel('Number of tweets in bin')

print counts

# Using underscores while unpacking values in
# a tuple is idiomatic for discarding them

counts = [count for count, _, _ in retweets]

# Taking the log of the *data values* themselves can
# often provide quick and valuable insight into the
# underlying distribution as well. Try it back on
# Example 13 and see if it helps.

plt.hist(log(counts))
plt.title("Retweets")
plt.xlabel('Log[Bins (number of times retweeted)]')
plt.ylabel('Log[Number of tweets in bin]')

print log(counts)
