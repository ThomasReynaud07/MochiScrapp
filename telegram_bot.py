"""
Intégration Telegram pour le bot de trading MochiBot
Notifications et commandes de gestion du bot
"""

import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

import config
from logger import log


class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

        if not self.bot_token or not self.chat_id:
            log.warning(
                "TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID manquant. "
                "Telegram notifications désactivé."
            )
            self.enabled = False
        else:
            self.enabled = True
            self.app = None

    async def initialize(self):
        """Initialiser le bot Telegram"""
        if not self.enabled:
            return

        try:
            self.app = Application.builder().token(self.bot_token).build()

            # Ajoute les handlers
            self.app.add_handler(CommandHandler("start", self.start))
            self.app.add_handler(CommandHandler("status", self.status))
            self.app.add_handler(CommandHandler("position", self.position_info))
            self.app.add_handler(CommandHandler("stop", self.stop_bot))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CallbackQueryHandler(self.button_callback))

            await self.app.initialize()
            log.info("Bot Telegram initialisé avec succès")
        except Exception as e:
            log.error(f"Erreur initialisation Telegram: {e}")
            self.enabled = False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /start"""
        message = (
            "🤖 *MochiBot - Trading Bot Binance*\n\n"
            "Commandes disponibles:\n"
            "/status - État du bot\n"
            "/position - Info position actuelle\n"
            "/stop - Arrêter le bot\n"
            "/help - Aide"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /status"""
        message = (
            f"📊 *État du Bot*\n\n"
            f"Paire: {config.SYMBOL}\n"
            f"Intervalle: {config.INTERVAL}\n"
            f"Montant: {config.TRADE_AMOUNT_USDT} USDT\n"
            f"Stop Loss: {config.STOP_LOSS_PCT*100:.1f}%\n"
            f"Take Profit: {config.TAKE_PROFIT_PCT*100:.1f}%\n"
            f"Statut: ✅ Actif"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def position_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /position"""
        message = (
            "📍 *Position Actuelle*\n\n"
            "Aucune position ouverte"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /stop"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmer", callback_data="confirm_stop"),
                InlineKeyboardButton("❌ Annuler", callback_data="cancel_stop"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ Êtes-vous sûr d'arrêter le bot?",
            reply_markup=reply_markup,
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commande /help"""
        message = (
            "🆘 *Aide MochiBot*\n\n"
            "*Commandes:*\n"
            "/status - Affiche l'état du bot\n"
            "/position - Affiche la position actuelle\n"
            "/stop - Arrête le bot\n"
            "/help - Affiche cette aide\n\n"
            "*À propos:*\n"
            "MochiBot est un bot de trading automatisé pour Binance.\n"
            "Utilise la stratégie RSI + EMA Crossover."
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gère les boutons inline"""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_stop":
            await query.edit_message_text(
                text="🛑 Bot arrêté par l'utilisateur"
            )
            # TODO: Trigger bot stop
        elif query.data == "cancel_stop":
            await query.edit_message_text(
                text="❌ Arrêt annulé"
            )

    async def send_notification(self, message: str):
        """Envoyer une notification Telegram"""
        if not self.enabled or not self.app:
            return

        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode="Markdown",
            )
        except Exception as e:
            log.error(f"Erreur envoi notification Telegram: {e}")

    async def send_buy_signal(self, price: float, amount: float):
        """Notifier d'un signal d'achat"""
        message = (
            f"🟢 *SIGNAL D'ACHAT*\n\n"
            f"Paire: {config.SYMBOL}\n"
            f"Prix: {price:.4f} USDT\n"
            f"Montant: {amount:.2f} USDT"
        )
        await self.send_notification(message)

    async def send_sell_signal(self, price: float, reason: str):
        """Notifier d'un signal de vente"""
        message = (
            f"🔴 *SIGNAL DE VENTE*\n\n"
            f"Paire: {config.SYMBOL}\n"
            f"Prix: {price:.4f} USDT\n"
            f"Raison: {reason}"
        )
        await self.send_notification(message)

    async def send_position_update(self, price: float, pnl_pct: float):
        """Notifier d'une mise à jour de position"""
        emoji = "📈" if pnl_pct >= 0 else "📉"
        message = (
            f"{emoji} *MISE À JOUR POSITION*\n\n"
            f"Prix actuel: {price:.4f} USDT\n"
            f"P&L: {pnl_pct:+.2f}%"
        )
        await self.send_notification(message)

    async def send_error(self, error: str):
        """Notifier d'une erreur"""
        message = f"❌ *ERREUR*\n\n{error}"
        await self.send_notification(message)


# Instance globale
telegram_notifier = TelegramNotifier()
