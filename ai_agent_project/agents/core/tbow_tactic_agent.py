import logging
from agents.core.AgentBase import AgentBase
from ai_engine.models.apis.market_data import MarketData
from ai_engine.models.trade_analyzer import TradeAnalyzer
from utils.scheduler import TaskScheduler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TbowTacticAgent(AgentBase):
    """
    AI-driven trading agent that analyzes market trends and generates Tbow Tactic trade strategies.
    """

    def __init__(self):
        super().__init__(name="TbowTacticAgent")
        self.market_data = MarketData()
        self.trade_analyzer = TradeAnalyzer()
        self.scheduler = TaskScheduler()

    def generate_trade_plan(self, stock_symbol: str) -> dict:
        """
        Fetches real-time stock data and generates a Tbow Tactic-based trade strategy.

        Args:
            stock_symbol (str): The stock ticker symbol.

        Returns:
            dict: Trade plan details.
        """
        stock_info = self.market_data.get_stock_data(stock_symbol)
        if not stock_info:
            return {"status": "error", "message": f"Failed to retrieve data for {stock_symbol}."}

        trade_plan = self.trade_analyzer.analyze(stock_info)
        return {"status": "success", "trade_plan": trade_plan}

    def schedule_trade_updates(self, interval: int = 60):
        """
        Schedules periodic trade strategy updates.

        Args:
            interval (int): Time in minutes for updates (default: 60).
        """
        self.scheduler.schedule_task(self.generate_trade_plan, interval)

    def solve_task(self, task: str, **kwargs) -> dict:
        """
        Executes specific trade-related tasks.

        Args:
            task (str): Task name.
            **kwargs: Additional parameters.

        Returns:
            dict: Task execution result.
        """
        if task == "generate_trade_plan":
            return self.generate_trade_plan(kwargs.get("symbol", "TSLA"))
        elif task == "schedule_updates":
            self.schedule_trade_updates(kwargs.get("interval", 60))
            return {"status": "success", "message": "Trade updates scheduled."}
        else:
            return {"status": "error", "message": f"Unknown task '{task}'."}

    def shutdown(self):
        """Shuts down the agent safely."""
        logger.info(f"{self.name} is shutting down.")
