# -*- coding: utf-8 -*-
# Use Python 2.7+
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

import argparse
import os
import sys
import simplejson
import time
import tweepy

#######
# PARAMETERS START
#######

pFOLLOWING_DIR = "following"
pMAX_FRIENDS = 200
pFRIENDS_OF_FRIENDS_LIMIT = 200
pTWITTERUSERNAME = "TED"

#######
# PARAMETERS END
#######

if not os.path.exists( pFOLLOWING_DIR ):
    os.makedirs( pFOLLOWING_DIR )

enc = lambda x: x.encode( 'ascii', errors='ignore' )

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
CONSUMER_KEY = '2zqaRrlnTi7AQrk6gD1lqsoqo'
CONSUMER_SECRET = 'EvGH0LPCjC7lyjt4uszT4s2lQmnd2om7rArDftYibtJ6yoRl8z'

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
ACCESS_TOKEN = '4415191522-OuA6gF4Zub4c0bTn4UwunHO2GSH8w1aYEdY9ZHf'
ACCESS_TOKEN_SECRET = 'N1jVLY2szClSxJ0zIpkREThkuSWYiiY3ItNKxTN8MJydx'

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
auth = tweepy.OAuthHandler( CONSUMER_KEY, CONSUMER_SECRET )
auth.set_access_token( ACCESS_TOKEN, ACCESS_TOKEN_SECRET )

api = tweepy.API( auth )


def getFollowerIDS(centre, maxDepth=1, currentDepth=0, repList=None):
    #print('current depth: %d, max depth: %d' % (currentDepth, maxDepth))
    #print('taboo list: ', ','.join([ str(i) for i in repList ]))

    if repList is None:
        repList = []
    global fname
    fname = ""
    if currentDepth == maxDepth:
        print 'out of depth'
        return repList

    if centre in repList:
        # we've been here before
        print 'Already been here.'
        return repList
    else:
        repList.append( centre )

    try:
        userfname = "test.json"
        if not os.path.exists( userfname ):
            print 'Retrieving user details for twitter id %s'%str( centre )
            while True:
                try:
                    user = api.get_user( centre )

                    d = {'name': user.name,
                         'screen_name': user.screen_name,
                         'id': user.id,
                         'friends_count': user.friends_count,
                         'followers_count': user.followers_count,
                         'followers_ids': user.followers_ids()}

                    with open( userfname, 'a' ) as outf:
                        outf.write( simplejson.dumps( d, indent=1 ) )

                    user = d
                    break
                except tweepy.TweepError, error:
                    print type( error )

                    if str( error ) == 'Not authorized.':
                        print 'Can''t access user data - not authorized.'
                        return repList

                    if str( error ) == 'User has been suspended.':
                        print 'User suspended.'
                        return repList

                    errorObj = error[0][0]

                    print errorObj

                    if errorObj['message'] == 'Rate limit exceeded':
                        print 'Rate limited. Sleeping for 15 minutes.'
                        time.sleep( 15*60 + 15 )
                        continue

                    return repList
        else:
            user = simplejson.loads( file( userfname ).read() )

        screen_name = enc( user['screen_name'] )
        fname = os.path.join( pFOLLOWING_DIR, screen_name + '.csv' )
        friendIDS = []

        # only retrieve friends of screen names
        if screen_name.startswith( pTWITTERUSERNAME ):
            if not os.path.exists( fname ):
                print 'No cached data for screen name "%s"'%screen_name
                with open( fname, 'w' ) as outf:
                    params = (enc( user['name'] ), screen_name)
                    print 'Retrieving friends for user "%s" (%s)'%params

                    # page over friends
                    c = tweepy.Cursor( api.friends, id=user['id'] ).items()

                    friend_count = 0
                    while True:
                        try:
                            friend = c.next()
                            friendIDS.append( friend.id )
                            params = (friend.id, enc( friend.screen_name ), enc( friend.name ))
                            outf.write( '%s\t%s\t%s\n'%params )
                            friend_count += 1
                            if friend_count >= pMAX_FRIENDS:
                                print 'Reached max no. of friends for "%s".'%friend.screen_name
                                break
                        except tweepy.TweepError:
                            # hit rate limit, sleep for 15 minutes
                            print 'Rate limited. Sleeping for 15 minutes.'
                            time.sleep( 15*60 + 15 )
                            continue
                        except StopIteration:
                            break
            else:
                friendids = [int( line.strip().split( '\t' )[0] ) for line in file( fname )]

            print 'Found %d friends for %s'%(len( friendIDS ), screen_name)

            # get friends of friends
            cd = currentDepth
            if cd + 1 < maxDepth:
                for fid in friendIDS[:pFRIENDS_OF_FRIENDS_LIMIT]:
                    taboo_list = getFollowerIDS( fid,
                                                 maxDepth=maxDepth,
                                                 currentDepth=cd + 1,
                                                 repList=repList )

            if cd + 1 < maxDepth and len( friendIDS ) > pFRIENDS_OF_FRIENDS_LIMIT:
                print 'Not all friends retrieved for %s.'%screen_name

    except Exception, error:
        print 'Error retrieving followers for user id: ', centre
        print error

        if os.path.exists( fname ):
            os.remove( fname )
            print 'Removed file "%s".'%fname

        sys.exit( 1 )

    return repList


def main():


    ap = argparse.ArgumentParser()
    ap.add_argument( "-s", "--screen-name", required=True, help="Screen name of twitter user" )
    ap.add_argument( "-d", "--depth", required=True, type=int, help="How far to follow user network" )
    args = vars( ap.parse_args() )

    twitter_screenname = args['screen_name']
    depth = int( args['depth'] )

    if depth < 1 or depth > 3:
        print 'Depth value %d is not valid. Valid range is 1-3.'%depth
        sys.exit( 'Invalid depth argument.' )

    print 'Max Depth: %d'%depth
    matches = api.lookup_users( screen_names=[twitter_screenname] )

    if len( matches ) == 1:
        print getFollowerIDS( matches[0].id, maxDepth=depth )
    else:
        print 'Sorry, could not find twitter user with screen name: %s'%twitter_screenname


if __name__ == '__main__':
    main()