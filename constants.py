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

TWEET_QUERY = "matcherino.com/tournaments -filter:retweets"

USE_LOCAL_DB = False
LOCAL_DB = "http://localhost:8000"
REMOTE_DB = "us-east-2"
DATA_TABLE = "MatcherinoBot"
KEY_FIELD = "row_id"
KEY_VALUE = "DATA_ROW"
LAST_ID_FIELD = "last_id"
