import asyncio, json, websockets, requests, os
from datetime import datetime

APP_ID = 1089
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# FULL LIST - ALL DERIV SYNTHETICS
SYMBOLS = {
    # Volatility - Normal (2 sec tick)
    "R_10": "Volatility 10 Index",
    "R_25": "Volatility 25 Index",
    "R_50": "Volatility 50 Index",
    "R_75": "Volatility 75 Index",
    "R_100": "Volatility 100 Index",
    "R_150": "Volatility 150 Index",
    "R_250": "Volatility 250 Index",

    # Volatility - 1s (1 sec tick) - includes new ones
    "1HZ10V": "Volatility 10 (1s) Index",
    "1HZ25V": "Volatility 25 (1s) Index",
    "1HZ50V": "Volatility 50 (1s) Index",
    "1HZ75V": "Volatility 75 (1s) Index",
    "1HZ100V": "Volatility 100 (1s) Index",
    "1HZ150V": "Volatility 150 (1s) Index",
    "1HZ250V": "Volatility 250 (1s) Index",
    "1HZ15V": "Volatility 15 (1s) Index",
    "1HZ30V": "Volatility 30 (1s) Index",
    "1HZ90V": "Volatility 90 (1s) Index",

    # Volatility - High Frequency (2 ticks per sec)
    "HF10": "Volatility 10 HF Index",
    "HF25": "Volatility 25 HF Index",
    "HF50": "Volatility 50 HF Index",
    "HF100": "Volatility 100 HF Index",

    # Boom - Full series
    "BOOM300": "Boom 300 Index",
    "BOOM500": "Boom 500 Index",
    "BOOM600": "Boom 600 Index",
    "BOOM900": "Boom 900 Index",
    "BOOM1000": "Boom 1000 Index",

    # Crash - Full series
    "CRASH300": "Crash 300 Index",
    "CRASH500": "Crash 500 Index",
    "CRASH600": "Crash 600 Index",
    "CRASH900": "Crash 900 Index",
    "CRASH1000": "Crash 1000 Index",

    # Jump - Full series
    "JD10": "Jump 10 Index",
    "JD25": "Jump 25 Index",
    "JD50": "Jump 50 Index",
    "JD75": "Jump 75 Index",
    "JD100": "Jump 100 Index",
    "JD150": "Jump 150 Index",

    # Step / Multi Step / Skew Step
    "STPHMC": "Step Index",
    "stpRNG": "Step Multi Index",

    # Range Break
    "RDBULL": "Range Break 100 Index",
    "RDBEAR": "Range Break 200 Index",

    # Drift Switch
    "DS10": "Drift Switch 10 Index",
    "DS20": "Drift Switch 20 Index",
    "DS30": "Drift Switch 30 Index",

    # DEX / Basket
    "DEXBULL": "DEX Bull 60 Index",
    "DEXBEAR": "DEX Bear 60 Index",
}

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

async def get_candles(sym):
    uri = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"ticks_history": sym, "granularity": 86400, "count": 500, "end": "latest", "style": "candles"}))
        d = json.loads(await ws.recv())
        return d.get('candles', [])

def analyze(candles):
    fresh=[]
    for i in range(1,len(candles)):
        if candles[i-1]['close']==candles[i]['open']: continue
        level=candles[i-1]['close']
        ok=True
        for j in range(i+1,len(candles)-1):
            if candles[j]['low']<=level<=candles[j]['high']:
                ok=False; break
        if ok: fresh.append({'level':level,'birth':i})
    return fresh

async def main():
    for sym,name in SYMBOLS.items():
        try:
            candles=await get_candles(sym)
            if not candles: continue
            fresh=analyze(candles)
            if not fresh: continue
            last=candles[-1]
            for f in fresh[:-1]:
                lvl=f['level']
                if not (last['low']<=lvl<=last['high']): continue
                if lvl>candles[-2]['close']:
                    if last['close']>lvl or last['close']<=last['open']: continue
                else:
                    if last['close']<lvl or last['close']>=last['open']: continue
                send_telegram(f"🔔 {name} - Fresh Gap\nLevel: {lvl}\nDate: {datetime.now().strftime('%Y-%m-%d')}")
        except: pass
        await asyncio.sleep(0.3)

asyncio.run(main())
