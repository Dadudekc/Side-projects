import os
from fpdf import FPDF
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
from datetime import datetime
import unittest


class PDFReportGenerator:
    def __init__(self, title, metrics, previous_metrics=None, theme='light'):
        self.title = title
        self.metrics = self._normalize_metrics(metrics)
        self.previous_metrics = self._normalize_metrics(previous_metrics) if previous_metrics else None
        self.theme = theme

    def _normalize_metrics(self, metrics):
        normalized = {}
        for k, v in metrics.items():
            if isinstance(v, (int, float)):
                normalized[k] = f"{v}" if k not in ["CTR", "Engagement Rate"] else f"{v}%"
            elif isinstance(v, str):
                normalized[k] = v
            else:
                normalized[k] = "0"
        return normalized

    def _add_title(self, pdf):
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, self.title, ln=True)
        pdf.ln(10)

    def _add_metrics(self, pdf):
        pdf.set_font("Arial", "", 12)
        for metric, value in self.metrics.items():
            pdf.cell(0, 10, f"{metric}: {value}", ln=True)
        pdf.ln(5)

    def _add_trend_analysis(self, pdf):
        if not self.previous_metrics:
            return
        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, "Trend Analysis:", ln=True)
        for key in self.metrics:
            current = float(self.metrics.get(key, '0').replace('%', ''))
            previous = float(self.previous_metrics.get(key, '0').replace('%', ''))
            change = current - previous
            trend = "Increased" if change > 0 else "Decreased" if change < 0 else "No Change"
            pdf.cell(0, 10, f"{key}: {trend} by {abs(change):.2f}", ln=True)
        pdf.ln(5)

    def _add_summary_insights(self, pdf):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary Insights:", ln=True)
        insights = []
        if float(self.metrics.get("Engagement Rate", '0').replace('%', '')) > 10:
            insights.append("Great engagement rate! Keep up the good work.")
        if float(self.metrics.get("CTR", '0').replace('%', '')) < 2:
            insights.append("Consider improving call-to-action strategies for better CTR.")
        for insight in insights:
            pdf.multi_cell(0, 8, f"- {insight}")
        pdf.ln(5)

    def _add_footer(self, pdf):
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, f"Generated on {timestamp}", 0, 0, "C")

    def _generate_chart(self, output_path):
        metrics = {k: float(v.replace('%', '')) if '%' in v else float(v) for k, v in self.metrics.items()}
        plt.figure(figsize=(6, 4))
        plt.bar(metrics.keys(), metrics.values(), color='skyblue')
        plt.title('Performance Metrics Overview')
        plt.xticks(rotation=45)
        chart_path = output_path.replace('.pdf', '_chart.png')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def generate_pdf(self, output_path):
        pdf = FPDF()
        pdf.add_page()
        self._add_title(pdf)
        self._add_metrics(pdf)
        self._add_trend_analysis(pdf)
        self._add_summary_insights(pdf)

        chart_path = self._generate_chart(output_path)
        pdf.image(chart_path, x=10, y=None, w=180)

        self._add_footer(pdf)
        pdf.output(output_path)

        if os.path.exists(chart_path):
            os.remove(chart_path)


def generate_pdf_report(data, period, output_path, previous_data=None):
    if period.lower() not in ["weekly", "monthly"]:
        raise ValueError("Period must be 'weekly' or 'monthly'")

    title = f"{period.capitalize()} Performance Report"
    metrics = {
        "Likes": data.get("likes", 0),
        "Comments": data.get("comments", 0),
        "Shares": data.get("shares", 0),
        "Views": data.get("views", 0),
        "CTR": f"{data.get('ctr', 0)}%",
        "Engagement Rate": f"{data.get('engagement_rate', 0)}%"
    }

    previous_metrics = {
        "Likes": previous_data.get("likes", 0),
        "Comments": previous_data.get("comments", 0),
        "Shares": previous_data.get("shares", 0),
        "Views": previous_data.get("views", 0),
        "CTR": f"{previous_data.get('ctr', 0)}%",
        "Engagement Rate": f"{previous_data.get('engagement_rate', 0)}%"
    } if previous_data else None

    generator = PDFReportGenerator(title, metrics, previous_metrics)
    generator.generate_pdf(output_path)


# Unit Tests
class TestPDFReportGenerator(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "likes": 100,
            "comments": 50,
            "shares": 20,
            "views": 1000,
            "ctr": 5.5,
            "engagement_rate": 10.2
        }
        self.previous_data = {
            "likes": 80,
            "comments": 40,
            "shares": 25,
            "views": 950,
            "ctr": 4.8,
            "engagement_rate": 9.5
        }
        self.output_file = "test_report.pdf"
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_generate_weekly_report_with_trends(self):
        generate_pdf_report(self.test_data, "weekly", self.output_file, self.previous_data)
        self.assertTrue(os.path.exists(self.output_file))
        reader = PdfReader(self.output_file)
        extracted_text = "".join([page.extract_text() for page in reader.pages])
        self.assertIn("Trend Analysis:", extracted_text)
        self.assertIn("Likes: Increased by 20.00", extracted_text)
        self.assertIn("Shares: Decreased by 5.00", extracted_text)

    def test_summary_insights(self):
        generate_pdf_report(self.test_data, "monthly", self.output_file)
        reader = PdfReader(self.output_file)
        extracted_text = "".join([page.extract_text() for page in reader.pages])
        self.assertIn("Summary Insights:", extracted_text)
        self.assertIn("Great engagement rate!", extracted_text)

    def test_invalid_period(self):
        with self.assertRaises(ValueError):
            generate_pdf_report(self.test_data, "daily", self.output_file)


# Run the tests
if __name__ == '__main__':
    unittest.main()
