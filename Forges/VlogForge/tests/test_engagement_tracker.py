import unittest
from datetime import datetime
from VlogForge.core.engagement_tracker import EngagementTracker


class TestEngagementTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = EngagementTracker()
        self.mock_data = [
            {"Date": "2025-02-01", "Views": 1000, "Likes": 150, "Comments": 20},
            {"Date": "2025-02-02", "Views": 800, "Likes": 120, "Comments": 15},
            {"Date": "2025-02-03", "Views": 1500, "Likes": 300, "Comments": 50},
            {"Date": "2025-02-04", "Views": 600, "Likes": 90, "Comments": 10},
        ]

    def test_engagement_rate_calculation(self):
        rates = self.tracker.calculate_engagement_rates(self.mock_data)
        expected_rates = [
            (150 + 20) / 1000 * 100,
            (120 + 15) / 800 * 100,
            (300 + 50) / 1500 * 100,
            (90 + 10) / 600 * 100
        ]

        # Compare each rate with tolerance for floating-point precision
        for actual, expected in zip(rates, expected_rates):
            self.assertAlmostEqual(actual, expected, places=2)

    def test_generate_engagement_heatmap(self):
        heatmap = self.tracker.generate_engagement_heatmap(self.mock_data)
        self.assertFalse(heatmap.empty)
        self.assertIn(10, heatmap.columns)
        self.assertIn('Saturday', heatmap.index)

    def test_empty_data(self):
        heatmap = self.tracker.generate_engagement_heatmap([])
        self.assertTrue(heatmap.empty)

    def test_growth_trend_analysis(self):
        growth_trend = self.tracker.analyze_growth_trend(self.mock_data)
        self.assertIsInstance(growth_trend, dict)
        self.assertIn('average_engagement_rate', growth_trend)
        self.assertIn('growth_trend', growth_trend)

    def test_top_performing_content_detection(self):
        top_content = self.tracker.get_top_performing_content(self.mock_data)
        self.assertEqual(top_content['Date'], "2025-02-03")  # Highest engagement day

    def test_empty_data_handling(self):
        rates = self.tracker.calculate_engagement_rates([])
        self.assertEqual(rates, [])

        growth_trend = self.tracker.analyze_growth_trend([])
        self.assertEqual(growth_trend, {'average_engagement_rate': 0, 'growth_trend': []})

        top_content = self.tracker.get_top_performing_content([])
        self.assertIsNone(top_content)

if __name__ == '__main__':
    unittest.main()
