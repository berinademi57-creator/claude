"""TradingAgents -> Bybit TESTNET / MetaTrader 5 DEMO.

Ablauf:
  1. TradingAgents (Multi-Agent-KI) analysiert ein Symbol und liefert ein Rating:
     Buy / Overweight / Hold / Underweight / Sell (oder REVIEW, wenn unklar).
  2. Das Rating wird in eine Aktion übersetzt (KAUFEN / VERKAUFEN / NICHTS).
  3. Ohne --execute wird nur angezeigt, was passieren würde (Trockenlauf).
     Mit --execute wird die Order platziert – aber ausschließlich auf
     Bybit TESTNET bzw. einem MT5 DEMO-Konto. Echtgeld ist absichtlich gesperrt.

Beispiele:
  python agent_trader.py --venue bybit --symbol BTCUSDT
  python agent_trader.py --venue bybit --symbol ETHUSDT --execute
  python agent_trader.py --venue mt5   --symbol XAUUSD  --execute
  python agent_trader.py --venue mt5   --symbol EURUSD  --signal Buy --execute   # ohne KI, zum Testen

Keine Anlageberatung. Die KI liegt oft falsch.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import os
import sys
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_FILE = HERE / "logs" / "decisions.csv"

BULLISH = {"Buy", "Overweight"}
BEARISH = {"Sell", "Underweight"}

# MT5-Symbol -> Yahoo-Finance-Ticker, den TradingAgents für Daten nutzt
MT5_TO_YAHOO = {
    "XAUUSD": "GC=F",
    "XAGUSD": "SI=F",
    "US30": "^DJI",
    "NAS100": "^NDX",
    "US500": "^GSPC",
    "GER40": "^GDAXI",
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
}


# --------------------------------------------------------------------------- #
# Hilfsfunktionen
# --------------------------------------------------------------------------- #
def env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    return float(raw) if raw else default


def need_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        sys.exit(f"FEHLER: {name} fehlt in trading/.env")
    return value


def action_for(signal: str) -> str:
    if signal in BULLISH:
        return "BUY"
    if signal in BEARISH:
        return "SELL"
    return "NONE"


def log_decision(venue: str, symbol: str, ticker: str, signal: str, action: str, result: str) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    new = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["zeit_utc", "venue", "symbol", "yahoo_ticker", "signal", "aktion", "ergebnis"])
        w.writerow([dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
                    venue, symbol, ticker, signal, action, result])


def floor_to(value: Decimal, step: str) -> Decimal:
    q = Decimal(step)
    return (value / q).to_integral_value(rounding=ROUND_DOWN) * q


# --------------------------------------------------------------------------- #
# 1) Analyse mit TradingAgents
# --------------------------------------------------------------------------- #
def yahoo_ticker(venue: str, symbol: str) -> tuple[str, str]:
    """Liefert (yahoo_ticker, asset_type)."""
    s = symbol.upper()
    if venue == "bybit":
        base = s.removesuffix("USDT").removesuffix("USDC")
        return f"{base}-USD", "crypto"
    if s in MT5_TO_YAHOO:
        t = MT5_TO_YAHOO[s]
        return t, ("crypto" if t.endswith("-USD") else "stock")
    if len(s) == 6 and s.isalpha():  # Forex-Paar wie EURUSD
        return f"{s}=X", "stock"
    return s, "stock"


def analyse(ticker: str, asset_type: str) -> str:
    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    # Fundamentaldaten gibt es nur für Aktien – für Krypto/Gold/Forex weglassen
    if asset_type == "crypto":
        analysts = ("market", "social", "news")
    elif ticker.endswith(("=X", "=F")) or ticker.startswith("^"):
        analysts = ("market", "news")
    else:
        analysts = ("market", "social", "news", "fundamentals")

    config = DEFAULT_CONFIG.copy()  # übernimmt TRADINGAGENTS_* aus der .env
    ta = TradingAgentsGraph(selected_analysts=analysts, config=config)
    today = dt.date.today().isoformat()
    print(f"[KI] Analysiere {ticker} ({asset_type}, Analysten: {', '.join(analysts)}) für {today} ...")
    state, signal = ta.propagate(ticker, today, asset_type=asset_type)
    ta.save_reports(state, ticker)
    print(f"[KI] Ergebnis: {signal}   (Bericht gespeichert unter ~/.tradingagents)")
    return signal


# --------------------------------------------------------------------------- #
# 2a) Bybit – fest auf TESTNET
# --------------------------------------------------------------------------- #
def bybit_trade(symbol: str, action: str, execute: bool) -> str:
    from pybit.unified_trading import HTTP

    # testnet=True ist absichtlich fest verdrahtet (kein Echtgeld).
    s = HTTP(testnet=True,
             api_key=need_env("BYBIT_TESTNET_API_KEY"),
             api_secret=need_env("BYBIT_TESTNET_API_SECRET"))

    max_trade = env_float("MAX_USDT_PER_TRADE", 10)
    max_symbol = env_float("MAX_USDT_PER_SYMBOL", 30)
    sl_pct = env_float("STOP_LOSS_PCT", 3)

    info = s.get_instruments_info(category="spot", symbol=symbol)["result"]["list"]
    if not info:
        return f"Symbol {symbol} gibt es auf Bybit Spot nicht"
    info = info[0]
    base_coin = info["baseCoin"]
    base_step = info["lotSizeFilter"]["basePrecision"]
    tick = info["priceFilter"]["tickSize"]
    min_amt = float(info["lotSizeFilter"].get("minOrderAmt", 1))

    price = Decimal(s.get_tickers(category="spot", symbol=symbol)["result"]["list"][0]["lastPrice"])

    def balance(coin: str) -> Decimal:
        rows = s.get_wallet_balance(accountType="UNIFIED", coin=coin)["result"]["list"]
        for c in rows[0]["coin"] if rows else []:
            if c["coin"] == coin:
                return Decimal(c.get("walletBalance") or "0")
        return Decimal("0")

    usdt = balance("USDT")
    held = balance(base_coin)
    held_value = held * price
    print(f"[Bybit TESTNET] Preis {symbol}: {price} | USDT frei: {usdt:.2f} | "
          f"{base_coin}: {held} (~{held_value:.2f} USDT)")

    if action == "BUY":
        amount = Decimal(str(min(max_trade, max_symbol - float(held_value))))
        if amount < Decimal(str(min_amt)):
            return f"kein Kauf: Limit pro Coin ({max_symbol} USDT) erreicht"
        if usdt < amount:
            return f"kein Kauf: zu wenig USDT ({usdt:.2f} < {amount:.2f})"
        qty = floor_to(amount / price, base_step)
        stop = floor_to(price * (1 - Decimal(str(sl_pct)) / 100), tick)
        plan = f"KAUF {qty} {base_coin} für ~{amount:.2f} USDT, Stop-Loss bei {stop}"
        if not execute:
            return "Trockenlauf: " + plan
        r = s.place_order(category="spot", symbol=symbol, side="Buy", orderType="Market",
                          qty=str(amount), marketUnit="quoteCoin")
        msg = f"{plan} -> Order {r['result'].get('orderId')}"
        try:
            sl = s.place_order(category="spot", symbol=symbol, side="Sell", orderType="Market",
                               qty=str(qty), triggerPrice=str(stop), orderFilter="tpslOrder")
            msg += f", Stop-Loss {sl['result'].get('orderId')}"
        except Exception as e:  # Kauf ist durch, nur der Stop fehlt
            msg += f", ACHTUNG Stop-Loss nicht gesetzt: {e}"
        return msg

    if action == "SELL":
        qty = floor_to(held, base_step)
        if qty * price < Decimal(str(min_amt)):
            return f"nichts zu verkaufen (kein {base_coin} im Testnet-Konto, Spot kann nicht shorten)"
        plan = f"VERKAUF {qty} {base_coin} (~{qty * price:.2f} USDT)"
        if not execute:
            return "Trockenlauf: " + plan
        try:  # offene Stop-Loss-Orders vorher löschen
            s.cancel_all_orders(category="spot", symbol=symbol, orderFilter="tpslOrder")
        except Exception:
            pass
        r = s.place_order(category="spot", symbol=symbol, side="Sell", orderType="Market", qty=str(qty))
        return f"{plan} -> Order {r['result'].get('orderId')}"

    return "keine Aktion (Hold/Review)"


# --------------------------------------------------------------------------- #
# 2b) MetaTrader 5 – nur DEMO-Konten
# --------------------------------------------------------------------------- #
def mt5_trade(symbol: str, action: str, execute: bool) -> str:
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return "MetaTrader5-Paket fehlt (gibt es nur unter Windows: pip install MetaTrader5)"

    kwargs = dict(login=int(need_env("MT5_DEMO_LOGIN")),
                  password=need_env("MT5_DEMO_PASSWORD"),
                  server=need_env("MT5_DEMO_SERVER"))
    if os.getenv("MT5_TERMINAL_PATH"):
        kwargs["path"] = os.environ["MT5_TERMINAL_PATH"]
    if not mt5.initialize(**kwargs):
        return f"MT5-Verbindung fehlgeschlagen: {mt5.last_error()}"
    try:
        acc = mt5.account_info()
        if acc is None or acc.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            return "ABGEBROCHEN: Das ist kein Demo-Konto. Dieser Bot handelt nur auf Demo."
        print(f"[MT5 DEMO] Konto {acc.login} | Saldo {acc.balance:.2f} {acc.currency}")

        if not mt5.symbol_select(symbol, True):
            return f"Symbol {symbol} gibt es bei diesem Broker nicht (evtl. heißt es z. B. {symbol}.m oder GOLD)"
        info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)

        open_pos = mt5.positions_get(symbol=symbol) or ()
        want = {"BUY": mt5.POSITION_TYPE_BUY, "SELL": mt5.POSITION_TYPE_SELL}.get(action)
        if want is None:
            return "keine Aktion (Hold/Review)"

        # Gegenposition schließen, gleiche Richtung nicht verdoppeln
        msgs = []
        for p in open_pos:
            if p.type == want:
                return f"bereits {action}-Position offen (Ticket {p.ticket}) – nichts Neues"
            close_type = mt5.ORDER_TYPE_SELL if p.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
            if execute:
                r = mt5.order_send(_mt5_request(mt5, info, close_type, p.volume,
                                                tick.bid if p.type == mt5.POSITION_TYPE_BUY else tick.ask,
                                                position=p.ticket))
                msgs.append(f"Gegenposition {p.ticket} geschlossen ({r.retcode})")
            else:
                msgs.append(f"würde Gegenposition {p.ticket} schließen")

        # Stop-Loss/Take-Profit aus ATR(14) auf H1
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 15)
        if rates is None or len(rates) < 2:
            return "; ".join(msgs + [f"keine Kursdaten für {symbol}: {mt5.last_error()}"])
        trs = [max(rates[i]["high"] - rates[i]["low"],
                   abs(rates[i]["high"] - rates[i - 1]["close"]),
                   abs(rates[i]["low"] - rates[i - 1]["close"])) for i in range(1, len(rates))]
        atr = sum(trs) / len(trs)
        sl_d, tp_d = atr * env_float("SL_ATR_MULT", 1.5), atr * env_float("TP_ATR_MULT", 3.0)

        volume = info.volume_min  # kleinste Lotgröße (meist 0.01)
        if action == "BUY":
            otype, price = mt5.ORDER_TYPE_BUY, tick.ask
            sl, tp = price - sl_d, price + tp_d
        else:
            otype, price = mt5.ORDER_TYPE_SELL, tick.bid
            sl, tp = price + sl_d, price - tp_d
        sl, tp = round(sl, info.digits), round(tp, info.digits)

        risk = abs(mt5.order_calc_profit(otype, symbol, volume, price, sl) or math.inf)
        max_risk = env_float("MAX_RISK_PER_TRADE", 5)
        plan = (f"{action} {volume} Lot {symbol} @ {price}, SL {sl}, TP {tp}, "
                f"Risiko bis SL ≈ {risk:.2f} {acc.currency}")
        if risk > max_risk:
            return "; ".join(msgs + [f"ABGELEHNT: {plan} > Limit {max_risk} – selbst die kleinste "
                                     f"Lotgröße ist für dein Budget zu riskant"])
        if not execute:
            return "; ".join(msgs + ["Trockenlauf: " + plan])
        r = mt5.order_send(_mt5_request(mt5, info, otype, volume, price, sl=sl, tp=tp))
        ok = r is not None and r.retcode == mt5.TRADE_RETCODE_DONE
        res = f"{plan} -> {'OK Ticket ' + str(r.order) if ok else 'FEHLER ' + str(r and r.comment)}"
        return "; ".join(msgs + [res])
    finally:
        mt5.shutdown()


def _mt5_request(mt5, info, otype, volume, price, sl=0.0, tp=0.0, position=None):
    fm = info.filling_mode
    filling = (mt5.ORDER_FILLING_FOK if fm & 1 else
               mt5.ORDER_FILLING_IOC if fm & 2 else mt5.ORDER_FILLING_RETURN)
    req = {
        "action": mt5.TRADE_ACTION_DEAL, "symbol": info.name, "volume": volume,
        "type": otype, "price": price, "sl": sl, "tp": tp, "deviation": 20,
        "magic": 260911, "comment": "TradingAgents", "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling,
    }
    if position is not None:
        req["position"] = position
        req.pop("sl"), req.pop("tp")
    return req


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description="TradingAgents -> Bybit Testnet / MT5 Demo")
    ap.add_argument("--venue", choices=["bybit", "mt5"], required=True)
    ap.add_argument("--symbol", required=True, help="z. B. BTCUSDT (Bybit) oder XAUUSD (MT5)")
    ap.add_argument("--yahoo", help="Yahoo-Ticker für die Analyse überschreiben (z. B. GC=F)")
    ap.add_argument("--signal", choices=["Buy", "Overweight", "Hold", "Underweight", "Sell"],
                    help="KI überspringen und dieses Signal nutzen (zum Testen der Verbindung)")
    ap.add_argument("--execute", action="store_true",
                    help="Order wirklich platzieren (Testnet/Demo). Ohne: nur Trockenlauf")
    args = ap.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv(HERE / ".env")
    except ImportError:
        pass

    symbol = args.symbol.upper()
    ticker, asset_type = yahoo_ticker(args.venue, symbol)
    if args.yahoo:
        ticker = args.yahoo

    signal = args.signal or analyse(ticker, asset_type)
    action = action_for(signal)
    print(f"[Plan] Signal {signal} -> Aktion {action}")

    if args.venue == "bybit":
        result = bybit_trade(symbol, action, args.execute)
    else:
        result = mt5_trade(symbol, action, args.execute)

    print(f"[Ergebnis] {result}")
    log_decision(args.venue, symbol, ticker, signal, action, result)


if __name__ == "__main__":
    main()
