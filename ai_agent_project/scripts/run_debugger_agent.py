"""

This script sets up and runs an AI-powered debugging agent. It initializes the Confidence Manager and Test Retry Manager, launching the debugging process to detect and attempt to fix failing tests with the help of AI-assisted patches. It runs the process with a retry limit of 3 tries, then logs the final results as either a success or failure. If the debugging fails, a review of log details is recommended. In the end, it provides a report of all final AI patch confidence scores for each attempted
"""

#!/usr/bin/env python
"""
run_debugger_agent.py

This script runs the AI-powered debugging system:
- Detects test failures.
- Attempts to fix errors using AI-assisted patching.
- Uses confidence-based retry logic.
- Rolls back changes if all fixes fail.
- Logs debugging session results.
"""

import logging
from test_retry_manager import AutoFixManager
from ai_confidence_manager import AIConfidenceManager

logger = logging.getLogger("RunDebuggerAgent")
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.info("🚀 Starting Debugger Agent...")

    # Initialize the AI confidence system and retry manager
    confidence_manager = AIConfidenceManager()
    test_manager = AutoFixManager()

    # Run the debugging process
    result = test_manager.retry_tests(max_retries=3)

    # Log final results
    if result["status"] == "success":
        logger.info("✅ Debugging completed successfully!")
    else:
        logger.error("🛑 Debugging failed. Review logs for details.")

    # Display AI confidence rankings for patches
    logger.info("📊 Final AI Patch Confidence Scores:")
    for error_sig, patches in confidence_manager.confidence_scores.items():
        for patch in patches:
            logger.info(f"🔹 Error: {error_sig}, Confidence: {patch['confidence']}, Reason: {patch['reason']}")

    logger.info("🎯 Debugging session completed!")
