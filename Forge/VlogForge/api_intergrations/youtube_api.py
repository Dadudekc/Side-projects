from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize YouTube API client using the API key
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_video_data(video_id):
    """
    Fetch video data such as views, likes, comments from YouTube API.

    :param video_id: The ID of the YouTube video.
    :return: Video metrics (views, likes, comments).
    """
    try:
        # Fetch video statistics from YouTube API
        video_response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()

        # Extract the data
        if 'items' in video_response and len(video_response['items']) > 0:
            video = video_response['items'][0]
            views = video['statistics'].get('viewCount', 0)
            likes = video['statistics'].get('likeCount', 0)
            comments = video['statistics'].get('commentCount', 0)

            return {
                "views": views,
                "likes": likes,
                "comments": comments
            }
        else:
            return {"error": "Video not found or no data available."}

    except Exception as e:
        return {"error": f"Failed to fetch video data: {str(e)}"}

# Example usage
if __name__ == "__main__":
    video_id = "dQw4w9WgXcQ"  # Example video ID (replace with an actual video ID)
    video_metrics = get_video_data(video_id)
    print(video_metrics)
