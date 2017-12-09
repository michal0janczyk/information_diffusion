#!/usr/bin/python
# -*- coding: utf-8 -*-
# Use Python 2.7+
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

from twitter import *

config = {}
execfile("/home/mike/Documents/repoo/information_diffusion/twitter_api/config/config.py", config)

# Create twitter API object
twitter = Twitter(auth=OAuth(config["ACCESS_TOKEN"], config["ACCESS_TOKEN_SECRET"],
                             config["CONSUMER_KEY"], config["CONSUMER_SECRET"]))

# Retrieve global trends.
# Other localised trends can be specified by looking up WOE IDs:
# From web page: http://developer.yahoo.com/geo/geoplanet/
# twitter API docs: https://dev.twitter.com/rest/reference/get/trends/place

WORLD_WOE_ID = 1
US_WOE_ID = 23424977
UK_WOE_ID = 23424975

def get_hashtags(text, order=False):
    tags = set([item.strip("#.,-\"\'&*^!") for item in text.split() if (item.startswith("#") and len(item) < 256)])
    return sorted(tags) if order else tags

def main():

    res = []
    resTrends = twitter.trends.place(_id=US_WOE_ID)
    for location in resTrends:
        for trend in location["trends"]:
            res.append("%s" % trend["name"])
            print res
            #with open('tweets_trends.data', 'a') as f:
            #    f.write(res)

    print(get_hashtags(res))


if __name__ == '__main__':
    main()