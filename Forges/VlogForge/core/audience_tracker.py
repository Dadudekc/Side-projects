import requests
import datetime
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth1

# Load environment variables
load_dotenv()

class AudienceInteractionTracker:
    def __init__(self):
        self.api_keys = {
            "twitter_api_key": os.getenv("TWITTER_API_KEY"),
            "twitter_api_secret": os.getenv("TWITTER_API_SECRET"),
            "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
            "twitter_access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "twitter_access_secret": os.getenv("TWITTER_ACCESS_SECRET")
        }
        self.data = []

    def fetch_data(self, platform: str, endpoint: str, params: Dict) -> Dict:
        if platform == "twitter":
            headers = {
                "Authorization": f"Bearer {self.api_keys.get('twitter_bearer_token', '')}"
            }
            attempt = 0
            delay = 60  # Default delay if Retry-After header isn't provided

            while attempt < 5:
                response = requests.get(endpoint, headers=headers, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    wait_time = int(retry_after) if retry_after else delay * (2 ** attempt)  # Exponential backoff

                    print(f"Rate limit exceeded (Attempt {attempt + 1}). Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                    attempt += 1
                elif response.status_code == 401:
                    print(f"Authentication failed for {platform}. Check your API credentials.")
                    break
                else:
                    print(f"Error fetching data from {platform}: {response.status_code} - {response.text}")
                    break
        return {}

    def process_data(self, raw_data: Dict) -> Dict:
        metrics = raw_data.get("public_metrics", {})
        processed_data = {
            "likes": metrics.get("like_count", 0),
            "comments": metrics.get("reply_count", 0),
            "shares": metrics.get("retweet_count", 0),
            "views": metrics.get("impression_count", 1),  # Default to 1 to avoid division by zero
            "ctr": self.calculate_ctr(metrics),
            "engagement_rate": self.calculate_engagement_rate(metrics)
        }
        self.data.append({"timestamp": datetime.datetime.now(), **processed_data})
        return processed_data

    def calculate_engagement_rate(self, metrics: Dict) -> float:
        total_interactions = metrics.get("like_count", 0) + metrics.get("reply_count", 0) + metrics.get("retweet_count", 0)
        impressions = metrics.get("impression_count", 1)
        return (total_interactions / impressions) * 100 if impressions else 0.0

    def calculate_ctr(self, metrics: Dict) -> float:
        link_clicks = metrics.get("link_clicks", 0)
        impressions = metrics.get("impression_count", 1)
        return (link_clicks / impressions) * 100 if impressions else 0.0

    def generate_report(self, period: str = "daily") -> Dict:
        today = datetime.date.today()
        if period == "weekly":
            start_date = today - datetime.timedelta(days=7)
        elif period == "monthly":
            start_date = today - datetime.timedelta(days=30)
        else:
            start_date = today

        filtered_data = [entry for entry in self.data if entry["timestamp"].date() >= start_date]
        if not filtered_data:
            return {"message": f"No data available for the {period} report."}

        report = {
            "likes": sum(entry["likes"] for entry in filtered_data),
            "comments": sum(entry["comments"] for entry in filtered_data),
            "shares": sum(entry["shares"] for entry in filtered_data),
            "views": sum(entry["views"] for entry in filtered_data),
            "ctr": sum(entry["ctr"] for entry in filtered_data) / len(filtered_data),
            "engagement_rate": sum(entry["engagement_rate"] for entry in filtered_data) / len(filtered_data),
        }
        return report

    def display_console_report(self, period: str = "daily"):
        report = self.generate_report(period)
        print(f"===== {period.capitalize()} Report =====")
        if "message" in report:
            print(report["message"])
        else:
            for key, value in report.items():
                print(f"{key.capitalize()}: {value}")

    def update(self):
        print("Updating audience interaction data...")
        today_data = self.generate_report("daily")
        print("Daily update completed.")
        return today_data

# Example usage
if __name__ == "__main__":
    tracker = AudienceInteractionTracker()

    twitter_data = tracker.fetch_data(
        "twitter",
        "https://api.twitter.com/2/tweets/search/recent",
        {
            "query": "audience engagement",
            "tweet.fields": "public_metrics",
            "max_results": 10
        }
    )
    if "data" in twitter_data:
        for tweet in twitter_data["data"]:
            tracker.process_data(tweet)

    tracker.display_console_report("daily")
    tracker.update()
