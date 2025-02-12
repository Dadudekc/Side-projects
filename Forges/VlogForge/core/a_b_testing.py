#!/usr/bin/env python3
"""
a_b_testing.py

This module implements A/B testing logic for Vlog Forge.
It provides the ABTestExperiment class to:

    • Create experiments with multiple content variants (e.g. titles, captions, posting times).
    • Record engagement metrics for each variant (likes, comments, shares, click-through rates).
    • Determine if one variant is statistically significantly better than the others.
    • Generate performance reports summarizing test results.
    • Persist experiment data to file with self-healing capabilities.

The module is developed using a Test-Driven Development (TDD) approach.
"""

import os
import json
import logging
import statistics
from scipy import stats
import unittest

# Configure logging for this module.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ABTestExperiment:
    def __init__(self, name):
        """
        Initialize a new A/B test experiment.

        :param name: Name or identifier for the experiment.
        """
        if not name:
            raise ValueError("Experiment name is required in production.")
        self.name = name
        self.variants = {}  # Maps variant names to their content and recorded metrics

    def add_variant(self, variant_name, content):
        """
        Add a new variant to the experiment.

        :param variant_name: Unique identifier for the variant.
        :param content: Dictionary containing content details (e.g., title, caption, post_time).
        :raises ValueError: If the variant already exists.
        """
        if variant_name in self.variants:
            raise ValueError(f"Variant '{variant_name}' already exists.")
        self.variants[variant_name] = {
            'content': content,
            'metrics': {}  # Will hold lists of recorded values for each metric
        }

    def record_engagement(self, variant_name, metric_name, value):
        """
        Record an engagement metric value for a given variant.

        :param variant_name: The variant to record the metric for.
        :param metric_name: The name of the metric (e.g., 'likes', 'comments').
        :param value: The recorded metric value.
        :raises ValueError: If the variant does not exist.
        """
        if variant_name not in self.variants:
            raise ValueError(f"Variant '{variant_name}' not found.")
        if metric_name not in self.variants[variant_name]['metrics']:
            self.variants[variant_name]['metrics'][metric_name] = []
        self.variants[variant_name]['metrics'][metric_name].append(value)

    def get_metric_data(self, metric_name):
        """
        Retrieve all recorded data for a given metric across all variants.

        :param metric_name: The metric name.
        :return: Dictionary mapping variant names to lists of recorded metric values.
        """
        data = {}
        for variant, details in self.variants.items():
            data[variant] = details['metrics'].get(metric_name, [])
        return data

    def determine_winner(self, metric_name, significance_level=0.05):
        """
        Determine the winning variant for a specified metric.

        The method compares the means of the recorded metric values for each variant.
        It uses a two-sample t-test (with unequal variances) to compare the best-performing
        variant against each of the others. Only if the best variant is statistically significantly
        better (p < significance_level) than all others (with sufficient data) is it declared the winner.

        :param metric_name: The engagement metric to evaluate.
        :param significance_level: The p-value threshold for statistical significance.
        :return: The winning variant name if a clear winner is identified; otherwise, None.
        """
        data = self.get_metric_data(metric_name)
        # Calculate mean for each variant; if no data, treat as worst.
        means = {variant: statistics.mean(values) if values else float('-inf')
                 for variant, values in data.items()}

        best_variant = max(means, key=means.get)
        best_data = data[best_variant]
        # Require at least two data points to perform a t-test
        if len(best_data) < 2:
            return None

        # Compare best variant with every other variant (if that variant has sufficient data)
        for variant, values in data.items():
            if variant == best_variant or len(values) < 2:
                continue
            t_stat, p_val = stats.ttest_ind(best_data, values, equal_var=False)
            if p_val >= significance_level:
                return None  # Difference not statistically significant
        return best_variant

    def generate_report(self, metric_name):
        """
        Generate a performance report summarizing the recorded data for a given metric.

        The report includes the count, mean, and standard deviation of the values for each variant.

        :param metric_name: The engagement metric to report on.
        :return: A dictionary with variant names as keys and their performance summaries as values.
        """
        data = self.get_metric_data(metric_name)
        report = {}
        for variant, values in data.items():
            if values:
                report[variant] = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
                    'values': values
                }
            else:
                report[variant] = {
                    'count': 0,
                    'mean': None,
                    'stdev': None,
                    'values': []
                }
        return report

    def to_dict(self):
        """
        Export the experiment data to a dictionary.
        """
        return {
            'name': self.name,
            'variants': self.variants
        }

    def save_to_file(self, file_path):
        """
        Save the experiment data to a JSON file.
        If a file already exists, it is backed up first.

        :param file_path: Path to the file where data will be saved.
        """
        try:
            if os.path.exists(file_path):
                # Backup existing file
                backup_path = file_path + ".bak"
                os.replace(file_path, backup_path)
                logging.info(f"Existing file backed up to {backup_path}.")
            with open(file_path, "w") as f:
                json.dump(self.to_dict(), f, indent=4)
            logging.info("Experiment data saved successfully.")
        except Exception as e:
            logging.error(f"Error saving experiment data: {e}")

    @classmethod
    def load_from_file(cls, file_path):
        """
        Load experiment data from a JSON file.
        If the file is missing or corrupted, a new experiment instance is returned,
        and the corrupt file is backed up.

        :param file_path: Path to the file from which data will be loaded.
        :return: An instance of ABTestExperiment.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            if "name" not in data or "variants" not in data:
                raise ValueError("Invalid experiment data structure.")
            experiment = cls(data["name"])
            experiment.variants = data["variants"]
            logging.info("Experiment data loaded successfully.")
            return experiment
        except Exception as e:
            logging.error(f"Error loading experiment data: {e}")
            # If file exists, back it up as corrupt
            if os.path.exists(file_path):
                backup_path = file_path + ".corrupt"
                os.replace(file_path, backup_path)
                logging.info(f"Corrupt file backed up to {backup_path}.")
            # Create a new instance as a self-healing measure
            new_experiment = cls("Healed Experiment")
            logging.info("Created a new experiment instance as self-healing measure.")
            return new_experiment


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
        # Similar data in both variants should yield no statistically significant winner.
        self.experiment.record_engagement("Variant A", "likes", 100)
        self.experiment.record_engagement("Variant A", "likes", 102)
        self.experiment.record_engagement("Variant B", "likes", 101)
        self.experiment.record_engagement("Variant B", "likes", 103)
        winner = self.experiment.determine_winner("likes")
        self.assertIsNone(winner)

    def test_determine_winner_with_significant_difference(self):
        # A clear performance gap should yield a winner.
        self.experiment.record_engagement("Variant A", "likes", 200)
        self.experiment.record_engagement("Variant A", "likes", 210)
        self.experiment.record_engagement("Variant B", "likes", 100)
        self.experiment.record_engagement("Variant B", "likes", 105)
        winner = self.experiment.determine_winner("likes")
        self.assertEqual(winner, "Variant A")

    def test_generate_performance_report(self):
        # Before recording any engagement, report should show zero count and None for mean.
        report = self.experiment.generate_report("likes")
        self.assertEqual(report["Variant A"]["count"], 0)
        self.assertIsNone(report["Variant A"]["mean"])
        # After recording, the report should reflect the correct statistics.
        self.experiment.record_engagement("Variant A", "likes", 180)
        self.experiment.record_engagement("Variant A", "likes", 190)
        self.experiment.record_engagement("Variant B", "likes", 160)
        self.experiment.record_engagement("Variant B", "likes", 170)
        report = self.experiment.generate_report("likes")
        self.assertEqual(report["Variant A"]["count"], 2)
        self.assertEqual(report["Variant B"]["count"], 2)
        self.assertAlmostEqual(report["Variant A"]["mean"], 185)
        self.assertAlmostEqual(report["Variant B"]["mean"], 165)

    def test_save_and_load(self):
        # Test saving to a file and then loading from it.
        file_path = "experiment_test.json"
        # Ensure any existing test file is removed.
        if os.path.exists(file_path):
            os.remove(file_path)
        self.experiment.record_engagement("Variant A", "likes", 150)
        self.experiment.save_to_file(file_path)
        loaded_experiment = ABTestExperiment.load_from_file(file_path)
        self.assertEqual(loaded_experiment.name, self.experiment.name)
        data = loaded_experiment.get_metric_data("likes")
        self.assertEqual(data["Variant A"], [150])
        # Cleanup test file(s)
        for f in [file_path, file_path + ".bak", file_path + ".corrupt"]:
            if os.path.exists(f):
                os.remove(f)


if __name__ == '__main__':
    # Run unit tests with increased verbosity.
    unittest.main(verbosity=2)
