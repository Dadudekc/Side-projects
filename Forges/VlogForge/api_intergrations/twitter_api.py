import os
import logging
import tweepy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TwitterClientV2:
    def __init__(self):
        """
        Initializes the TwitterClientV2:
          - Loads credentials from the .env file.
          - Builds the Twitter API v2 client.
        """
        load_dotenv()
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret_key = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")

        # Check for required credentials
        if not all([self.bearer_token, self.api_key, self.api_secret_key, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials in environment variables.")

        self.client = self._build_client()

    def _build_client(self):
        """
        Builds and returns the Twitter API v2 client using Tweepy.
        """
        try:
            client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret_key,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            logging.info("Twitter API v2 client built successfully.")
            return client
        except Exception as e:
            logging.error(f"Error building Twitter API client: {e}")
            raise

    def post_tweet(self, content, retry=True):
        """
        Posts a tweet using the Twitter API v2.

        Args:
            content (str): The content of the tweet.
            retry (bool): Whether to retry on failure after rebuilding the client.

        Returns:
            The Tweet ID on success or an error message on failure.
        """
        try:
            response = self.client.create_tweet(text=content)
            if response.data:
                tweet_id = response.data['id']
                logging.info(f"Tweet posted successfully with ID: {tweet_id}")
                return tweet_id
            else:
                return {"error": "Tweet not posted successfully."}
        except tweepy.TweepyException as e:
            logging.error(f"Error posting tweet: {e}")
            if retry:
                logging.info("Rebuilding Twitter API client and retrying post.")
                self.client = self._build_client()
                return self.post_tweet(content, retry=False)
            return f"Error posting tweet: {e}"

    def get_tweet_engagement(self, tweet_id, retry=True):
        """
        Retrieves engagement metrics (likes, retweets, replies) for a tweet.

        Args:
            tweet_id (str or int): The ID of the tweet.
            retry (bool): Whether to retry on failure after rebuilding the client.

        Returns:
            A dictionary containing engagement metrics or an error message.
        """
        try:
            response = self.client.get_tweet(tweet_id, tweet_fields=["public_metrics"])
            if response.data and "public_metrics" in response.data:
                metrics = response.data["public_metrics"]
                logging.info(f"Engagement data retrieved for Tweet ID: {tweet_id}")
                return {
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0)
                }
            return {"error": "No engagement data found."}
        except tweepy.TweepyException as e:
            logging.error(f"Error retrieving tweet engagement: {e}")
            if retry:
                logging.info("Rebuilding Twitter API client and retrying engagement retrieval.")
                self.client = self._build_client()
                return self.get_tweet_engagement(tweet_id, retry=False)
            return f"Error retrieving engagement data: {e}"


# Sample usage
if __name__ == "__main__":
    twitter_client = TwitterClientV2()

    # Post a tweet
    tweet_id = twitter_client.post_tweet("Testing Twitter API v2 integration!")
    print(f"Tweet posted with ID: {tweet_id}")

    # Retrieve engagement metrics
    if tweet_id and not isinstance(tweet_id, dict):  # Check if tweet_id is valid
        engagement = twitter_client.get_tweet_engagement(tweet_id)
        print(f"Engagement metrics: {engagement}")
