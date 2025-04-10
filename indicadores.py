import numpy as np
import pandas as pd

def calcular_rsi(candles, periodo=14):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None

def calcular_adx(candles, periodo=14):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df[['high', 'low', 'close']] = df[['high', 'low', 'close']].apply(pd.to_numeric, errors='coerce')
    df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift()), abs(df['low'] - df['close'].shift())))
    df['dm_plus'] = np.where((df['high'] - df['high'].shift()) > (df['low'].shift() - df['low']), np.maximum(df['high'] - df['high'].shift(), 0), 0)
    df['dm_minus'] = np.where((df['low'].shift() - df['low']) > (df['high'] - df['high'].shift()), np.maximum(df['low'].shift() - df['low'], 0), 0)
    tr_smooth = df['tr'].rolling(window=periodo).mean()
    dm_plus_smooth = df['dm_plus'].rolling(window=periodo).mean()
    dm_minus_smooth = df['dm_minus'].rolling(window=periodo).mean()
    di_plus = 100 * dm_plus_smooth / tr_smooth
    di_minus = 100 * dm_minus_smooth / tr_smooth
    dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
    adx = dx.rolling(window=periodo).mean()
    return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else None

def calcular_ema(candles, periodo):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    ema = df['close'].ewm(span=periodo, adjust=False).mean()
    return ema.iloc[-1] if not pd.isna(ema.iloc[-1]) else None

def calcular_macd(candles, curto=12, longo=26, sinal=9):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    ema_curto = df['close'].ewm(span=curto, adjust=False).mean()
    ema_longo = df['close'].ewm(span=longo, adjust=False).mean()
    macd = ema_curto - ema_longo
    sinal_line = macd.ewm(span=sinal, adjust=False).mean()
    return macd.iloc[-1], sinal_line.iloc[-1] if not pd.isna(macd.iloc[-1]) else (None, None)

def calcular_volume(candles):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    return float(df['volume'].iloc[-1]) if not pd.isna(df['volume'].iloc[-1]) else None

def calcular_bollinger_bands(candles, periodo=20, desvios=2):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    sma = df['close'].rolling(window=periodo).mean()
    std = df['close'].rolling(window=periodo).std()
    superior = sma + (std * desvios)
    inferior = sma - (std * desvios)
    return (superior.iloc[-1], sma.iloc[-1], inferior.iloc[-1]) if not pd.isna(sma.iloc[-1]) else (None, None, None)

def calcular_estocastico(candles, periodo=14):
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df[['high', 'low', 'close']] = df[['high', 'low', 'close']].apply(pd.to_numeric, errors='coerce')
    low_min = df['low'].rolling(window=periodo).min()
    high_max = df['high'].rolling(window=periodo).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min)
    return k.iloc[-1] if not pd.isna(k.iloc[-1]) else None

def calcular_vwap(candles):
    try:
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df[['high', 'low', 'close', 'volume']] = df[['high', 'low', 'close', 'volume']].apply(pd.to_numeric, errors='coerce')
        df['price_typical'] = (df['high'] + df['low'] + df['close']) / 3
        df['price_volume'] = df['price_typical'] * df['volume']
        volume_sum = df['volume'].sum()
        if volume_sum == 0 or pd.isna(volume_sum):
            return None
        vwap = df['price_volume'].sum() / volume_sum
        return vwap if not pd.isna(vwap) else None
    except Exception as e:
        print(f"[INDICADORES] Erro ao calcular VWAP: {e}")
        return None

def calcular_fibonacci(candles, periodo=20):
    df = pd.DataFrame(candles[-periodo:], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df[['high', 'low']] = df[['high', 'low']].apply(pd.to_numeric, errors='coerce')
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low
    niveis = {
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff
    }
    return niveis if not pd.isna(high) and not pd.isna(low) else {}