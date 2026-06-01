"""
Gestion de la persistance des données (positions, trades, logs)
"""

import json
import os
from datetime import datetime
from pathlib import Path

from logger import log


class Database:
    def __init__(self, db_path: str = "trading_data.json"):
        self.db_path = Path(db_path)
        self.ensure_database()

    def ensure_database(self):
        """Créer la base de données si elle n'existe pas"""
        if not self.db_path.exists():
            initial_data = {
                "positions": [],
                "trades": [],
                "performance": {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "total_profit_loss": 0.0,
                    "win_rate": 0.0,
                },
                "settings": {
                    "created_at": datetime.now().isoformat(),
                    "last_modified": datetime.now().isoformat(),
                }
            }
            self.save_data(initial_data)
            log.info(f"Base de données créée: {self.db_path}")

    def load_data(self) -> dict:
        """Charger tous les données"""
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Erreur lecture base de données: {e}")
            return {}

    def save_data(self, data: dict):
        """Sauvegarder les données"""
        try:
            data["settings"]["last_modified"] = datetime.now().isoformat()
            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.error(f"Erreur sauvegarde base de données: {e}")

    def open_position(self, symbol: str, entry_price: float, quantity: float, amount: float):
        """Enregistrer l'ouverture d'une position"""
        data = self.load_data()
        position = {
            "id": len(data["positions"]) + 1,
            "symbol": symbol,
            "entry_price": entry_price,
            "quantity": quantity,
            "amount": amount,
            "entry_time": datetime.now().isoformat(),
            "status": "open",
        }
        data["positions"].append(position)
        self.save_data(data)
        log.info(f"Position ouverte: {symbol} @ {entry_price:.4f}")
        return position

    def close_position(self, exit_price: float, reason: str = ""):
        """Fermer la position actuelle"""
        data = self.load_data()
        positions = data["positions"]

        # Trouver la position ouverte
        open_position = next(
            (p for p in positions if p["status"] == "open"),
            None
        )

        if not open_position:
            log.warning("Aucune position ouverte à fermer")
            return None

        # Calculer le P&L
        entry = open_position["entry_price"]
        quantity = open_position["quantity"]
        pnl = (exit_price - entry) * quantity
        pnl_pct = ((exit_price - entry) / entry) * 100

        # Créer le trade
        trade = {
            "id": len(data["trades"]) + 1,
            "symbol": open_position["symbol"],
            "entry_price": entry,
            "exit_price": exit_price,
            "quantity": quantity,
            "entry_time": open_position["entry_time"],
            "exit_time": datetime.now().isoformat(),
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "reason": reason,
        }

        # Mettre à jour la position
        open_position["status"] = "closed"
        open_position["exit_price"] = exit_price
        open_position["exit_time"] = datetime.now().isoformat()
        open_position["pnl"] = pnl
        open_position["pnl_pct"] = pnl_pct

        # Ajouter le trade
        data["trades"].append(trade)

        # Mettre à jour les stats
        perf = data["performance"]
        perf["total_trades"] += 1
        if pnl > 0:
            perf["winning_trades"] += 1
        else:
            perf["losing_trades"] += 1
        perf["total_profit_loss"] += pnl
        if perf["total_trades"] > 0:
            perf["win_rate"] = (perf["winning_trades"] / perf["total_trades"]) * 100

        self.save_data(data)

        log.info(
            f"Position fermée: {open_position['symbol']} | "
            f"P&L: {pnl:+.4f} ({pnl_pct:+.2f}%) | {reason}"
        )

        return trade

    def get_open_position(self) -> dict:
        """Récupérer la position ouverte"""
        data = self.load_data()
        positions = data.get("positions", [])
        return next((p for p in positions if p["status"] == "open"), None)

    def get_performance(self) -> dict:
        """Récupérer les stats de performance"""
        data = self.load_data()
        return data.get("performance", {})

    def get_trades_history(self, limit: int = 10) -> list:
        """Récupérer l'historique des trades"""
        data = self.load_data()
        trades = data.get("trades", [])
        return trades[-limit:] if limit else trades


# Instance globale
db = Database()
