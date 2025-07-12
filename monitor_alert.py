import ccxt
import pandas as pd
import ta
from telegram import Bot
import asyncio
import datetime

# ====== Configuration ======
TELEGRAM_TOKEN = '7443495110:AAG1u7E8ZQnmgGuzHpvpbm7wLbjw1B7e-qg'
CHAT_ID = '6641217424'

SYMBOLS = ['BTC/USDT', 'NEIRO/USDT']
EXCHANGE_ID = 'binance'
TIMEFRAME = '1m'
CHECK_INTERVAL = 60  # seconds
PRICE_CHANGE_THRESHOLD = 0.0001
VOLUME_SPIKE_MULTIPLIER = 2
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ====== Setup ======
exchange = getattr(ccxt, EXCHANGE_ID)()
bot = Bot(token=TELEGRAM_TOKEN)

async def send_alert(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"✅ 已发送通知: {message}")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

def fetch_ohlcv(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=RSI_PERIOD+1)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"❌ 获取K线失败: {symbol} | {e}")
        return None

async def check_anomaly(symbol):
    df = fetch_ohlcv(symbol)
    if df is None:
        return

    close = df['close'].iloc[-1]
    prev_close = df['close'].iloc[-2]
    price_change = (close - prev_close) / prev_close
    avg_volume = df['volume'].iloc[:-1].mean()
    recent_volume = df['volume'].iloc[-1]
    rsi = ta.momentum.RSIIndicator(df['close'], window=RSI_PERIOD).rsi().iloc[-1]

    messages = []

    if abs(price_change) >= PRICE_CHANGE_THRESHOLD:
        direction = '上涨' if price_change > 0 else '下跌'
        messages.append(f"{symbol} 价格{direction}{price_change*100:.2f}% => {close:.2f}")

    if recent_volume >= VOLUME_SPIKE_MULTIPLIER * avg_volume:
        messages.append(f"{symbol} 成交量激增: 最新 {recent_volume:.0f}, 平均 {avg_volume:.0f}")

    if rsi >= RSI_OVERBOUGHT:
        messages.append(f"{symbol} RSI 超买: {rsi:.1f}")
    elif rsi <= RSI_OVERSOLD:
        messages.append(f"{symbol} RSI 超卖: {rsi:.1f}")

    if messages:
        alert = f"📈 异动预警 ({datetime.datetime.now().strftime('%H:%M:%S')}):\n" + "\n".join(messages)
        await send_alert(alert)

async def main():
    print("✅ 启动市场异动监控系统...")
    while True:
        for symbol in SYMBOLS:
            await check_anomaly(symbol)
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
