import tweepy
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET_KEY = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Ensure credentials are loaded correctly
if not all([API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    raise ValueError("Missing Twitter API credentials in environment variables.")

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Example functions to post tweet and retrieve engagement
def post_tweet(content):
    try:
        tweet = api.update_status(content)
        return tweet
    except Exception as e:
        return f"Error posting tweet: {e}"

def get_tweet_engagement(tweet_id):
    try:
        tweet = api.get_status(tweet_id)
        likes = tweet.favorite_count
        retweets = tweet.retweet_count
        comments = tweet.reply_count if hasattr(tweet, 'reply_count') else 0
        return {"likes": likes, "retweets": retweets, "comments": comments}
    except Exception as e:
        return f"Error retrieving engagement data: {e}"

# Sample post tweet to test
if __name__ == "__main__":
    tweet = post_tweet("Testing Twitter API integration!")
    print(tweet)
