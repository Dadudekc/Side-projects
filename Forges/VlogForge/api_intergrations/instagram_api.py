#!/usr/bin/env python3
"""
Instagram API Integration Module

This module provides functionality to interact with the Instagram Graph API,
including authentication, posting, and retrieving analytics.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import requests
from requests_oauthlib import OAuth2Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramAPI:
    """Instagram API integration class."""
    
    def __init__(self):
        """Initialize Instagram API client."""
        self.api_key = os.getenv('INSTAGRAM_API_KEY')
        self.api_secret = os.getenv('INSTAGRAM_API_SECRET')
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.base_url = "https://graph.instagram.com/v12.0"
        
        if not all([self.api_key, self.api_secret, self.access_token]):
            raise ValueError("Instagram API credentials not found in environment variables")
        
        self.session = OAuth2Session(
            client_id=self.api_key,
            token={
                'access_token': self.access_token,
                'token_type': 'Bearer'
            }
        )

    def get_account_info(self) -> Dict:
        """
        Get basic account information.
        
        Returns:
            Dict: Account information including username, profile picture, etc.
        """
        try:
            response = self.session.get(f"{self.base_url}/me")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching account info: {str(e)}")
            raise

    def get_media_list(self, limit: int = 10) -> List[Dict]:
        """
        Get list of recent media posts.
        
        Args:
            limit (int): Number of posts to retrieve (default: 10)
            
        Returns:
            List[Dict]: List of media posts with details
        """
        try:
            response = self.session.get(
                f"{self.base_url}/me/media",
                params={'limit': limit}
            )
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching media list: {str(e)}")
            raise

    def get_media_insights(self, media_id: str) -> Dict:
        """
        Get insights for a specific media post.
        
        Args:
            media_id (str): ID of the media post
            
        Returns:
            Dict: Media insights including engagement metrics
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{media_id}/insights",
                params={'metric': 'engagement,impressions,reach'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching media insights: {str(e)}")
            raise

    def post_media(self, image_url: str, caption: str) -> Dict:
        """
        Post a new media item to Instagram.
        
        Args:
            image_url (str): URL of the image to post
            caption (str): Caption for the post
            
        Returns:
            Dict: Response containing post details
        """
        try:
            # First, create a container
            container_response = self.session.post(
                f"{self.base_url}/me/media",
                params={
                    'image_url': image_url,
                    'caption': caption,
                    'access_token': self.access_token
                }
            )
            container_response.raise_for_status()
            container_id = container_response.json().get('id')
            
            # Then, publish the container
            publish_response = self.session.post(
                f"{self.base_url}/me/media_publish",
                params={
                    'creation_id': container_id,
                    'access_token': self.access_token
                }
            )
            publish_response.raise_for_status()
            return publish_response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting media: {str(e)}")
            raise

    def get_hashtag_insights(self, hashtag: str) -> Dict:
        """
        Get insights for a specific hashtag.
        
        Args:
            hashtag (str): Hashtag to analyze
            
        Returns:
            Dict: Hashtag insights including usage statistics
        """
        try:
            # First, get the hashtag ID
            hashtag_response = self.session.get(
                f"{self.base_url}/ig_hashtag_search",
                params={
                    'user_id': self.get_account_info()['id'],
                    'q': hashtag
                }
            )
            hashtag_response.raise_for_status()
            hashtag_id = hashtag_response.json().get('data', [{}])[0].get('id')
            
            # Then, get the hashtag insights
            insights_response = self.session.get(
                f"{self.base_url}/{hashtag_id}/top_media",
                params={'user_id': self.get_account_info()['id']}
            )
            insights_response.raise_for_status()
            return insights_response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching hashtag insights: {str(e)}")
            raise

    def get_audience_insights(self) -> Dict:
        """
        Get audience insights for the account.
        
        Returns:
            Dict: Audience insights including demographics and engagement
        """
        try:
            response = self.session.get(
                f"{self.base_url}/me/insights",
                params={'metric': 'audience_city,audience_country,audience_gender_age'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching audience insights: {str(e)}")
            raise

def main():
    """Example usage of the Instagram API client."""
    try:
        # Initialize the API client
        instagram = InstagramAPI()
        
        # Get account info
        account_info = instagram.get_account_info()
        logger.info(f"Account info: {json.dumps(account_info, indent=2)}")
        
        # Get recent media
        media_list = instagram.get_media_list(limit=5)
        logger.info(f"Recent media: {json.dumps(media_list, indent=2)}")
        
        # Get audience insights
        audience_insights = instagram.get_audience_insights()
        logger.info(f"Audience insights: {json.dumps(audience_insights, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 