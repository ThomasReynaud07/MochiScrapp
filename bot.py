"""
MochiBot — Bot de trading Spot Binance
Stratégie : RSI + EMA Crossover combinés
Avec support Telegram, API REST, et persistance
"""

import time
import asyncio
import schedule
import signal
import sys

import config
from exchange import Exchange
from strategy import analyze, Signal
from risk import RiskManager
from logger import log
from database import db
from api import api
from telegram_bot import telegram_notifier
from position_tracker import PositionTracker
from notifications import notification_manager

CANDLE_LIMIT = 150
RUNNING = True


def signal_handler(sig, frame):
    """Gestion de l'interruption du bot"""
    global RUNNING
    log.info("\n⏸ Arrêt du bot...")
    RUNNING = False
    sys.exit(0)


def get_interval_seconds(interval: str) -> int:
    """Convertir l'intervalle en secondes"""
    units = {"m": 60, "h": 3600, "d": 86400}
    return int(interval[:-1]) * units[interval[-1]]


async def run_cycle(exchange: Exchange, risk: RiskManager, tracker: PositionTracker):
    """Cycle principal du bot"""
    try:
        df = exchange.get_candles(limit=CANDLE_LIMIT)
        result = analyze(df)
        current_price = result.price

        log.info(
            f"{config.SYMBOL} @ {current_price:.4f} | {result.reason}"
        )

        # Mettre à jour le prix dans le tracker
        tracker.update_price(current_price)

        # Gérer une position ouverte
        if risk.in_position:
            tracker.check_extreme_moves()
            exit_reason = risk.check_exit(current_price)

            if exit_reason in ("stop_loss", "take_profit"):
                qty = risk.position.quantity
                order = exchange.sell_market(qty)
                if order:
                    pnl = tracker.position.pnl if tracker.position else 0
                    pnl_pct = tracker.position.pnl_pct if tracker.position else 0

                    # Fermer la position
                    risk.close_position()
                    tracker.close_position()

                    # Enregistrer le trade
                    db.close_position(current_price, reason=exit_reason)

                    # Notifications
                    await notification_manager.send_sell_signal(
                        config.SYMBOL, current_price, exit_reason, pnl
                    )

            elif result.signal == Signal.SELL:
                qty = risk.position.quantity
                order = exchange.sell_market(qty)
                if order:
                    pnl = tracker.position.pnl if tracker.position else 0
                    pnl_pct = tracker.position.pnl_pct if tracker.position else 0

                    log.info("Vente sur signal stratégie.")
                    risk.close_position()
                    tracker.close_position()

                    db.close_position(current_price, reason="signal_vente")

                    await notification_manager.send_sell_signal(
                        config.SYMBOL, current_price, "Signal stratégie", pnl
                    )

        # Ouvrir une nouvelle position
        else:
            if result.signal == Signal.BUY:
                usdt_balance = exchange.get_usdt_balance()
                amount = min(config.TRADE_AMOUNT_USDT, usdt_balance)

                if amount < 5:
                    await notification_manager.send_warning(
                        f"Solde USDT insuffisant: {usdt_balance:.2f} USDT"
                    )
                    return

                order = exchange.buy_market(amount)
                if order:
                    qty = exchange.get_base_balance()
                    risk.open_position(current_price, qty)
                    tracker.open_position(config.SYMBOL, current_price, qty, amount)

                    # Enregistrer en DB
                    db.open_position(config.SYMBOL, current_price, qty, amount)

                    # Notifications
                    await notification_manager.send_buy_signal(
                        config.SYMBOL, current_price, amount
                    )

    except Exception as e:
        error_msg = f"Erreur dans le cycle: {str(e)}"
        log.error(error_msg, exc_info=True)
        await notification_manager.send_error(error_msg, error_type="cycle_error")


async def async_cycle_wrapper(exchange, risk, tracker):
    """Wrapper pour exécuter le cycle asynchrone"""
    try:
        await run_cycle(exchange, risk, tracker)
    except Exception as e:
        log.error(f"Erreur wrapper: {e}")


def main():
    """Fonction principale"""
    global RUNNING

    # Configuration du signal handler
    signal.signal(signal.SIGINT, signal_handler)

    log.info("=" * 60)
    log.info("  🤖 MochiBot — Bot de Trading Automatisé")
    log.info("=" * 60)
    log.info(f"  Paire          : {config.SYMBOL}")
    log.info(f"  Intervalle     : {config.INTERVAL}")
    log.info(f"  Montant/trade  : {config.TRADE_AMOUNT_USDT} USDT")
    log.info(f"  Stop Loss      : {config.STOP_LOSS_PCT*100:.1f}%")
    log.info(f"  Take Profit    : {config.TAKE_PROFIT_PCT*100:.1f}%")
    log.info(f"  API REST       : http://0.0.0.0:5000")
    log.info("=" * 60)

    try:
        # Initialiser les composants
        exchange = Exchange()
        risk = RiskManager()
        tracker = PositionTracker()

        # Configurer API et Telegram
        api.set_exchange(exchange)
        api.set_risk_manager(risk)
        api.start()

        # Initialiser Telegram (asynchrone)
        loop = asyncio.get_event_loop()
        if telegram_notifier.enabled:
            loop.run_until_complete(telegram_notifier.initialize())
            notification_manager.set_telegram_notifier(telegram_notifier)

        # Afficher le solde
        usdt = exchange.get_usdt_balance()
        log.info(f"💰 Solde USDT disponible: {usdt:.2f} USDT")

        # Récupérer l'intervalle en secondes
        interval_seconds = get_interval_seconds(config.INTERVAL)

        # Premier cycle
        log.info("🔄 Premier cycle en cours...")
        loop.run_until_complete(asyncio.create_task(
            async_cycle_wrapper(exchange, risk, tracker)
        ))

        # Planifier les cycles
        schedule.every(interval_seconds).seconds.do(
            lambda: loop.run_until_complete(
                async_cycle_wrapper(exchange, risk, tracker)
            )
        )

        log.info(f"✅ Boucle principale active — cycle toutes les {config.INTERVAL}")
        log.info("Appuyez sur Ctrl+C pour arrêter le bot")

        # Boucle principale
        while RUNNING:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        log.info("Arrêt du bot...")
    except Exception as e:
        log.error(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
