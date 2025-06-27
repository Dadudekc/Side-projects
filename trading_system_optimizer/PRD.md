# Trading System Optimizer Product Requirements Document

## Purpose
The Trading System Optimizer (TSO) helps traders log, analyze and improve their strategies. It provides a GUI for recording trades, generates analytics such as equity curves, and can send notifications via Discord.

## Target Users
- Individual traders tracking performance
- Hobbyists experimenting with strategy tweaks

## Features
- PyQt GUI with logging and statistics windows
- YAML trade journal and analytics modules
- Performance analyzer and strategy insights
- Discord bot for trade notifications
- Configurable settings via `config.py`

## Success Metrics
- Users can record trades and view equity curve plots
- Analytical summaries generated without errors
- Discord notifications work when configured

## Dependencies
- PyQt5, pandas, yaml
- Discord webhook URL for bot integration
