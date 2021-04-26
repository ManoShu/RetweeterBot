import tweepy
import boto3
from os import environ

DEBUG = False

# App
CONSUMER_KEY = environ["CONSUMER_KEY"]
CONSUMER_SECRET = environ["CONSUMER_SECRET"]

# Bot
ACCESS_KEY = environ["ACCESS_KEY"]
ACCESS_SECRET = environ["ACCESS_SECRET"]

# DynamoDB
AWS_SERVER_PUBLIC_KEY = environ["AWS_SERVER_PUBLIC_KEY"]
AWS_SERVER_SECRET_KEY = environ["AWS_SERVER_SECRET_KEY"]

TWEET_QUERY = environ["TWEET_QUERY"] 

USE_LOCAL_DB = False
LOCAL_DB = "http://localhost:8000"
REMOTE_DB = environ["REMOTE_DB"]
DATA_TABLE = "RetweetBots"
KEY_FIELD = "row_id"
KEY_VALUE = environ["KEY_VALUE"]
LAST_ID_FIELD = "last_id"

def create_table(dynamodb=None):
    if not dynamodb:
        dynamodb = get_dynamo()

    table = dynamodb.create_table(
        TableName=DATA_TABLE,
        KeySchema=[
            {
                'AttributeName': KEY_FIELD,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': KEY_FIELD,
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    if DEBUG:
        print("create_table", table)

    return table

def get_last_id(dynamo=None) -> str:
    #here a query to AWS's DynamoDB will be made to get the last retweeted id

    if not dynamo:
        dynamo = get_dynamo()

    existing_tables = [x.name for x in dynamo.tables.all()]
    if DATA_TABLE not in existing_tables:
        create_table(dynamo)

    table = get_table(dynamo)
    response = table.scan()
    items = response.get('Items', [])

    the_id: str = None

    for item in items:
        the_id =item[LAST_ID_FIELD]
        break
    if DEBUG:
        print("select", the_id)
    return the_id

def set_last_id(previous_id: str, the_id: str, dynamo=None):
    #same, but updating the last id
    if not dynamo:
        dynamo = get_dynamo()

    table = get_table(dynamo)

    has_data = previous_id is not None

    if  has_data:
        response = table.update_item(
            Key={
                KEY_FIELD: KEY_VALUE
            },
            UpdateExpression="set last_id=:l",
            ExpressionAttributeValues={
                ':l': the_id
            },
            ReturnValues="UPDATED_NEW"
            )
        if DEBUG:
            print("update", response)
    else:
        table.put_item(Item={ KEY_FIELD: KEY_VALUE, LAST_ID_FIELD: the_id})
        if DEBUG:
            print("insert", the_id)

def get_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def get_dynamo():
    session = boto3.Session(
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
    )
    dynamodb = session.resource('dynamodb', endpoint_url=LOCAL_DB) if USE_LOCAL_DB else boto3.resource('dynamodb', region_name=REMOTE_DB)
    return dynamodb

def get_table(dynamo=None):
    if dynamo is None:
        dynamo = get_dynamo()
    return dynamo.Table(DATA_TABLE)

def run():
    api = get_api()

    dynamo = get_dynamo()

    last_id = get_last_id(dynamo)
    previous_id = last_id

    query_count = int(environ["QUERY_COUNT"]) if "QUERY_COUNT" in environ else 5

    #if there's no last id, get one to use as base
    if last_id is None:
        query_count = 1

    tweets = tweepy.Cursor(api.search,
              q=TWEET_QUERY,
              result_type="recent",
              since_id=last_id,
              include_entities=False).items()

    tweet_id_list = []

    for tweet in tweets:
        if tweet.in_reply_to_status_id is not None:
            if DEBUG: print("Reply. Ignoring...")
        elif tweet.retweeted != False:
            if DEBUG: print("Already retweeted")
        elif hasattr(tweet, 'retweeted_status'):
            if DEBUG: print("Is a retweet itself, ignoring...")
        else:
            tweet_id_list.append(tweet.id_str)
            
    tweet_id_list.reverse()

    # print(tweet_id_list)

    rt_count = 0
    for tweet_id in tweet_id_list:
        try:
            if DEBUG:
                print(tweet_id)
                # not setting id to keep at same position for non-debug run
                # last_id = tweet_id
            else:                
                last_id = tweet_id
                api.retweet(id=tweet_id)
                

            rt_count += 1
            if rt_count == query_count:
                break
        except tweepy.error.TweepError as e:
            # already retweeted
            if e.api_code == 327:
                if DEBUG: print("already retweeted")
            else:
                raise

    if last_id != previous_id:
        set_last_id(previous_id, last_id, dynamo)

if __name__ == "__main__":
    run()
