import unittest
import pandas as pd
from collections import defaultdict

class HashtagPerformanceTracker:
    def __init__(self):
        self.data = {}
        self.hashtag_data = pd.DataFrame()

    def analyze(self, hashtag_data):
        performance = {}
        for hashtag, metrics in hashtag_data.items():
            performance[hashtag] = {
                "engagement_rate": metrics.get("likes", 0) + metrics.get("shares", 0),
                "growth": metrics.get("new_followers", 0)
            }
        return performance

    def add_hashtag_data(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data should be a pandas DataFrame")

        required_columns = {"hashtag", "engagement", "date", "platform"}
        if not required_columns.issubset(data.columns):
            raise ValueError("Data must contain 'hashtag', 'engagement', 'date', and 'platform' columns")

        data['date'] = pd.to_datetime(data['date'])
        self.hashtag_data = pd.concat([self.hashtag_data, data], ignore_index=True)

    def get_top_hashtags(self, top_n=5):
        if self.hashtag_data.empty:
            raise ValueError("No hashtag data available")

        top_hashtags = (
            self.hashtag_data.groupby('hashtag')['engagement']
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )
        return top_hashtags

    def filter_by_date_range(self, start_date, end_date):
        if self.hashtag_data.empty:
            raise ValueError("No hashtag data available")

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        filtered_data = self.hashtag_data[(self.hashtag_data['date'] >= start_date) & (self.hashtag_data['date'] <= end_date)]
        return filtered_data

    def calculate_effectiveness_score(self):
        if self.hashtag_data.empty:
            raise ValueError("No hashtag data available")

        grouped_data = self.hashtag_data.groupby('hashtag').agg({
            'engagement': 'sum',
            'platform': 'nunique',
            'date': 'count'
        }).rename(columns={'platform': 'reach', 'date': 'frequency'})

        grouped_data['effectiveness_score'] = (
            grouped_data['engagement'] * 0.5 + grouped_data['reach'] * 0.3 + grouped_data['frequency'] * 0.2
        )

        return grouped_data.sort_values(by='effectiveness_score', ascending=False)

    def platform_performance(self):
        if self.hashtag_data.empty:
            raise ValueError("No hashtag data available")

        platform_data = (
            self.hashtag_data.groupby(['hashtag', 'platform'])['engagement']
            .sum()
            .unstack(fill_value=0)
        )
        return platform_data

class TestHashtagPerformanceTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = HashtagPerformanceTracker()
        self.sample_data = pd.DataFrame({
            "hashtag": ["#AI", "#Tech", "#AI", "#Growth", "#Tech"],
            "engagement": [100, 200, 150, 80, 300],
            "date": ["2024-04-01", "2024-04-02", "2024-04-03", "2024-04-04", "2024-04-05"],
            "platform": ["Twitter", "Instagram", "Twitter", "Facebook", "Instagram"]
        })

    def test_add_hashtag_data_success(self):
        self.tracker.add_hashtag_data(self.sample_data)
        self.assertEqual(len(self.tracker.hashtag_data), 5)

    def test_add_hashtag_data_invalid_format(self):
        with self.assertRaises(ValueError):
            self.tracker.add_hashtag_data("Invalid Data")

    def test_add_hashtag_data_missing_columns(self):
        data = pd.DataFrame({
            "tag": ["#AI"],
            "likes": [100]
        })
        with self.assertRaises(ValueError):
            self.tracker.add_hashtag_data(data)

    def test_get_top_hashtags(self):
        self.tracker.add_hashtag_data(self.sample_data)
        top_hashtags = self.tracker.get_top_hashtags(top_n=2)
        self.assertIn("#Tech", top_hashtags.index)
        self.assertIn("#AI", top_hashtags.index)

    def test_filter_by_date_range(self):
        self.tracker.add_hashtag_data(self.sample_data)
        filtered_data = self.tracker.filter_by_date_range("2024-04-02", "2024-04-04")
        self.assertEqual(len(filtered_data), 3)
        self.assertIn("#Tech", filtered_data['hashtag'].values)
        self.assertIn("#Growth", filtered_data['hashtag'].values)

    def test_calculate_effectiveness_score(self):
        self.tracker.add_hashtag_data(self.sample_data)
        effectiveness_scores = self.tracker.calculate_effectiveness_score()
        self.assertIn('effectiveness_score', effectiveness_scores.columns)
        self.assertTrue((effectiveness_scores['effectiveness_score'] > 0).all())

    def test_platform_performance(self):
        self.tracker.add_hashtag_data(self.sample_data)
        platform_data = self.tracker.platform_performance()
        self.assertIn("Twitter", platform_data.columns)
        self.assertIn("Instagram", platform_data.columns)
        self.assertIn("Facebook", platform_data.columns)

if __name__ == '__main__':
    unittest.main()
