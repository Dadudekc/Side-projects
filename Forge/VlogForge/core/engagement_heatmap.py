import unittest
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

class EngagementHeatmap:
    def __init__(self):
        self.engagement_data = pd.DataFrame()

    def add_engagement_data(self, data):
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data should be a pandas DataFrame")
        
        required_columns = {"timestamp", "engagement", "type"}
        if not required_columns.issubset(data.columns):
            raise ValueError("Data must contain 'timestamp', 'engagement', and 'type' columns")

        data['timestamp'] = pd.to_datetime(data['timestamp'])
        self.engagement_data = pd.concat([self.engagement_data, data], ignore_index=True)

    def filter_data(self, start_date=None, end_date=None, engagement_type=None):
        filtered_data = self.engagement_data

        if start_date:
            filtered_data = filtered_data[filtered_data['timestamp'] >= pd.to_datetime(start_date)]
        if end_date:
            filtered_data = filtered_data[filtered_data['timestamp'] <= pd.to_datetime(end_date)]
        if engagement_type:
            filtered_data = filtered_data[filtered_data['type'] == engagement_type]

        return filtered_data

    def generate_heatmap(self, start_date=None, end_date=None, engagement_type=None):
        filtered_data = self.filter_data(start_date, end_date, engagement_type)

        if filtered_data.empty:
            raise ValueError("No engagement data to display")

        filtered_data['day'] = filtered_data['timestamp'].dt.day_name()
        filtered_data['hour'] = filtered_data['timestamp'].dt.hour

        pivot_table = filtered_data.pivot_table(
            index='day', 
            columns='hour', 
            values='engagement', 
            aggfunc='mean'
        )

        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="coolwarm")
        plt.title("Engagement Heatmap")
        plt.xlabel("Hour of Day")
        plt.ylabel("Day of Week")
        plt.show()

class TestEngagementHeatmap(unittest.TestCase):
    def setUp(self):
        self.heatmap = EngagementHeatmap()

    def test_add_engagement_data_success(self):
        data = pd.DataFrame({
            'timestamp': [datetime(2024, 4, 1, 12), datetime(2024, 4, 2, 14)],
            'engagement': [100, 150],
            'type': ['like', 'comment']
        })
        self.heatmap.add_engagement_data(data)
        self.assertEqual(len(self.heatmap.engagement_data), 2)

    def test_add_engagement_data_invalid_format(self):
        with self.assertRaises(ValueError):
            self.heatmap.add_engagement_data("Invalid Data")

    def test_add_engagement_data_missing_columns(self):
        data = pd.DataFrame({
            'time': [datetime(2024, 4, 1, 12)],
            'likes': [100]
        })
        with self.assertRaises(ValueError):
            self.heatmap.add_engagement_data(data)

    def test_generate_heatmap_no_data(self):
        with self.assertRaises(ValueError):
            self.heatmap.generate_heatmap()

    def test_generate_heatmap_success(self):
        data = pd.DataFrame({
            'timestamp': [datetime(2024, 4, 1, 12), datetime(2024, 4, 2, 14)],
            'engagement': [100, 150],
            'type': ['like', 'comment']
        })
        self.heatmap.add_engagement_data(data)
        # This should not raise an error
        self.heatmap.generate_heatmap()

    def test_filter_by_date_range(self):
        data = pd.DataFrame({
            'timestamp': [datetime(2024, 4, 1, 12), datetime(2024, 4, 3, 14)],
            'engagement': [100, 150],
            'type': ['like', 'comment']
        })
        self.heatmap.add_engagement_data(data)
        filtered_data = self.heatmap.filter_data(start_date='2024-04-02')
        self.assertEqual(len(filtered_data), 1)

    def test_filter_by_engagement_type(self):
        data = pd.DataFrame({
            'timestamp': [datetime(2024, 4, 1, 12), datetime(2024, 4, 2, 14)],
            'engagement': [100, 150],
            'type': ['like', 'comment']
        })
        self.heatmap.add_engagement_data(data)
        filtered_data = self.heatmap.filter_data(engagement_type='comment')
        self.assertEqual(len(filtered_data), 1)

if __name__ == '__main__':
    unittest.main()
