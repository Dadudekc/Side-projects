import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

class AutoPostScheduler:
    def __init__(self):
        self.scheduled_posts = []
        self.published_posts = []

    def schedule_post(self, content, scheduled_time, allow_past=False, current_time=None):
        if current_time is None:
            current_time = datetime.now()

        if not content or not scheduled_time:
            return {"success": False, "message": "Content and scheduled time are required."}

        if scheduled_time < current_time and not allow_past:
            return {"success": False, "message": "Cannot schedule a post in the past."}

        for post in self.scheduled_posts:
            if post["content"] == content and post["scheduled_time"] == scheduled_time:
                return {"success": False, "message": "Duplicate post for the same time is not allowed."}

        self.scheduled_posts.append({
            "content": content,
            "scheduled_time": scheduled_time
        })
        return {"success": True, "message": "Post scheduled successfully."}

    def reschedule_post(self, content, new_time):
        for post in self.scheduled_posts:
            if post["content"] == content:
                if new_time < datetime.now():
                    return {"success": False, "message": "Cannot reschedule to a past time."}
                post["scheduled_time"] = new_time
                return {"success": True, "message": "Post rescheduled successfully."}
        return {"success": False, "message": "Post not found."}

    def delete_post(self, content):
        for post in self.scheduled_posts:
            if post["content"] == content:
                self.scheduled_posts.remove(post)
                return {"success": True, "message": "Post deleted successfully."}
        return {"success": False, "message": "Post not found."}

    def auto_publish(self, current_time=None):
        if current_time is None:
            current_time = datetime.now()

        print("Scheduled posts before publishing:", self.scheduled_posts)

        published_posts = []
        remaining_posts = []

        for post in self.scheduled_posts:
            if post["scheduled_time"] <= current_time:
                published_posts.append(post)
            else:
                remaining_posts.append(post)

        self.published_posts.extend(published_posts)
        self.scheduled_posts = remaining_posts

        print("Published posts:", self.published_posts)
        print("Scheduled posts after publishing:", self.scheduled_posts)

        return self.published_posts

    def update_post_content(self, old_content, new_content):
        for post in self.scheduled_posts:
            if post["content"] == old_content:
                post["content"] = new_content
                return {"success": True, "message": "Post content updated successfully."}
        return {"success": False, "message": "Post not found."}

class TestAutoPostScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = AutoPostScheduler()

    def test_schedule_post(self):
        post_content = "This is a scheduled post."
        scheduled_time = datetime.now() + timedelta(hours=1)

        result = self.scheduler.schedule_post(post_content, scheduled_time)

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Post scheduled successfully.")
        self.assertIn(post_content, [post["content"] for post in self.scheduler.scheduled_posts])

    def test_cannot_schedule_post_in_past(self):
        post_content = "This is a past post."
        scheduled_time = datetime.now() - timedelta(hours=1)

        result = self.scheduler.schedule_post(post_content, scheduled_time)

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Cannot schedule a post in the past.")

    def test_prevent_duplicate_scheduled_posts(self):
        post_content = "This is a duplicate post."
        scheduled_time = datetime.now() + timedelta(hours=2)

        # Schedule the first post
        self.scheduler.schedule_post(post_content, scheduled_time)

        # Attempt to schedule the same post again for the same time
        result = self.scheduler.schedule_post(post_content, scheduled_time)

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Duplicate post for the same time is not allowed.")

    def test_reschedule_post(self):
        post_content = "This is a post to reschedule."
        original_time = datetime.now() + timedelta(hours=1)
        new_time = datetime.now() + timedelta(hours=3)

        self.scheduler.schedule_post(post_content, original_time)
        result = self.scheduler.reschedule_post(post_content, new_time)

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Post rescheduled successfully.")
        self.assertEqual(self.scheduler.scheduled_posts[0]["scheduled_time"], new_time)

    def test_delete_post(self):
        post_content = "This is a post to delete."
        scheduled_time = datetime.now() + timedelta(hours=1)

        self.scheduler.schedule_post(post_content, scheduled_time)
        result = self.scheduler.delete_post(post_content)

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Post deleted successfully.")
        self.assertNotIn(post_content, [post["content"] for post in self.scheduler.scheduled_posts])

    def test_auto_publish_behavior(self):
        fixed_current_time = datetime(2024, 1, 1, 12, 0, 0)
        due_post = {"content": "This post should be published.", "scheduled_time": fixed_current_time - timedelta(minutes=1)}
        future_post = {"content": "This post is scheduled for the future.", "scheduled_time": fixed_current_time + timedelta(hours=1)}

        # Schedule posts with the fixed current time
        due_result = self.scheduler.schedule_post(due_post["content"], due_post["scheduled_time"], allow_past=True, current_time=fixed_current_time)
        future_result = self.scheduler.schedule_post(future_post["content"], future_post["scheduled_time"], current_time=fixed_current_time)

        self.assertTrue(due_result["success"], "Failed to schedule due post.")
        self.assertTrue(future_result["success"], "Failed to schedule future post.")

        published_posts = self.scheduler.auto_publish(current_time=fixed_current_time)

        self.assertIn(due_post["content"], [post["content"] for post in published_posts])
        self.assertNotIn(future_post["content"], [post["content"] for post in published_posts])

        self.assertIn(future_post["content"], [post["content"] for post in self.scheduler.scheduled_posts])
        self.assertNotIn(due_post["content"], [post["content"] for post in self.scheduler.scheduled_posts])

    def test_update_post_content(self):
        post_content = "Original content."
        updated_content = "Updated content."
        scheduled_time = datetime.now() + timedelta(hours=1)

        # Schedule the original post
        self.scheduler.schedule_post(post_content, scheduled_time)

        # Update the post content
        result = self.scheduler.update_post_content(post_content, updated_content)

        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Post content updated successfully.")
        self.assertIn(updated_content, [post["content"] for post in self.scheduler.scheduled_posts])
        self.assertNotIn(post_content, [post["content"] for post in self.scheduler.scheduled_posts])

if __name__ == '__main__':
    unittest.main()
