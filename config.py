import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# BINANCE API (REQUIS)
# ========================================
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# ========================================
# PARAMÈTRES DE TRADING
# ========================================
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "15m")
TRADE_AMOUNT_USDT = float(os.getenv("TRADE_AMOUNT_USDT", "20"))

# ========================================
# GESTION DU RISQUE
# ========================================
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "2.0")) / 100
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "4.0")) / 100

# ========================================
# STRATÉGIE
# ========================================
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "35"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "65"))

EMA_FAST = int(os.getenv("EMA_FAST", "9"))
EMA_SLOW = int(os.getenv("EMA_SLOW", "21"))

# ========================================
# TELEGRAM (OPTIONNEL)
# ========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# ========================================
# API REST (OPTIONNEL)
# ========================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))

# ========================================
# LOGGING
# ========================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "trading_bot.log")

# ========================================
# VALIDATION
# ========================================
if not API_KEY or not API_SECRET:
    raise EnvironmentError(
        "❌ BINANCE_API_KEY et BINANCE_API_SECRET manquants.\n"
        "   Copie .env.example en .env et remplis tes clés API Binance.\n"
        "   Tutoriel: https://www.binance.com/en/support/faq/how-to-create-api"
    )
