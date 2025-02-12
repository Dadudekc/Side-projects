import unittest
from datetime import datetime
from textblob import TextBlob
import random

class BatchContentGenerator:
    def __init__(self):
        self.generated_scripts = []

    def generate_scripts(self, trade_recaps, include_takeaways=True, include_lessons=True, include_next_steps=True, custom_headers=None, tags=None, tone='neutral', content_length='medium'):
        if not trade_recaps:
            return {"success": False, "message": "No trade recaps provided."}

        scripts = []
        for recap in trade_recaps:
            sentiment = self.analyze_sentiment(recap)
            highlights = self.extract_key_insights(recap)
            quote = self.generate_dynamic_quote(sentiment)
            story = self.storytelling_mode(recap)
            script = self._generate_script(recap, include_takeaways, include_lessons, include_next_steps, custom_headers, tags, tone, sentiment, highlights, quote, story, content_length)
            scripts.append(script)

        self.generated_scripts.extend(scripts)
        self.auto_save_drafts()
        return {"success": True, "scripts": scripts}

    def _generate_script(self, recap, include_takeaways, include_lessons, include_next_steps, custom_headers, tags, tone, sentiment, highlights, quote, story, content_length):
        tone_templates = {
            'motivational': "Stay focused, stay driven. Every trade is a step forward.",
            'educational': "Let's break this down for better understanding.",
            'reflective': "Reflect on the journey, learn from each step.",
            'neutral': "Here's the breakdown of today's trade."
        }

        header_takeaways = custom_headers.get("takeaways", "Key Takeaways") if custom_headers else "Key Takeaways"
        header_lessons = custom_headers.get("lessons", "Lessons Learned") if custom_headers else "Lessons Learned"
        header_next_steps = custom_headers.get("next_steps", "Next Steps") if custom_headers else "Next Steps"

        script = f"Vlog Script:\nDate: {datetime.now().strftime('%Y-%m-%d')}\nRecap: {recap}\nTone: {tone_templates.get(tone, tone_templates['neutral'])}\nSentiment: {sentiment}\nHighlights: {highlights}\nQuote: {quote}\nStory: {story}"

        if tags:
            script += f"\nTags: {' '.join(tags)}"

        if include_takeaways:
            script += f"\n{header_takeaways}:\n- Identify winning setups\n- Recognize patterns\n- Improve entry/exit timing"
        if include_lessons:
            script += f"\n{header_lessons}:\n- Avoid overtrading\n- Stick to the plan\n- Review mistakes"
        if include_next_steps:
            script += f"\n{header_next_steps}:\n- Set goals for the next trading session\n- Adjust strategies if needed\n- Focus on risk management"

        # Adjust content length
        if content_length == 'short':
            script = '\n'.join(script.split('\n')[:5])
        elif content_length == 'detailed':
            script += "\nDetailed Analysis:\n- Market conditions\n- Entry/Exit strategies\n- Lessons learned in detail"

        return script

    def analyze_sentiment(self, recap):
        analysis = TextBlob(recap)
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"

    def extract_key_insights(self, recap):
        words = recap.split()
        return ' '.join(words[:5]) + "..." if len(words) > 5 else recap

    def generate_dynamic_quote(self, sentiment):
        quotes = {
            "Positive": ["Success is not final; failure is not fatal.", "Celebrate small wins every day."],
            "Neutral": ["Consistency is the key to mastery.", "Stay the course, no matter the result."],
            "Negative": ["Mistakes are proof that you're trying.", "Failure is the foundation of growth."]
        }
        return random.choice(quotes.get(sentiment, quotes["Neutral"]))

    def storytelling_mode(self, recap):
        return f"Once upon a trade, a decision was made: {recap}"  # Basic narrative hook

    def auto_save_drafts(self):
        with open('drafts.txt', 'w') as file:
            for script in self.generated_scripts:
                file.write(script + '\n---\n')

class TestBatchContentGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = BatchContentGenerator()

    def test_generate_scripts_success(self):
        trade_recaps = ["Trade 1 recap", "Trade 2 recap"]
        result = self.generator.generate_scripts(trade_recaps)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["scripts"]), 2)
        self.assertIn("Trade 1 recap", result["scripts"][0])
        self.assertIn("Trade 2 recap", result["scripts"][1])

    def test_generate_scripts_no_input(self):
        result = self.generator.generate_scripts([])
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "No trade recaps provided.")

    def test_generated_scripts_persistence(self):
        trade_recaps = ["Trade 1 recap"]
        self.generator.generate_scripts(trade_recaps)
        self.assertEqual(len(self.generator.generated_scripts), 1)
        self.assertIn("Trade 1 recap", self.generator.generated_scripts[0])

    def test_dynamic_quote_generation(self):
        positive_quote = self.generator.generate_dynamic_quote("Positive")
        self.assertIn(positive_quote, ["Success is not final; failure is not fatal.", "Celebrate small wins every day."])

    def test_storytelling_mode(self):
        recap = "A bold trade decision."
        story = self.generator.storytelling_mode(recap)
        self.assertIn("Once upon a trade, a decision was made:", story)

    def test_auto_save_drafts(self):
        trade_recaps = ["Auto-save draft test"]
        self.generator.generate_scripts(trade_recaps)
        with open('drafts.txt', 'r') as file:
            content = file.read()
        self.assertIn("Auto-save draft test", content)

    def test_adaptive_content_length(self):
        recap = "A comprehensive trade recap with lots of details."
        result = self.generator.generate_scripts([recap], content_length='short')
        short_script = result["scripts"][0]
        self.assertLessEqual(len(short_script.split('\n')), 5)

        result_detailed = self.generator.generate_scripts([recap], content_length='detailed')
        detailed_script = result_detailed["scripts"][0]
        self.assertIn("Detailed Analysis:", detailed_script)

if __name__ == '__main__':
    unittest.main()
