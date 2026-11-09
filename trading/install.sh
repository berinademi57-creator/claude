#!/usr/bin/env bash
# Installation unter macOS/Linux (nur Bybit – MetaTrader5 gibt es nur für Windows).
#   cd trading && bash install.sh
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "trading/.env angelegt - jetzt deine Keys eintragen."
fi

./.venv/bin/python -c "import tradingagents, pybit; print('TradingAgents', tradingagents.__version__, '+ pybit OK')"
echo "Fertig. Test ohne KI:  ./.venv/bin/python agent_trader.py --venue bybit --symbol BTCUSDT --signal Buy"
