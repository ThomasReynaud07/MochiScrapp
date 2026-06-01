"""
Script de test pour vérifier la configuration et l'intégration
"""

import sys
import json
from pathlib import Path

import config
from logger import log


def test_env_variables():
    """Test 1: Vérifier les variables d'environnement"""
    log.info("=" * 60)
    log.info("TEST 1: Variables d'Environnement")
    log.info("=" * 60)

    tests = [
        ("API_KEY", config.API_KEY, True),
        ("API_SECRET", config.API_SECRET, True),
        ("SYMBOL", config.SYMBOL, True),
        ("INTERVAL", config.INTERVAL, True),
        ("TRADE_AMOUNT_USDT", str(config.TRADE_AMOUNT_USDT), True),
        ("STOP_LOSS_PCT", str(config.STOP_LOSS_PCT), True),
        ("TAKE_PROFIT_PCT", str(config.TAKE_PROFIT_PCT), True),
        ("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN, False),
        ("TELEGRAM_CHAT_ID", config.TELEGRAM_CHAT_ID, False),
    ]

    passed = 0
    for name, value, required in tests:
        if value:
            log.info(f"✅ {name}: OK")
            passed += 1
        elif required:
            log.error(f"❌ {name}: MANQUANT (REQUIS)")
        else:
            log.warning(f"⚠️  {name}: Pas configuré (optionnel)")

    return passed, len([t for t in tests if t[2]])  # (passed, total_required)


def test_database():
    """Test 2: Vérifier la base de données"""
    log.info("\n" + "=" * 60)
    log.info("TEST 2: Base de Données")
    log.info("=" * 60)

    try:
        from database import db

        # Charger les données
        data = db.load_data()
        log.info(f"✅ Base de données accessible: {len(data)} clés")

        # Vérifier la structure
        required_keys = ["positions", "trades", "performance", "settings"]
        for key in required_keys:
            if key in data:
                log.info(f"   ✅ {key}: OK")
            else:
                log.warning(f"   ⚠️  {key}: Clé manquante")

        # Afficher les stats
        perf = data.get("performance", {})
        log.info(f"\n📊 Statistiques Actuelles:")
        log.info(f"   Total trades: {perf.get('total_trades', 0)}")
        log.info(f"   Win rate: {perf.get('win_rate', 0):.1f}%")
        log.info(f"   Total P&L: {perf.get('total_profit_loss', 0):.4f}")

        return True

    except Exception as e:
        log.error(f"❌ Erreur base de données: {e}")
        return False


def test_exchange():
    """Test 3: Vérifier la connexion Binance"""
    log.info("\n" + "=" * 60)
    log.info("TEST 3: Connexion Binance")
    log.info("=" * 60)

    try:
        from exchange import Exchange

        exchange = Exchange()
        log.info("✅ Connexion établie")

        # Tester les balances
        try:
            usdt = exchange.get_usdt_balance()
            log.info(f"✅ Balance USDT: {usdt:.2f} USDT")

            if usdt < 5:
                log.warning(f"⚠️  Solde faible: {usdt:.2f} USDT")
                log.warning("   Recommandation: Dépose au moins 10 USDT")

            return True
        except Exception as e:
            log.error(f"❌ Erreur lecture balances: {e}")
            log.error("   Vérifie tes clés API et IP whitelist")
            return False

    except Exception as e:
        log.error(f"❌ Erreur connexion Binance: {e}")
        return False


def test_strategy():
    """Test 4: Vérifier la stratégie"""
    log.info("\n" + "=" * 60)
    log.info("TEST 4: Configuration Stratégie")
    log.info("=" * 60)

    try:
        from exchange import Exchange
        from strategy import analyze

        exchange = Exchange()

        # Récupérer des données
        log.info("Récupération des données de marché...")
        df = exchange.get_candles(limit=150)
        log.info(f"✅ {len(df)} bougies reçues")

        # Analyser
        result = analyze(df)
        log.info(f"\n📈 Analyse Stratégie:")
        log.info(f"   Prix actuel: {result.price:.4f}")
        log.info(f"   RSI: {result.rsi:.2f}")
        log.info(f"   EMA Fast: {result.ema_fast:.4f}")
        log.info(f"   EMA Slow: {result.ema_slow:.4f}")
        log.info(f"   Signal: {result.signal.name}")
        log.info(f"   Raison: {result.reason}")

        return True

    except Exception as e:
        log.error(f"❌ Erreur stratégie: {e}")
        return False


def test_api():
    """Test 5: Vérifier l'API REST"""
    log.info("\n" + "=" * 60)
    log.info("TEST 5: API REST")
    log.info("=" * 60)

    try:
        from api import api
        import time
        import requests
        from threading import Thread

        # Démarrer l'API
        log.info("Démarrage de l'API...")
        api_thread = Thread(target=api.start, daemon=True)
        api_thread.start()

        # Attendre le démarrage
        time.sleep(2)

        # Tester les endpoints
        endpoints = [
            "/api/status",
            "/api/health",
            "/api/position",
            "/api/performance",
        ]

        all_ok = True
        for endpoint in endpoints:
            try:
                url = f"http://localhost:5000{endpoint}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    log.info(f"✅ {endpoint}: OK")
                else:
                    log.warning(f"⚠️  {endpoint}: Status {response.status_code}")
                    all_ok = False
            except Exception as e:
                log.error(f"❌ {endpoint}: {e}")
                all_ok = False

        return all_ok

    except Exception as e:
        log.error(f"❌ Erreur API: {e}")
        return False


def test_telegram():
    """Test 6: Vérifier Telegram (optionnel)"""
    log.info("\n" + "=" * 60)
    log.info("TEST 6: Telegram (Optionnel)")
    log.info("=" * 60)

    if not config.TELEGRAM_ENABLED:
        log.warning("⚠️  Telegram non configuré")
        return True

    try:
        from telegram_bot import telegram_notifier
        import asyncio

        log.info("Initialisation Telegram...")

        async def test_init():
            await telegram_notifier.initialize()
            if telegram_notifier.enabled:
                log.info("✅ Telegram connecté")
                # Tester l'envoi
                await telegram_notifier.send_notification("🧪 Test de notification MochiBot")
                log.info("✅ Notification envoyée")
                return True
            else:
                log.error("❌ Telegram désactivé")
                return False

        # Exécuter le test async
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_init())

    except Exception as e:
        log.error(f"❌ Erreur Telegram: {e}")
        return False


