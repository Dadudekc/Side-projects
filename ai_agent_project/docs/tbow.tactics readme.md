# Tbow Tactic Trading Bot

## Overview
The **Tbow Tactic Trading Bot** automates stock trading using MACD curl detection and Alpaca API execution. It includes:
- **TbowScanner** → Detects MACD curl signals.
- **TbowTradeExecutor** → Places trades via Alpaca.
- **TbowTacticAgent** → Orchestrates trading & risk management.
- **Unit Tests** → Ensures functionality via mocked API calls.

## Folder Structure
```
agents/
├── core/
│   ├── tbow_tactic_agent.py  # Main trading logic
│   ├── utilities/
│   │   ├── tbow_scanner.py  # MACD Scanner
│   │   ├── tbow_trade_executor.py  # Trade Execution

# Tests
├── tests/
│   ├── test_tbow_tactic_agent.py  # Tests for trading agent
│   ├── test_tbow_scanner.py  # Tests for scanner logic
│   ├── test_tbow_trade_executor.py  # Tests for trade execution
```

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   Create a `.env` file with:
   ```
   ALPACA_API_KEY=your_api_key
   ALPACA_SECRET_KEY=your_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

4. **Run Unit Tests**
   ```bash
   python -m unittest discover tests/
   ```

5. **Run the Trading Agent**
   ```python
   from agents.core.tbow_tactic_agent import TbowTacticAgent
   
   agent = TbowTacticAgent(api_key, api_secret, base_url)
   agent.execute_trading_strategy("AAPL", qty=10)
   ```

## Next Steps
- **Expand Indicators** → Add RSI, VWAP confirmations.
- **Enhance Risk Management** → Improve stop-loss logic.
- **Deploy Live** → Transition from paper trading to real funds.

🚀 Happy Trading!

