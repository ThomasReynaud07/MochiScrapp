"""
Système de notifications multi-canal (Telegram, logs, email)
"""

import asyncio
from typing import Callable, Optional
from logger import log


class NotificationManager:
    """Gère les notifications à travers plusieurs canaux"""

    def __init__(self):
        self.telegram = None
        self.callbacks = []
        self.enabled_channels = {
            "telegram": True,
            "log": True,
            "console": True,
        }

    def set_telegram_notifier(self, telegram_notifier):
        """Définir le notificateur Telegram"""
        self.telegram = telegram_notifier

    def add_callback(self, callback: Callable):
        """Ajouter un callback personnalisé pour les notifications"""
        self.callbacks.append(callback)

    def enable_channel(self, channel: str, enabled: bool = True):
        """Activer/désactiver un canal de notification"""
        if channel in self.enabled_channels:
            self.enabled_channels[channel] = enabled

    async def send_buy_signal(self, symbol: str, price: float, amount: float):
        """Envoyer une notification de signal d'achat"""
        message = f"🟢 BUY {symbol} @ {price:.4f} | Montant: {amount:.2f} USDT"

        if self.enabled_channels["log"]:
            log.info(message)

        if self.enabled_channels["telegram"] and self.telegram:
            try:
                await self.telegram.send_buy_signal(price, amount)
            except Exception as e:
                log.error(f"Erreur notification Telegram: {e}")

        # Appeler les callbacks
        for callback in self.callbacks:
            try:
                callback("buy_signal", {"symbol": symbol, "price": price, "amount": amount})
            except Exception as e:
                log.error(f"Erreur callback notification: {e}")

    async def send_sell_signal(self, symbol: str, price: float, reason: str, pnl: float = 0):
        """Envoyer une notification de signal de vente"""
        pnl_str = f" | P&L: {pnl:+.4f}" if pnl else ""
        message = f"🔴 SELL {symbol} @ {price:.4f} | Raison: {reason}{pnl_str}"

        if self.enabled_channels["log"]:
            log.info(message)

        if self.enabled_channels["telegram"] and self.telegram:
            try:
                await self.telegram.send_sell_signal(price, reason)
            except Exception as e:
                log.error(f"Erreur notification Telegram: {e}")

        for callback in self.callbacks:
            try:
                callback("sell_signal", {
                    "symbol": symbol,
                    "price": price,
                    "reason": reason,
                    "pnl": pnl,
                })
            except Exception as e:
                log.error(f"Erreur callback notification: {e}")

    async def send_position_update(self, symbol: str, price: float, pnl_pct: float):
        """Envoyer une mise à jour de position"""
        emoji = "📈" if pnl_pct >= 0 else "📉"
        message = f"{emoji} Position {symbol} @ {price:.4f} | P&L: {pnl_pct:+.2f}%"

        if self.enabled_channels["log"]:
            log.debug(message)

        if self.enabled_channels["telegram"] and self.telegram:
            try:
                # Envoyer moins souvent (ex: toutes les 5 updates)
                await self.telegram.send_position_update(price, pnl_pct)
            except Exception as e:
                log.error(f"Erreur notification Telegram: {e}")

    async def send_error(self, error_message: str, error_type: str = "unknown"):
        """Envoyer une notification d'erreur"""
        message = f"❌ [{error_type}] {error_message}"

        if self.enabled_channels["log"]:
            log.error(message)

        if self.enabled_channels["telegram"] and self.telegram:
            try:
                await self.telegram.send_error(error_message)
            except Exception as e:
                log.error(f"Erreur notification Telegram: {e}")

        for callback in self.callbacks:
            try:
                callback("error", {"message": error_message, "type": error_type})
            except Exception as e:
                log.error(f"Erreur callback notification: {e}")

    async def send_warning(self, warning_message: str):
        """Envoyer une notification d'avertissement"""
        message = f"⚠️ {warning_message}"

        if self.enabled_channels["log"]:
            log.warning(message)

        if self.enabled_channels["telegram"] and self.telegram:
            try:
                await self.telegram.send_notification(message)
            except Exception as e:
                log.error(f"Erreur notification Telegram: {e}")

    async def send_info(self, info_message: str):
        """Envoyer une notification d'info"""
        message = f"ℹ️ {info_message}"

        if self.enabled_channels["log"]:
            log.info(message)


# Instance globale
notification_manager = NotificationManager()
