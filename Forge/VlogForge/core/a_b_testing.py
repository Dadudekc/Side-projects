#!/usr/bin/env python3
"""
a_b_testing.py

This module implements A/B testing logic for Vlog Forge.
It provides the ABTestExperiment class to:

    • Create experiments with multiple content variants (e.g. titles, captions, posting times).
    • Record engagement metrics for each variant (likes, comments, shares, click-through rates).
    • Determine if one variant is statistically significantly better than the others.
    • Generate performance reports summarizing test results.

The module is developed using a TDD approach.
"""

import statistics
from scipy import stats
import unittest


class ABTestExperiment:
    def __init__(self, name):
        self.name = name
        self.variants = {}

    def add_variant(self, variant_name, content):
        if variant_name in self.variants:
            raise ValueError(f"Variant '{variant_name}' already exists.")
        self.variants[variant_name] = {
            'content': content,
            'metrics': {}
        }

    def record_engagement(self, variant_name, metric_name, value):
        if variant_name not in self.variants:
            raise ValueError(f"Variant '{variant_name}' not found.")
        if metric_name not in self.variants[variant_name]['metrics']:
            self.variants[variant_name]['metrics'][metric_name] = []
        self.variants[variant_name]['metrics'][metric_name].append(value)

    def get_metric_data(self, metric_name):
        data = {}
        for variant, details in self.variants.items():
            data[variant] = details['metrics'].get(metric_name, [])
        return data

    def determine_winner(self, metric_name, significance_level=0.05):
        data = self.get_metric_data(metric_name)
        means = {variant: statistics.mean(values) if values else float('-inf')
                 for variant, values in data.items()}

        best_variant = max(means, key=means.get)
        best_data = data[best_variant]
        if len(best_data) < 2:
            return None

        for variant, values in data.items():
            if variant == best_variant or len(values) < 2:
                continue
            t_stat, p_val = stats.ttest_ind(best_data, values, equal_var=False)
            if p_val >= significance_level:
                return None
        return best_variant

    def generate_report(self, metric_name):
        data = self.get_metric_data(metric_name)
        report = {}
        for variant, values in data.items():
            report[variant] = {
                'count': len(values),
                'mean': statistics.mean(values) if values else None,
                'stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'values': values
            }
        return report


# ===========================
# Unit Tests for ABTestExperiment
# ===========================

class TestABTestExperiment(unittest.TestCase):
    def setUp(self):
        self.experiment = ABTestExperiment("Content Optimization Test")
        self.experiment.add_variant("Variant A", {"title": "Title A", "caption": "Caption A", "post_time": "10:00 AM"})
        self.experiment.add_variant("Variant B", {"title": "Title B", "caption": "Caption B", "post_time": "2:00 PM"})

    def test_add_variant(self):
        with self.assertRaises(ValueError):
            self.experiment.add_variant("Variant A", {"title": "Duplicate Title", "caption": "Duplicate Caption", "post_time": "3:00 PM"})

    def test_record_engagement_invalid_variant(self):
        with self.assertRaises(ValueError):
            self.experiment.record_engagement("Variant C", "likes", 100)

    def test_record_and_retrieve_engagement(self):
        self.experiment.record_engagement("Variant A", "likes", 150)
        self.experiment.record_engagement("Variant B", "likes", 120)
        data = self.experiment.get_metric_data("likes")
        self.assertEqual(data["Variant A"], [150])
        self.assertEqual(data["Variant B"], [120])

    def test_determine_winner_no_significant_difference(self):
        self.experiment.record_engagement("Variant A", "likes", 100)
        self.experiment.record_engagement("Variant A", "likes", 102)
        self.experiment.record_engagement("Variant B", "likes", 101)
        self.experiment.record_engagement("Variant B", "likes", 103)
        winner = self.experiment.determine_winner("likes")
        self.assertIsNone(winner)

    def test_determine_winner_with_significant_difference(self):
        self.experiment.record_engagement("Variant A", "likes", 200)
        self.experiment.record_engagement("Variant A", "likes", 210)
        self.experiment.record_engagement("Variant B", "likes", 100)
        self.experiment.record_engagement("Variant B", "likes", 105)
        winner = self.experiment.determine_winner("likes")
        self.assertEqual(winner, "Variant A")

    def test_generate_performance_report(self):
        self.experiment.record_engagement("Variant A", "likes", 180)
        self.experiment.record_engagement("Variant A", "likes", 190)
        self.experiment.record_engagement("Variant B", "likes", 160)
        self.experiment.record_engagement("Variant B", "likes", 170)
        report = self.experiment.generate_report("likes")
        self.assertEqual(report["Variant A"]["count"], 2)
        self.assertEqual(report["Variant B"]["count"], 2)
        self.assertAlmostEqual(report["Variant A"]["mean"], 185)
        self.assertAlmostEqual(report["Variant B"]["mean"], 165)


if __name__ == '__main__':
    unittest.main(verbosity=2)
