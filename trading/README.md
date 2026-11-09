# TradingAgents → Bybit Testnet / MetaTrader 5 Demo

[TradingAgents](https://github.com/TauricResearch/TradingAgents) ist ein KI-Team
(Analysten, Bull/Bear-Researcher, Trader, Risiko-Manager), das ein Symbol
analysiert und am Ende ein Rating ausgibt: **Buy / Overweight / Hold /
Underweight / Sell**. Selbst handelt es nicht – dafür ist `agent_trader.py` da.

```
TradingAgents (KI) ──► Rating ──► agent_trader.py ──► Bybit TESTNET  (Krypto Spot)
                                                  └─► MT5 DEMO-Konto (Gold, Forex …)
```

| Rating               | Bybit (Spot)                         | MetaTrader 5                         |
|----------------------|--------------------------------------|--------------------------------------|
| Buy / Overweight     | kaufen (max. `MAX_USDT_PER_TRADE`) + Stop-Loss | Long 0.01 Lot mit SL/TP (ATR)  |
| Sell / Underweight   | Bestand verkaufen (Spot kann nicht shorten) | Short 0.01 Lot, Long-Position schließen |
| Hold / REVIEW        | nichts                               | nichts                               |

## Warum nur Testnet/Demo?

Echtgeld-Konten bei Bybit und bei MT5-Brokern gibt es erst **ab 18** (Ausweis-
prüfung/KYC). Deshalb ist der Bot **fest** auf Spielgeld eingestellt:
- Bybit: `testnet=True` ist im Code verdrahtet, keine Einstellung dafür.
- MT5: Der Bot prüft das Konto und bricht ab, wenn es kein Demo-Konto ist.

Das ist auch inhaltlich sinnvoll: TradingAgents ist ein Forschungsprojekt, die
Ratings sind oft falsch. Lass es ein paar Wochen auf Demo laufen und schau in
`logs/decisions.csv`, ob es überhaupt Geld verdient hätte.

## Was du brauchst

1. **Windows-PC** (für MT5) mit **Python 3.12** und **Git**.
2. **KI-Key**: Anthropic-API-Key (console.anthropic.com, Prepaid ab 5 $; das
   Claude.ai-Abo zählt nicht). Eine Analyse mit Haiku/Sonnet kostet grob
   0,05–0,50 $. Kostenlos geht es mit einem lokalen Modell über Ollama
   (langsamer, schlechter).
3. **Bybit-Testnet-Account**: testnet.bybit.com → API-Key mit „Read-Write“ +
   „Spot Trade“ (ohne Auszahlungsrechte). Im Testnet gibt es Spielgeld über
   „Assets → Request Test Coins“.
4. **MT5-Demo-Konto**: MetaTrader 5 installieren → Datei → Konto eröffnen →
   Demo. Login, Passwort und Servername notieren.

## Installation (Windows)

```powershell
git clone https://github.com/berinademi57-creator/claude.git
cd claude\trading
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
notepad .env        # Keys eintragen
```

## Benutzen

```powershell
# 1. Verbindung testen, ohne KI und ohne Order (Trockenlauf)
.\.venv\Scripts\python.exe agent_trader.py --venue bybit --symbol BTCUSDT --signal Buy
.\.venv\Scripts\python.exe agent_trader.py --venue mt5   --symbol XAUUSD  --signal Buy

# 2. KI analysieren lassen, nur anzeigen
.\.venv\Scripts\python.exe agent_trader.py --venue bybit --symbol BTCUSDT

# 3. KI analysieren lassen UND auf Testnet/Demo handeln
.\.venv\Scripts\python.exe agent_trader.py --venue bybit --symbol ETHUSDT --execute
.\.venv\Scripts\python.exe agent_trader.py --venue mt5   --symbol XAUUSD  --execute
```

Für MT5 muss das Terminal geöffnet sein und „Algo Trading“ aktiv sein.
Heißt Gold bei deinem Broker anders (z. B. `GOLD` oder `XAUUSD.m`), nimm diesen
Namen und gib den Daten-Ticker dazu an: `--symbol GOLD --yahoo GC=F`.

Täglich automatisch: Windows-Aufgabenplanung → Aufgabe erstellen → Programm
`...\trading\.venv\Scripts\python.exe`, Argumente
`agent_trader.py --venue bybit --symbol BTCUSDT --execute`, Starten in
`...\trading`.

## Kleines Budget – worauf achten

- **Bybit Spot**: ab ca. 5–10 USDT pro Order möglich, kein Hebel, kein Shorten.
  Für kleines Budget der einfachste Weg.
- **MT5 Gold**: Die kleinste Größe (0.01 Lot = 1 Unze) bewegt sich schnell um
  10–30 $ bis zum Stop-Loss. Der Bot lehnt den Trade ab, wenn das mehr als
  `MAX_RISK_PER_TRADE` wäre – bei 100 € Konto ist Gold meist zu groß.
- Die Grenzen stehen in `.env` (`MAX_USDT_PER_TRADE`, `MAX_USDT_PER_SYMBOL`,
  `STOP_LOSS_PCT`, `MAX_RISK_PER_TRADE`).

Zusätzlich gibt es den Indikator `../mt5/GoldSignals.mq5` (EMA + RSI), der nur
Signale im Chart zeigt. Beides kann man vergleichen.

Keine Anlageberatung.
