---
name: trading-agents
description: Run the TradingAgents multi-agent LLM analysis on a symbol and turn its rating into an order on Bybit TESTNET (crypto spot) or a MetaTrader 5 DEMO account (gold, forex). Use when the user asks to analyse a coin/gold/forex pair with TradingAgents, to place a test trade on Bybit or MT5, to check the bot's decision log, or to set up/repair the trading bot in trading/.
---

# TradingAgents → Bybit Testnet / MT5 Demo

Everything lives in `trading/` of this repo. Read `trading/README.md` for the
user-facing setup (it is in German; answer the user in German).

## Hard rules

- **Demo/testnet only.** `trading/agent_trader.py` hard-codes `testnet=True`
  for Bybit and aborts on any MT5 account that is not
  `ACCOUNT_TRADE_MODE_DEMO`. Never remove or bypass these checks and never add a
  live-trading switch: the account owner is a minor, and real-money accounts at
  Bybit and MT5 brokers require 18+.
- Never print, log or commit API keys. They belong only in `trading/.env`
  (git-ignored). Never ask the user to paste keys into chat.
- Default to a dry run; add `--execute` only when the user asks to place the
  order.
- Keep the risk limits from `.env` (`MAX_USDT_PER_TRADE`,
  `MAX_USDT_PER_SYMBOL`, `STOP_LOSS_PCT`, `MAX_RISK_PER_TRADE`). Do not raise
  them without the user asking, and say what changes when they do.
- Present ratings as the model's opinion, not financial advice.

## Commands (run inside `trading/`)

Python: `.venv/Scripts/python.exe` on Windows, `.venv/bin/python` elsewhere.
If `.venv` is missing, run `install.ps1` (Windows) or `install.sh`.

| Goal | Command |
|------|---------|
| Test connection, no AI, no order | `python agent_trader.py --venue bybit --symbol BTCUSDT --signal Buy` |
| AI analysis, show plan only | `python agent_trader.py --venue bybit --symbol BTCUSDT` |
| AI analysis + testnet order | `python agent_trader.py --venue bybit --symbol ETHUSDT --execute` |
| AI analysis + MT5 demo order | `python agent_trader.py --venue mt5 --symbol XAUUSD --execute` |
| Broker uses another gold name | `--symbol GOLD --yahoo GC=F` |

Rating mapping: Buy/Overweight → buy; Sell/Underweight → sell (Bybit: sell
holdings only, spot cannot short; MT5: close long, open short); Hold/REVIEW →
nothing.

Decisions are appended to `trading/logs/decisions.csv`; full AI reports are
saved under `~/.tradingagents`. When asked "how is the bot doing", read the CSV
and summarise signals and results.

## Notes

- MetaTrader5 Python package exists only for Windows and needs the MT5 terminal
  running with Algo Trading enabled.
- TradingAgents is pinned to a commit in `trading/requirements.txt`; models and
  provider come from `TRADINGAGENTS_*` variables in `trading/.env` (cheap
  defaults: Haiku 4.5 quick, Sonnet 5 deep).
