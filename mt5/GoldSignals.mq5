//+------------------------------------------------------------------+
//| GoldSignals.mq5 - REIN/RAUS-Signale fuer Gold (XAUUSD) in MT5     |
//| Regel: EMA-Crossover + RSI-Filter, Stop/Ziel per ATR.             |
//| Signale nur auf GESCHLOSSENEN Kerzen (kein Repainting).           |
//| Nur Signale, KEINE automatischen Orders. Kein Anlagerat.          |
//+------------------------------------------------------------------+
#property copyright "Beispiel"
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "REIN Long"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrLime
#property indicator_width1  2

#property indicator_label2  "REIN Short"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrOrangeRed
#property indicator_width2  2

input int    FastPeriod   = 20;    // schnelle EMA
input int    SlowPeriod   = 50;    // langsame EMA
input int    RsiPeriod    = 14;    // RSI
input int    AtrPeriod    = 14;    // ATR
input double SlAtrMult    = 1.5;   // Stop-Loss = ATR * x
input double TpAtrMult    = 3.0;   // Take-Profit = ATR * x
input bool   UseAlert     = true;  // Popup-Alarm
input bool   UsePush      = false; // Push aufs Handy (MT5-App, MetaQuotes-ID in Optionen noetig)

double BuyBuf[], SellBuf[];
double fastV[], slowV[], rsiV[], atrV[];
int hF, hS, hR, hA;
datetime lastAlertBar = 0;

int OnInit()
  {
   SetIndexBuffer(0, BuyBuf,  INDICATOR_DATA);
   SetIndexBuffer(1, SellBuf, INDICATOR_DATA);
   PlotIndexSetInteger(0, PLOT_ARROW, 233);
   PlotIndexSetInteger(1, PLOT_ARROW, 234);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);

   hF = iMA(_Symbol, _Period, FastPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hS = iMA(_Symbol, _Period, SlowPeriod, 0, MODE_EMA, PRICE_CLOSE);
   hR = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);
   hA = iATR(_Symbol, _Period, AtrPeriod);
   if(hF == INVALID_HANDLE || hS == INVALID_HANDLE || hR == INVALID_HANDLE || hA == INVALID_HANDLE)
      return INIT_FAILED;
   return INIT_SUCCEEDED;
  }

int OnCalculate(const int rates_total, const int prev_calculated,
                const datetime &time[], const double &open[], const double &high[],
                const double &low[], const double &close[], const long &tick_volume[],
                const long &volume[], const int &spread[])
  {
   int minBars = MathMax(SlowPeriod, MathMax(RsiPeriod, AtrPeriod)) + 5;
   if(rates_total < minBars)
      return 0;

   ArraySetAsSeries(fastV, false); ArraySetAsSeries(slowV, false);
   ArraySetAsSeries(rsiV,  false); ArraySetAsSeries(atrV,  false);
   if(CopyBuffer(hF, 0, 0, rates_total, fastV) != rates_total) return prev_calculated;
   if(CopyBuffer(hS, 0, 0, rates_total, slowV) != rates_total) return prev_calculated;
   if(CopyBuffer(hR, 0, 0, rates_total, rsiV)  != rates_total) return prev_calculated;
   if(CopyBuffer(hA, 0, 0, rates_total, atrV)  != rates_total) return prev_calculated;

   int start = (prev_calculated > minBars) ? prev_calculated - 2 : minBars;
   int lastClosed = rates_total - 2;   // rates_total-1 ist die laufende Kerze

   for(int i = start; i < rates_total; i++)
     {
      BuyBuf[i] = EMPTY_VALUE;
      SellBuf[i] = EMPTY_VALUE;
      if(i > lastClosed) continue;

      bool crossUp   = fastV[i] > slowV[i] && fastV[i-1] <= slowV[i-1];
      bool crossDown = fastV[i] < slowV[i] && fastV[i-1] >= slowV[i-1];

      if(crossUp && rsiV[i] > 50.0)
        {
         BuyBuf[i] = low[i] - atrV[i] * 0.5;
         if(i == lastClosed) Notify(time[i], true, close[i], atrV[i]);
        }
      else if(crossDown && rsiV[i] < 50.0)
        {
         SellBuf[i] = high[i] + atrV[i] * 0.5;
         if(i == lastClosed) Notify(time[i], false, close[i], atrV[i]);
        }
     }
   return rates_total;
  }

void Notify(datetime barTime, bool isLong, double price, double atr)
  {
   if(barTime == lastAlertBar) return;
   lastAlertBar = barTime;
   double sl = isLong ? price - atr * SlAtrMult : price + atr * SlAtrMult;
   double tp = isLong ? price + atr * TpAtrMult : price - atr * TpAtrMult;
   string msg = StringFormat("%s %s: %s @ %.2f | SL %.2f | TP %.2f | RAUS bei Gegensignal",
                             _Symbol, EnumToString(_Period),
                             isLong ? "REIN LONG (und Short raus)" : "REIN SHORT (und Long raus)",
                             price, sl, tp);
   if(UseAlert) Alert(msg);
   if(UsePush)  SendNotification(msg);
   Print(msg);
  }

void OnDeinit(const int reason)
  {
   IndicatorRelease(hF); IndicatorRelease(hS);
   IndicatorRelease(hR); IndicatorRelease(hA);
  }
