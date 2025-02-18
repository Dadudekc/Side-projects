"""

This is the main module of the Overnight AI Debugger. It starts by running an immediate debugging cycle, 
and then schedules future cycles (for example, on an hourly basis). 

It uses the logging module to track its activities and schedule module to handle the scheduling of future debugging cycles.
The actual debugging is handled by the overnight_debugging function from the debugger_core module, 
which uses the DebuggingStrategy provided.

The main function handles the creation and configuration of a logging object with StreamHandler.
"""

#!/usr/bin/env python
"""
Main module for the Overnight AI Debugger.
Runs an immediate debugging cycle, then schedules future cycles.

Usage:
  python main.py
"""

import logging
import schedule
import time

from debugger_core import overnight_debugging
from debugging_strategy import DebuggingStrategy

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # Create our debugging strategy (for patch generation & application).
    debug_strategy = DebuggingStrategy()

    # Run immediate cycle
    overnight_debugging(debug_strategy)

    # Schedule future cycles, e.g. hourly
    schedule.every().hour.do(lambda: overnight_debugging(debug_strategy))
    logging.info("Overnight debugging scheduler started. Waiting for scheduled tasks...")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
