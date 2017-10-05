import nltk
import random
import re

TRENDS = ["MeanGirlsDay",
         "TuesdayThoughts",
         "charitytuesday",
         "Gareth Bale",
         "r4today",
         "TravelTuesday",
         "Jeremy Hunt",
         "Jimmy Kimmel",
         "Ian Wright",
         "Britvic",
         "Zlatan Ibrahimovic",
         "Amber Rudd",
         "Bon Iver",
         "Andrew House",
         "The NHS",
         "Checkatrade Trophy",
         "The Prime Minister",
         "Dan Brown",
         "How Las Vegas",
         "Mark Sampson",
         "ScottishMuseumsDay",
         "popmaster",
         "TomPettyRIP",
         "ScotConf17",
         "cogcdigisymp",
         "CREME21",
         "newcaremodels",
         "NationalBoyfriendDay",
         "smartpractice",
         "futurecontent",
         "RedHatForumUK",
         "VictoriaLIVE",
         "MonsterMashUp",
         "YNCOTY",
         "CRFAmsterdam",
         "partnershipconf",
         "ForzaMotorsport7",
         "FleetLive",
         "NationalPizzaAwards",
         "LHHH",
         "GunContolNow",
         "NobelPrize2017",
         "CXDay",
         "startswithme",
         "BBMFJPO",
         "Origin",
         "SME2017",
         "BringBackHeavyMetal",
         "BBCSchoolReport",
         "NormalBirth17"]

# Regular expression used to clean up the tweet data
mrt_station_re = re.compile('|'.join(TRENDS).lower())
http_re = re.compile(r'\s+http://[^\s]*')
remove_ellipsis_re = re.compile(r'\.\.\.')
at_sign_re = re.compile(r'\@\S+')
punct_re = re.compile(r"[\"'\[\],.:;()\-&!]")
price_re = re.compile(r"\d+\.\d\d")
number_re = re.compile(r"\d+")

# converts to lower case and clean up the text
def normalize_tweet(tweet):
    t = tweet.lower()
    t = re.sub(remove_ellipsis_re, '', t)
    t = re.sub(http_re, ' LINK', t)
    t = re.sub(punct_re, '', t)
    t = re.sub(at_sign_re, '@', t)
    return t

def tweet_features(tweet_data):
    features = {}

    tweet = normalize_tweet(tweet_data['tweet'])
    for bigrams in nltk.bigrams(tweet.split(' ')):
        features['contains(%s)' % ','.join(bigrams)] = True

    return features

# reads three lines of text from a file
read3lines = lambda x: [ x.readline().strip(), x.readline().strip(), x.readline() ]

data = []
with open('labelled_tweets.data') as f:
    tweet, label, newline = read3lines(f)

    while len(tweet) > 0:
        data.append({ 'tweet': tweet, 'label': label })
        tweet, label, newline = read3lines(f)

#random.shuffle(data)

# we split the data into two parts
# the first part (90% of the data) is for training
# the remaining 10% of the data is for testing
size = int(len(data) * 0.9)

train_data = data[:size]
test_data = data[size:]

# generate features for tweet
train_set = [ (tweet_features(d), d['label']) for d in train_data ]
test_set  = [ (tweet_features(d), d['label']) for d in test_data  ]

# pick a classifier
classifier = nltk.NaiveBayesClassifier

# train classifier using training set
classifier = nltk.NaiveBayesClassifier.train(train_set)

classifier.show_most_informative_features(20)

# collect tweets that were wrongly classified
errors = []
for d in test_data:
    label = d['label']
    guess = classifier.classify(tweet_features(d))
    if guess != label:
        errors.append( (label, guess, d) )

for (label, guess, d) in sorted(errors):
    print 'correct label: %s\nguessed label: %s\ntweet=%s\n' % (label, guess, d['tweet'])

print 'Total errors: %d' % len(errors)

print 'Accuracy: ', nltk.classify.accuracy(classifier, test_set)