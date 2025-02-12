import pandas as pd


class EngagementTracker:
    def calculate_engagement_rates(self, data):
        if not data:
            return []
        return [
            round(((entry['Likes'] + entry['Comments']) / entry['Views']) * 100, 2)
            for entry in data if entry['Views'] > 0
        ]

    def analyze_growth_trend(self, data):
        if not data:
            return {'average_engagement_rate': 0, 'growth_trend': []}
        rates = self.calculate_engagement_rates(data)
        avg_rate = sum(rates) / len(rates) if rates else 0
        growth_trend = [{'Date': entry['Date'], 'EngagementRate': rate} for entry, rate in zip(data, rates)]
        return {'average_engagement_rate': round(avg_rate, 2), 'growth_trend': growth_trend}

    def get_top_performing_content(self, data):
        if not data:
            return None
        rates = self.calculate_engagement_rates(data)
        max_rate_index = rates.index(max(rates)) if rates else -1
        return data[max_rate_index] if max_rate_index >= 0 else None

    def generate_engagement_heatmap(self, data):
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df['DayOfWeek'] = df['Date'].dt.day_name()
        df['Hour'] = df['Date'].dt.hour
        if 'EngagementRate' not in df.columns:
            df['EngagementRate'] = self.calculate_engagement_rates(data)
        all_hours = list(range(24))
        df = df.set_index(['DayOfWeek', 'Hour']).reindex(
            pd.MultiIndex.from_product([df['DayOfWeek'].unique(), all_hours], names=['DayOfWeek', 'Hour']),
            fill_value=0
        ).reset_index()
        heatmap_data = pd.pivot_table(
            df,
            values='EngagementRate',
            index='DayOfWeek',
            columns='Hour',
            aggfunc='mean',
            fill_value=0
        )
        return heatmap_data

    def track(self, content_data):
        """
        Track engagement metrics for the provided content data.
        Aggregates engagement rates, growth trends, and identifies top-performing content.
        """
        if not content_data:
            return {"message": "No content data provided."}

        engagement_rates = self.calculate_engagement_rates(content_data)
        growth_trend = self.analyze_growth_trend(content_data)
        top_content = self.get_top_performing_content(content_data)
        heatmap = self.generate_engagement_heatmap(content_data)

        return {
            "engagement_rates": engagement_rates,
            "growth_trend": growth_trend,
            "top_performing_content": top_content,
            "engagement_heatmap": heatmap
        }
