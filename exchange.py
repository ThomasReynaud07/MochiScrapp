import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Optional

import config
from logger import log


class Exchange:
    def __init__(self):
        self.client = Client(config.API_KEY, config.API_SECRET)
        self._verify_connection()
        self._symbol_info = self._load_symbol_info()

    def _verify_connection(self):
        try:
            self.client.ping()
            server_time = self.client.get_server_time()
            log.info(f"Connecté à Binance. Heure serveur: {server_time['serverTime']}")
        except BinanceAPIException as e:
            raise ConnectionError(f"Impossible de se connecter à Binance: {e}")

    def _load_symbol_info(self) -> dict:
        info = self.client.get_symbol_info(config.SYMBOL)
        if not info:
            raise ValueError(f"Symbole {config.SYMBOL} introuvable sur Binance.")
        return info

    def get_candles(self, limit: int = 100) -> pd.DataFrame:
        klines = self.client.get_klines(
            symbol=config.SYMBOL,
            interval=config.INTERVAL,
            limit=limit,
        )
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df

    def get_usdt_balance(self) -> float:
        balance = self.client.get_asset_balance(asset="USDT")
        return float(balance["free"]) if balance else 0.0

    def get_base_balance(self) -> float:
        base_asset = self._symbol_info["baseAsset"]
        balance = self.client.get_asset_balance(asset=base_asset)
        return float(balance["free"]) if balance else 0.0

    def get_current_price(self) -> float:
        ticker = self.client.get_symbol_ticker(symbol=config.SYMBOL)
        return float(ticker["price"])

    def _round_quantity(self, qty: float) -> float:
        """Arrondit la quantité selon les règles LOT_SIZE de Binance."""
        for f in self._symbol_info["filters"]:
            if f["filterType"] == "LOT_SIZE":
                step = float(f["stepSize"])
                precision = len(str(step).rstrip("0").split(".")[-1]) if "." in str(step) else 0
                qty = round(qty - (qty % step), precision)
                break
        return qty

    def buy_market(self, usdt_amount: float) -> Optional[dict]:
        price = self.get_current_price()
        qty = self._round_quantity(usdt_amount / price)
        if qty <= 0:
            log.warning(f"Quantité calculée trop faible: {qty}")
            return None
        try:
            order = self.client.order_market_buy(symbol=config.SYMBOL, quantity=qty)
            log.info(f"ACHAT exécuté: {qty} {self._symbol_info['baseAsset']} @ ~{price:.4f} USDT")
            return order
        except BinanceAPIException as e:
            log.error(f"Erreur lors de l'achat: {e}")
            return None

    def sell_market(self, base_amount: float) -> Optional[dict]:
        qty = self._round_quantity(base_amount)
        if qty <= 0:
            log.warning(f"Quantité à vendre trop faible: {qty}")
            return None
        try:
            order = self.client.order_market_sell(symbol=config.SYMBOL, quantity=qty)
            log.info(f"VENTE exécutée: {qty} {self._symbol_info['baseAsset']}")
            return order
        except BinanceAPIException as e:
            log.error(f"Erreur lors de la vente: {e}")
            return None
