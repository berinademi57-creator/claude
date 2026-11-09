# Installation unter Windows (PowerShell im Ordner "trading" ausführen):
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\install.ps1
# Voraussetzungen: Python 3.12 (python.org, Haken bei "Add to PATH"), Git (git-scm.com)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "trading\.env angelegt - jetzt deine Keys eintragen (notepad .env)." -ForegroundColor Yellow
}

.\.venv\Scripts\python.exe -c "import tradingagents, pybit; print('TradingAgents', tradingagents.__version__, '+ pybit OK')"
.\.venv\Scripts\python.exe -c "import MetaTrader5 as m; print('MetaTrader5', m.__version__, 'OK')"
Write-Host "Fertig. Test ohne KI:  .\.venv\Scripts\python.exe agent_trader.py --venue bybit --symbol BTCUSDT --signal Buy" -ForegroundColor Green
