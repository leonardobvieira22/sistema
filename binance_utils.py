# binance_utils.py
import logging
import requests
import json
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import REAL_API_KEY, REAL_API_SECRET, DRY_RUN_API_KEY, DRY_RUN_API_SECRET, DRY_RUN

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BinanceUtils:
    def __init__(self):
        # Seleciona as chaves com base no modo DRY_RUN
        api_key = DRY_RUN_API_KEY if DRY_RUN else REAL_API_KEY
        api_secret = DRY_RUN_API_SECRET if DRY_RUN else REAL_API_SECRET
        self.client = Client(api_key, api_secret, testnet=DRY_RUN)
        self.base_url = "https://fapi.binance.com" if not DRY_RUN else "https://testnet.binancefuture.com"

    def get_order_book(self, symbol):
        """Obtém o order book para o símbolo especificado."""
        try:
            order_book = self.client.get_order_book(symbol=symbol)
            logger.info(f"[ICEBERG] Order book obtido para {symbol}: {order_book['lastUpdateId']}")
            return order_book
        except AttributeError as e:
            logger.error(f"[ICEBERG] Erro ao verificar order book: {e}")
            return None
        except BinanceAPIException as e:
            logger.error(f"[ICEBERG] Erro na API ao obter order book: {e}")
            return None

    def calculate_delta_volume(self, symbol):
        """Calcula o delta de volume com base em trades recentes."""
        try:
            trades = self.client.get_recent_trades(symbol=symbol, limit=100)
            delta = 0
            for trade in trades:
                if 'isBuyerMaker' in trade:
                    qty = float(trade['qty'])
                    delta += qty if trade['isBuyerMaker'] else -qty
                else:
                    logger.warning(f"[DELTA] Chave 'isBuyerMaker' não encontrada em trade: {trade}")
            logger.info(f"[DELTA] Delta volume calculado para {symbol}: {delta}")
            return delta
        except BinanceAPIException as e:
            logger.error(f"[DELTA] Erro na API ao calcular delta volume: {e}")
            return None
        except Exception as e:
            logger.error(f"[DELTA] Erro inesperado ao calcular delta volume: {e}")
            return None

    def get_open_interest(self, symbol):
        """Obtém o open interest para o símbolo especificado."""
        url = f"{self.base_url}/fapi/v1/openInterest?symbol={symbol}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"[SENTIMENTO] Open Interest para {symbol}: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"[SENTIMENTO] Erro na requisição de OI: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"[SENTIMENTO] Resposta inválida da API: {response.text}")
            return None

    def get_funding_rate(self, symbol):
        """Obtém o funding rate para o símbolo especificado."""
        url = f"{self.base_url}/fapi/v1/fundingRate?symbol={symbol}&limit=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"[SENTIMENTO] Funding Rate para {symbol}: {data}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"[SENTIMENTO] Erro na requisição de Funding Rate: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"[SENTIMENTO] Resposta inválida da API: {response.text}")
            return None