#Import the necessary methods from tweepy library
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import pandas as pd

config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)

# Since we're going to be using a streaming endpoint, there is no need to worry
# about rate limits.
# Create twitter API object

auth = tweepy.OAuthHandler(config["CONSUMER_KEY"], config["CONSUMER_SECRET"])
auth.set_access_token(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth, wait_on_rate_limit=True)


# function to save required basic tweets info to a dataframe
def populate_tweet_df (tweets):
    # Create an empty dataframe
    df = pd.DataFrame()

    df['id'] = list( map( lambda tweet: tweet.id, tweets ) )
    df['text'] = list( map( lambda tweet: tweet.text, tweets ) )
    df['retweeted'] = list( map( lambda tweet: tweet.retweeted, tweets ) )
    df['place'] = list( map( lambda tweet: tweet.user.location, tweets ) )
    df['screen_name'] = list( map( lambda tweet: tweet.user.screen_name, tweets ) )
    df['verified_user'] = list( map( lambda tweet: tweet.user.verified, tweets ) )
    df['followers_count'] = list( map( lambda tweet: tweet.user.followers_count, tweets ) )
    df['friends_count'] = list( map( lambda tweet: tweet.user.friends_count, tweets ) )

    # Highly popular user's tweet could possibly seen by large audience, so lets check the popularity of user
    df['friendship_coeff'] = list(
        map( lambda tweet: float( tweet.user.followers_count )/float( tweet.user.friends_count ), tweets ) )
    return df


#fetch recent 10 tweets containing words iphone7 camera
fetched_tweets = api.search(q=['iPhone X','iPhoneX','camera'], result_type='recent', lang='en', count=10)
print "Number of tweets: ", len(fetched_tweets)

# Print the tweet text
for tweet in fetched_tweets:
    print 'Tweet ID: ', tweet.id
    print 'Tweet Text: ', tweet.text, '\n'

df = populate_tweet_df( fetched_tweets )
print df.head( 10 )

# For help about api look here http://tweepy.readthedocs.org/en/v2.3.0/api.html
fetched_tweets =  api.user_timeline(id='Iphone7review', count=5)

# Print the tweet text
for tweet in fetched_tweets:
    print 'Tweet ID: ', tweet.id
    print 'Tweet Text: ', tweet.text, '\n'

