# main.py
import time
from datetime import datetime
import logging
import pandas as pd
from ta.trend import SMAIndicator
from binance_utils import BinanceUtils
from config import SYMBOLS, TIMEFRAMES, DRY_RUN

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraBot:
    def __init__(self):
        self.binance = BinanceUtils()
        logger.info(f"Bot inicializado em modo {'DRY RUN' if DRY_RUN else 'REAL'}")

    def analyze_timeframes(self, symbol):
        """Analisa múltiplos timeframes para o símbolo"""
        aligned_timeframes = 0
        for tf in TIMEFRAMES:
            try:
                klines = self.binance.client.get_historical_klines(symbol, tf, "1 day ago UTC")
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                                  'close_time', 'quote_asset_volume', 'trades', 
                                                  'taker_buy_base', 'taker_buy_quote', 'ignored'])
                df['close'] = df['close'].astype(float)
                sma_fast = SMAIndicator(df['close'], window=10).sma_indicator()
                sma_slow = SMAIndicator(df['close'], window=50).sma_indicator()
                if sma_fast.iloc[-1] > sma_slow.iloc[-1]:  # Cruzamento de médias
                    aligned_timeframes += 1
            except Exception as e:
                logger.error(f"Erro ao analisar timeframe {tf} para {symbol}: {e}")
        return aligned_timeframes

    def get_current_price(self, symbol):
        """Obtém o preço atual do símbolo"""
        try:
            ticker = self.binance.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Erro ao obter preço atual para {symbol}: {e}")
            return None

    def generate_signal(self, symbol):
        """Gera um sinal de trading com base nos dados"""
        try:
            order_book = self.binance.get_order_book(symbol)
            delta_volume = self.binance.calculate_delta_volume(symbol)
            oi_data = self.binance.get_open_interest(symbol)
            funding_data = self.binance.get_funding_rate(symbol)
            current_price = self.get_current_price(symbol)

            if not all([order_book, delta_volume is not None, oi_data, funding_data, current_price]):
                logger.warning(f"Dados insuficientes para gerar sinal para {symbol}")
                return None

            aligned_timeframes = self.analyze_timeframes(symbol)
            score = 40 if aligned_timeframes >= 2 else 10  # Simulação de score

            signal = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pair": symbol,
                "timeframe": "15m",
                "direction": "N/A",
                "current_price": current_price,
                "score": score,
                "aligned_timeframes": aligned_timeframes
            }

            self.log_signal(signal)
            return signal
            
        except Exception as e:
            logger.error(f"Erro crítico ao gerar sinal para {symbol}: {e}")
            return None

    def log_signal(self, signal):
        """Registra o sinal gerado no log"""
        signal_text = (
            f"┌──────────────────────────────────────────────────┐\n"
            f"│ [ULTRABOT] Sinal Gerado - {signal['timestamp']}    │\n"
            f"│ Par: {signal['pair']}                                   │\n"
            f"│ Timeframe: {signal['timeframe']}                                    │\n"
            f"│ Direção: {signal['direction']}                                     │\n"
            f"│ Preço Atual: {signal['current_price']}                              │\n"
            f"│ Score Total: {signal['score']} (Baixo)                       │\n"
            f"│ Timeframes Analisados: {', '.join(TIMEFRAMES)}                │\n"
            f"├─ Resultado ────────────────────────────────────┤\n"
        )

        if signal['aligned_timeframes'] < 2 or signal['score'] < 50:
            signal_text += (
                f"│ ❌ Sinal Recusado - Menos de 2 TFs alinhados ou scores < 50│\n"
                f"│ Ação: Não Executado                  │\n"
            )
        else:
            signal_text += (
                f"│ ✅ Sinal Aceito - Executando ordem...          │\n"
                f"│ Ação: Executado                      │\n"
            )

        signal_text += "└──────────────────────────────────────────────────┘"
        logger.info(signal_text)

def main():
    bot = UltraBot()
    while True:
        try:
            for symbol in SYMBOLS:
                bot.generate_signal(symbol)
            time.sleep(60)  # Executa a cada 1 minuto para todos os pares
        except KeyboardInterrupt:
            logger.info("Bot encerrado pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(60)  # Espera antes de tentar novamente

if __name__ == "__main__":
    main()