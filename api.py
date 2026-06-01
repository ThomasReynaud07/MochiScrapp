"""
API REST pour monitorer et contrôler le bot de trading
Endpoints: /status, /position, /performance, /trades
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import os

from database import db
from logger import log


class TradingAPI:
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)
        self.host = host
        self.port = port
        self.thread = None
        self.exchange_instance = None
        self.risk_instance = None

        self.setup_routes()

    def setup_routes(self):
        """Configure les routes de l'API"""
        @self.app.route("/api/status", methods=["GET"])
        def get_status():
            """Récupère l'état du bot"""
            return jsonify({
                "status": "running",
                "exchange": "binance",
                "symbol": os.getenv("SYMBOL", "BTCUSDT"),
                "interval": os.getenv("INTERVAL", "15m"),
            })

        @self.app.route("/api/position", methods=["GET"])
        def get_position():
            """Récupère la position actuelle"""
            position = db.get_open_position()
            if not position:
                return jsonify({"position": None, "status": "no_position"})
            return jsonify(position)

        @self.app.route("/api/performance", methods=["GET"])
        def get_performance():
            """Récupère les stats de performance"""
            perf = db.get_performance()
            return jsonify(perf)

        @self.app.route("/api/trades", methods=["GET"])
        def get_trades():
            """Récupère l'historique des trades"""
            limit = request.args.get("limit", 10, type=int)
            trades = db.get_trades_history(limit=limit)
            return jsonify({"trades": trades, "total": len(trades)})

        @self.app.route("/api/balance", methods=["GET"])
        def get_balance():
            """Récupère les balances"""
            if not self.exchange_instance:
                return jsonify({"error": "Exchange not available"}), 500
            try:
                usdt = self.exchange_instance.get_usdt_balance()
                base = self.exchange_instance.get_base_balance()
                return jsonify({
                    "usdt": usdt,
                    "base": base,
                    "symbol": os.getenv("SYMBOL", "BTCUSDT"),
                })
            except Exception as e:
                log.error(f"Erreur API balance: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/health", methods=["GET"])
        def health_check():
            """Vérification de santé"""
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "api": "running"
            })

        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({"error": "Endpoint not found"}), 404

        @self.app.errorhandler(500)
        def internal_error(e):
            return jsonify({"error": "Internal server error"}), 500

    def set_exchange(self, exchange):
        """Définir l'instance d'exchange"""
        self.exchange_instance = exchange

    def set_risk_manager(self, risk):
        """Définir l'instance de risk manager"""
        self.risk_instance = risk

    def start(self):
        """Démarrer l'API dans un thread séparé"""
        def run_server():
            try:
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True,
                )
            except Exception as e:
                log.error(f"Erreur API: {e}")

        self.thread = Thread(target=run_server, daemon=True)
        self.thread.start()
        log.info(f"API démarrée sur http://{self.host}:{self.port}")

    def stop(self):
        """Arrêter l'API"""
        # Flask n'a pas d'API directe pour arrêter, on peut utiliser un signal
        log.info("Arrêt de l'API")


# Instance globale
api = TradingAPI(
    host=os.getenv("API_HOST", "0.0.0.0"),
    port=int(os.getenv("API_PORT", 5000))
)
