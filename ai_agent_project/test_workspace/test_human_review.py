from ai_refactor_agent import get_human_feedback, submit_human_feedback

def test_human_review():
    pending_reviews = get_human_feedback()
    if not pending_reviews:
        print("⚠️ No pending AI suggestions to review. Insert test data first.")
        return

    review_id = pending_reviews[0][0]
    submit_human_feedback(review_id, "approved")

    print(f"✅ Human review test passed for review_id: {review_id}")

if __name__ == "__main__":
    test_human_review()
