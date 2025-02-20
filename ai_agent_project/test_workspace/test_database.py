import sqlite3
from ai_refactor_agent import initialize_database, save_ai_suggestion, get_human_feedback, submit_human_feedback

DB_FILE = "ai_refactor_reviews.db"

def test_database():
    initialize_database()

    # Insert test data
    test_file = "test_script.py"
    original_code = "print('Hello, world!')"
    ai_suggestion = "print('Hello, AI-powered world!')"
    
    save_ai_suggestion(test_file, original_code, ai_suggestion)

    # Retrieve pending suggestions
    pending_reviews = get_human_feedback()
    assert len(pending_reviews) > 0, "❌ No pending reviews found."

    # Submit feedback
    review_id = pending_reviews[0][0]
    submit_human_feedback(review_id, "approved")

    print("✅ Database tests passed!")

if __name__ == "__main__":
    test_database()
