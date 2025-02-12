from textblob import TextBlob
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from unittest.mock import patch, Mock
import unittest
import pandas as pd


class SocialMediaAnalyzer:
    def __init__(self, keywords=None):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.keywords = keywords or []  # Add keyword filter

    def scrape_stocktwits_post(self, title, description):
        url = f'https://stocktwits.com/symbol/{title}'
        return self.scrape_generic(url, title, description, 'st_3rd_party_message_content')

    def scrape_instagram_posts(self, hashtag, description):
        url = f'https://www.instagram.com/explore/tags/{hashtag}/'
        return self.scrape_generic(url, hashtag, description, 'C4VMK')

    def scrape_youtube_comments(self, video_id, description):
        url = f'https://www.youtube.com/watch?v={video_id}'
        return self.scrape_generic(url, video_id, description, 'style-scope ytd-comment-renderer')

    def scrape_generic(self, url, title, description, content_class):
        scraped_data = []

        def process_post(post):
            post_text = post.text.strip()
            if self.keywords and not self.keyword_filter(post_text):
                return None  # Skip posts without keywords
            sentiment = round(TextBlob(post_text).sentiment.polarity, 2)
            print(f'{title} Post: {post_text} | Sentiment: {sentiment}')
            return {'title': title, 'description': description, 'post': post_text, 'sentiment': sentiment}

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            if response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = soup.find_all('p', class_=content_class)[:10]
                with ThreadPoolExecutor(max_workers=5) as executor:
                    results = list(executor.map(process_post, posts))
                    scraped_data = [r for r in results if r]  # Filter out None values

                if scraped_data:  # Only save and generate reports if data exists
                    self.save_data(title, scraped_data)
            else:
                print('No content available to parse.')
        except (requests.exceptions.RequestException, ValueError, TypeError):
            print(f'Failed to scrape {title}.')

    def keyword_filter(self, text):
        return any(keyword.lower() in text.lower() for keyword in self.keywords)

    def save_data(self, title, data):
        with open(f'{title}_report.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'description', 'post', 'sentiment'])
            writer.writeheader()
            writer.writerows(data)

        self.generate_sentiment_graph(title, data)
        self.generate_summary_report(title, data)

    def generate_sentiment_graph(self, title, data):
        sentiments = [item['sentiment'] for item in data]
        posts = [f"Post {i+1}" for i in range(len(sentiments))]

        plt.figure(figsize=(10, 6))
        plt.bar(posts, sentiments, color='skyblue')
        plt.title(f'Sentiment Analysis for {title}')
        plt.xlabel('Posts')
        plt.ylabel('Sentiment Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{title}_sentiment_graph.png')
        plt.close()

    def generate_summary_report(self, title, data):
        if not data:
            return  # Skip report generation if no data exists

        avg_sentiment = round(sum(item['sentiment'] for item in data) / len(data), 2)
        positive_posts = len([item for item in data if item['sentiment'] > 0])
        negative_posts = len([item for item in data if item['sentiment'] < 0])
        neutral_posts = len(data) - positive_posts - negative_posts

        summary = (
            f"Summary Report for {title}:\n"
            f"Average Sentiment: {avg_sentiment}\n"
            f"Positive Posts: {positive_posts}\n"
            f"Negative Posts: {negative_posts}\n"
            f"Neutral Posts: {neutral_posts}\n"
        )

        print(summary)
        with open(f'{title}_summary_report.txt', 'w') as file:
            file.write(summary)

class TestSocialMediaAnalyzer(unittest.TestCase):
    @patch('requests.get')
    def test_scrape_stocktwits_post(self, mock_get):
        analyzer = SocialMediaAnalyzer(keywords=['content'])
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <body>
                <p class="st_3rd_party_message_content">Post 1 content</p>
                <p class="st_3rd_party_message_content">Post 2 content</p>
                <p class="st_3rd_party_message_content">Post 3 content</p>
                <p class="st_3rd_party_message_content">Irrelevant post</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        with patch('builtins.print') as mock_print:
            analyzer.scrape_stocktwits_post('AAPL', 'Description')

            mock_print.assert_any_call('AAPL Post: Post 1 content | Sentiment: 0.0')
            mock_print.assert_any_call('AAPL Post: Post 2 content | Sentiment: 0.0')
            mock_print.assert_any_call('AAPL Post: Post 3 content | Sentiment: 0.0')
            self.assertGreaterEqual(mock_print.call_count, 3)

    @patch('requests.get')
    def test_no_keyword_match(self, mock_get):
        analyzer = SocialMediaAnalyzer(keywords=['unmatched'])
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <body>
                <p class="st_3rd_party_message_content">Post without matching keyword</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        with patch('builtins.print') as mock_print:
            analyzer.scrape_stocktwits_post('AAPL', 'Description')
            mock_print.assert_not_called()  # No print calls expected

    @patch('requests.get')
    def test_multiple_keywords_match(self, mock_get):
        analyzer = SocialMediaAnalyzer(keywords=['content', 'Post'])
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <body>
                <p class="st_3rd_party_message_content">Post 1 with content</p>
                <p class="st_3rd_party_message_content">Another Post about content</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        with patch('builtins.print') as mock_print:
            analyzer.scrape_stocktwits_post('AAPL', 'Description')

            mock_print.assert_any_call('AAPL Post: Post 1 with content | Sentiment: 0.0')
            mock_print.assert_any_call('AAPL Post: Another Post about content | Sentiment: 0.0')
            self.assertEqual(mock_print.call_count, 3)

    @patch('requests.get')
    def test_empty_response_handling(self, mock_get):
        analyzer = SocialMediaAnalyzer()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = ''  # Empty response
        mock_get.return_value = mock_response

        with patch('builtins.print') as mock_print:
            analyzer.scrape_stocktwits_post('AAPL', 'Description')
            mock_print.assert_called_once_with('No content available to parse.')

    @patch('requests.get')
    def test_scrape_stocktwits_post_failure(self, mock_get):
        analyzer = SocialMediaAnalyzer()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with patch('builtins.print') as mock_print:
            analyzer.scrape_stocktwits_post('AAPL', 'Description')

            mock_print.assert_called_once_with('Failed to scrape AAPL.')

if __name__ == '__main__':
    unittest.main()
