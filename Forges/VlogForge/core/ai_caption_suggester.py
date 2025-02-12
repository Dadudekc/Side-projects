import unittest
from typing import List, Optional
import re

class AICaptionSuggester:
    def suggest_captions(self, content: str, max_length: Optional[int] = None, highlight: bool = False, seo_optimized: bool = False) -> List[str]:
        if not content.strip():
            return ["Content cannot be empty."]

        # Normalize multiline content, remove extra spaces, and handle punctuation
        base_caption = " ".join(content.strip().splitlines()).strip()
        base_caption = " ".join(base_caption.split())  # Remove multiple spaces
        base_caption = base_caption.capitalize()

        # Apply keyword highlighting if enabled
        if highlight:
            keywords = [word for word in content.split() if len(word) > 2 or word.upper() == "AI"]
            for keyword in keywords:
                if keyword.upper() == "AI":
                    base_caption = re.sub(rf"\b{re.escape(keyword)}\b", f"**AI**", base_caption, flags=re.IGNORECASE)
                else:
                    base_caption = re.sub(rf"\b{re.escape(keyword)}\b", f"**{keyword.upper()}**", base_caption, flags=re.IGNORECASE)

        # Apply SEO optimization if enabled
        if seo_optimized:
            keywords = [word for word in content.split() if len(word) > 3]
            base_caption += " " + " ".join(keywords[:2])  # Add top 2 keywords for SEO

        captions = [
            f"Discover: {base_caption}",
            f"Why {base_caption} matters!",
            f"Top insights on {base_caption}",
            f"Unveiling the story behind {base_caption}",
            f"Quick thoughts: {base_caption}",
            f"Explore the future of {base_caption}",
            f"Insights that matter: {base_caption}",
            f"Is {base_caption} the future of marketing?",
            f"How will {base_caption} shape businesses in 2025?"
        ]

        # Apply length limiter if max_length is provided
        if max_length:
            captions = [caption[:max_length] for caption in captions]

        return captions

    def generate_ab_test_captions(self, content: str) -> List[str]:
        # Generate two slightly different captions for A/B testing
        base_captions = self.suggest_captions(content)
        if len(base_captions) >= 2:
            return [base_captions[0], base_captions[1]]
        return base_captions

    def generate_hashtags(self, content: str) -> List[str]:
        keywords = [word.strip(".,!?") for word in content.split() if len(word) > 2 or word.upper() == "AI"]
        hashtags = [f"#{word.upper()}" for word in keywords if word.isalpha() or word.upper() == "AI"]
        if "#AI" not in hashtags:
            hashtags.append("#AI")
        return list(set(hashtags))  # Remove duplicates

class TestAICaptionSuggester(unittest.TestCase):
    def setUp(self):
        self.suggester = AICaptionSuggester()

    def test_suggest_captions_with_valid_content(self):
        content = "AI in marketing"
        captions = self.suggester.suggest_captions(content)
        self.assertEqual(len(captions), 9)
        self.assertIn("Discover: Ai in marketing", captions)

    def test_suggest_captions_with_empty_content(self):
        content = "   "
        captions = self.suggester.suggest_captions(content)
        self.assertEqual(captions, ["Content cannot be empty."])

    def test_keyword_highlighting(self):
        content = "AI in marketing"
        captions = self.suggester.suggest_captions(content, highlight=True)
        self.assertIn("Discover: **AI** in **MARKETING**", captions)

    def test_question_based_captions(self):
        content = "AI in marketing"
        captions = self.suggester.suggest_captions(content)
        self.assertIn("Is Ai in marketing the future of marketing?", captions)

    def test_length_limiter(self):
        content = "The future of AI in modern business strategies"
        captions = self.suggester.suggest_captions(content, max_length=50)
        for caption in captions:
            self.assertLessEqual(len(caption), 50)

    def test_generate_hashtags(self):
        content = "AI in marketing"
        hashtags = self.suggester.generate_hashtags(content)
        expected_hashtags = ["#AI", "#MARKETING"]
        for hashtag in expected_hashtags:
            self.assertIn(hashtag, hashtags)

    def test_generate_ab_test_captions(self):
        content = "AI in business growth"
        ab_captions = self.suggester.generate_ab_test_captions(content)
        self.assertEqual(len(ab_captions), 2)
        self.assertNotEqual(ab_captions[0], ab_captions[1])

    def test_seo_optimized_captions(self):
        content = "Maximize growth with AI in business"
        captions = self.suggester.suggest_captions(content, seo_optimized=True)
        self.assertTrue(any("growth" in caption or "business" in caption for caption in captions))

if __name__ == '__main__':
    unittest.main()
