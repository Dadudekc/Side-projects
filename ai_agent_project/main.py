#!/usr/bin/env python
"""
Main module for the Overnight AI Debugger.

This script runs an immediate debugging cycle and then schedules additional cycles to run hourly.
It is designed to work with the debugging ecosystem, integrating memory management, structured 
data analysis, and AI-driven error detection.

Dependencies:
- logging: Used for structured logging of debugging cycles.
- schedule: Handles automated execution of debugging cycles.
- time: Controls timing and sleep intervals between scheduled runs.
- debugger_core.overnight_debugging: The core function responsible for executing a debugging cycle.
- debugging_strategy.DebuggingStrategy: Defines the debugging approach and strategies.

Usage:
  python main.py

Behavior:
- Initializes logging.
- Runs an immediate debugging cycle using `overnight_debugging()`.
- Schedules future debugging cycles to run every hour.
- Enters an infinite loop to continuously check and execute scheduled debugging tasks.
"""

import logging
import schedule
import time

from debugger_core import overnight_debugging
from debugging_strategy import DebuggingStrategy

def main():
    """Sets up and runs the Overnight AI Debugger."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    logging.info("Initializing Overnight AI Debugger...")

    # Create the debugging strategy instance
    debug_strategy = DebuggingStrategy()

    logging.info("Running initial debugging cycle...")
    overnight_debugging(debug_strategy)

    # Schedule future cycles to run every hour
    schedule.every().hour.do(lambda: overnight_debugging(debug_strategy))
    logging.info("Scheduled hourly debugging cycles. The system will monitor and execute them.")

    # Enter an infinite loop to process scheduled tasks
    while True:
        schedule.run_pending()
        logging.debug("Waiting for the next scheduled debugging cycle...")
        time.sleep(60)  # Sleep for 60 seconds before checking again

if __name__ == "__main__":
    main()
