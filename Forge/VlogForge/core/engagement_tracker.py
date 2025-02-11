import pandas as pd
import numpy as np

class EngagementTracker:
    def calculate_engagement_rates(self, data):
        """
        Calculate the engagement rate for each data entry.
        Engagement Rate = ((Likes + Comments) / Views) * 100
        """
        if not data:
            return []

        return [
            round(((entry['Likes'] + entry['Comments']) / entry['Views']) * 100, 2)
            for entry in data if entry['Views'] > 0
        ]

    def analyze_growth_trend(self, data):
        """
        Analyze growth trends based on engagement rates.
        Returns the average engagement rate and a simple growth trend list.
        """
        if not data:
            return {'average_engagement_rate': 0, 'growth_trend': []}

        rates = self.calculate_engagement_rates(data)
        avg_rate = sum(rates) / len(rates) if rates else 0

        growth_trend = [
            {'Date': entry['Date'], 'EngagementRate': rate}
            for entry, rate in zip(data, rates)
        ]

        return {'average_engagement_rate': round(avg_rate, 2), 'growth_trend': growth_trend}

    def get_top_performing_content(self, data):
        """
        Identify the content with the highest engagement rate.
        """
        if not data:
            return None

        rates = self.calculate_engagement_rates(data)
        max_rate_index = rates.index(max(rates)) if rates else -1

        return data[max_rate_index] if max_rate_index >= 0 else None

    def generate_engagement_heatmap(self, data):
        """
        Generate an engagement heatmap based on day of the week and time of day.
        """
        if not data:
            return pd.DataFrame()

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df['DayOfWeek'] = df['Date'].dt.day_name()
        df['Hour'] = df['Date'].dt.hour

        # Calculate engagement rate if not already present
        if 'EngagementRate' not in df.columns:
            df['EngagementRate'] = self.calculate_engagement_rates(data)

        # Create pivot table for heatmap (Days as rows, Hours as columns)
        heatmap_data = pd.pivot_table(
            df,
            values='EngagementRate',
            index='DayOfWeek',
            columns='Hour',
            aggfunc=np.mean,
            fill_value=0
        )

        return heatmap_data