def main():
    """Exécuter tous les tests"""
    log.info("\n")
    log.info("🧪 SUITE DE TESTS — MochiBot")
    log.info("=" * 60)

    results = []

    # Test 1
    try:
        passed, total = test_env_variables()
        results.append(("Variables d'Env", passed == total))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("Variables d'Env", False))

    # Test 2
    try:
        results.append(("Base de Données", test_database()))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("Base de Données", False))

    # Test 3
    try:
        results.append(("Connexion Binance", test_exchange()))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("Connexion Binance", False))

    # Test 4
    try:
        results.append(("Stratégie", test_strategy()))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("Stratégie", False))

    # Test 5
    try:
        results.append(("API REST", test_api()))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("API REST", False))

    # Test 6
    try:
        results.append(("Telegram", test_telegram()))
    except Exception as e:
        log.error(f"Test échoué: {e}")
        results.append(("Telegram", False))

    # Résumé
    log.info("\n" + "=" * 60)
    log.info("📋 RÉSUMÉ DES TESTS")
    log.info("=" * 60)

    passed_count = 0
    for test_name, result in results:
        status = "✅" if result else "❌"
        log.info(f"{status} {test_name}")
        if result:
            passed_count += 1

    log.info("\n" + "=" * 60)
    if passed_count == len(results):
        log.info(f"🎉 TOUS LES TESTS RÉUSSIS! ({passed_count}/{len(results)})")
        log.info("✅ Tu peux démarrer le bot avec: python bot.py")
    else:
        log.error(f"❌ {len(results) - passed_count} test(s) échoué(s)")
        log.error("⚠️  Vérifie les erreurs ci-dessus avant de démarrer le bot")
        sys.exit(1)

    log.info("=" * 60 + "\n")


if __name__ == "__main__":
    main()
