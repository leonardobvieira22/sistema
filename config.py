# config.py

# Chaves da API para o ambiente real (produção)
REAL_API_KEY = "VGQ0dhdCcHjDhEjj0Xuue3ZtyIZHiG9NK8chA4ew0HMQMywydjrVrLTWeN8nnZ9e"
REAL_API_SECRET = "jHrPFutd2fQH2AECeABbG6mDvbJqhEYBt1kuYmiWfcBjJV22Fwtykqx8mDFle3dO"

# Chaves da API para o ambiente de dry run (testnet/simulação)
DRY_RUN_API_KEY = "g9mSN8ic44DqKKcyCSqKatm1H3H8RISsBbz64TixKU1vgqMLwAIkoGJWQ0F7zPs3"
DRY_RUN_API_SECRET = "g4UKf1z0vGLVCqTUuWg1qA5SLvvvIfTtZYgxlCaeVcDZmUgEUfK8z6agx8JUX1CY"

# Lista de pares a serem negociados
SYMBOLS = [
    "XRPUSDT",  # Par 1
    "DOGEUSDT", # Par 2
    "TRXUSDT"   # Par 3
]

# Timeframes analisados
TIMEFRAMES = ["15m", "1h", "2h", "4h"]

# Modo de execução: True para dry run (testnet), False para real
DRY_RUN = True