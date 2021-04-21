import tweepy

from constants import *

def get_last_id():
    #here a query to AWS's DynamoDB will be made to get the last retweeted id
    return 0

def set_last_id(the_id):
    #same, but updating the last id
    pass

def get_api():
    

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def run():
    api = get_api()
    last_id = get_last_id()

    query_count = 5

    #if there's no last id, get one to use as base
    if last_id == 0:
        query_count = 1

    tweets = tweepy.Cursor(api.search,
              q=TWEET_QUERY,
              result_type="recent",
              since_id=last_id,
              include_entities=False).items(query_count)

    last_id_set = False

    try:
        for tweet in tweets:
            api.retweet(id=tweet.id)

            if not last_id_set:
                last_id = tweet.id
                last_id_set = True
    except:
         print("Something went wrong, sorry.")

    set_last_id(last_id)

run()

