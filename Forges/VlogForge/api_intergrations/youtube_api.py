import os
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Configure logging for debugging and error reporting.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class YouTubeDataFetcher:
    def __init__(self):
        """
        Initialize the YouTubeDataFetcher:
          - Loads environment variables.
          - Retrieves the API key.
          - Builds the YouTube API client.
        """
        load_dotenv()
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            logging.error("YOUTUBE_API_KEY not found in environment variables.")
            raise ValueError("Missing YOUTUBE_API_KEY in environment variables.")
        self.youtube = self._build_client()

    def _build_client(self):
        """
        Builds the YouTube API client.
        Returns:
            An instance of the YouTube API client.
        """
        try:
            youtube_client = build("youtube", "v3", developerKey=self.api_key)
            logging.info("YouTube API client built successfully.")
            return youtube_client
        except Exception as e:
            logging.error(f"Error building YouTube API client: {e}")
            raise

    def get_video_data(self, video_id, retry=True):
        """
        Fetches video data (views, likes, comments) from the YouTube API.

        Args:
            video_id (str): The ID of the YouTube video.
            retry (bool): If True, attempts to rebuild the client and retry once upon failure.
            
        Returns:
            dict: A dictionary containing video metrics or an error message.
        """
        try:
            video_response = self.youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            if video_response.get('items'):
                video = video_response['items'][0]
                stats = video.get('statistics', {})
                views = stats.get('viewCount', 0)
                likes = stats.get('likeCount', 0)
                comments = stats.get('commentCount', 0)
                logging.info(f"Successfully retrieved data for video ID: {video_id}")
                return {
                    "views": views,
                    "likes": likes,
                    "comments": comments
                }
            else:
                logging.warning(f"No video data found for video ID: {video_id}")
                return {"error": "Video not found or no data available."}

        except HttpError as e:
            logging.error(f"HTTP error while fetching video data: {e}")
            return {"error": f"HTTP error occurred: {str(e)}"}

        except Exception as e:
            logging.error(f"Error fetching video data: {e}")
            # Self-healing: attempt to rebuild the client and retry once.
            if retry:
                logging.info("Attempting to rebuild the YouTube API client and retry the request.")
                self.youtube = self._build_client()
                return self.get_video_data(video_id, retry=False)
            return {"error": f"Failed to fetch video data: {str(e)}"}

if __name__ == "__main__":
    # Replace with the video ID you want to query.
    video_id = "dQw4w9WgXcQ"  
    fetcher = YouTubeDataFetcher()
    video_metrics = fetcher.get_video_data(video_id)
    print(video_metrics)
