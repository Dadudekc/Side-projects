"""Entry point for the trading journal GUI and CLI interface."""
from .gui.logger_window import run_logger

def main():
    """Run the trade logger GUI."""
    run_logger()

if __name__ == "__main__":
    main()
