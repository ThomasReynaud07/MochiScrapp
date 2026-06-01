"""
Manager de stratégies v2.1.0
- Support stratégies custom
- Backtesting simple
- Signal scoring
- Hot-swap de stratégie
"""

import importlib.util
import sys
from pathlib import Path
from typing import Callable, Dict, List
from datetime import datetime
from dataclasses import dataclass
import pandas as pd

from logger import log
from strategy import Signal


@dataclass
class StrategyInfo:
    """Information sur une stratégie"""
    name: str
    description: str
    author: str
    version: str
    parameters: Dict


class StrategyManager:
    """Gestionnaire de stratégies custom"""

    def __init__(self, strategies_dir: str = "strategies"):
        self.strategies_dir = Path(strategies_dir)
        self.strategies_dir.mkdir(exist_ok=True)
        self.loaded_strategies = {}
        self.current_strategy = None
        self.load_builtin_strategies()

    def load_builtin_strategies(self):
        """Charger les stratégies intégrées"""
        try:
            from strategy import analyze, Signal as BuiltinSignal
            self.loaded_strategies["builtin"] = {
                "func": analyze,
                "name": "RSI + EMA Crossover (Builtin)",
                "description": "Stratégie par défaut du bot",
                "type": "builtin",
            }
            self.current_strategy = "builtin"
            log.info("✅ Stratégie builtin chargée")
        except Exception as e:
            log.error(f"❌ Erreur chargement stratégie builtin: {e}")

    def load_custom_strategy(self, filepath: str) -> bool:
        """Charger une stratégie custom depuis un fichier Python"""
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                log.error(f"❌ Fichier stratégie non trouvé: {filepath}")
                return False

            # Charger le module
            spec = importlib.util.spec_from_file_location("custom_strategy", filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules["custom_strategy"] = module
            spec.loader.exec_module(module)

            # Vérifier que le module a une fonction analyze
            if not hasattr(module, "analyze"):
                log.error("❌ Le module n'a pas de fonction 'analyze'")
                return False

            # Charger la stratégie
            strategy_name = filepath.stem
            self.loaded_strategies[strategy_name] = {
                "func": module.analyze,
                "name": getattr(module, "STRATEGY_NAME", strategy_name),
                "description": getattr(module, "STRATEGY_DESCRIPTION", "Stratégie custom"),
                "type": "custom",
            }

            log.info(f"✅ Stratégie custom chargée: {strategy_name}")
            return True

        except Exception as e:
            log.error(f"❌ Erreur chargement stratégie custom: {e}", exc_info=True)
            return False

    def load_all_custom_strategies(self) -> int:
        """Charger toutes les stratégies du dossier strategies/"""
        if not self.strategies_dir.exists():
            self.strategies_dir.mkdir(exist_ok=True)
            return 0

        count = 0
        for strategy_file in self.strategies_dir.glob("*.py"):
            if strategy_file.name.startswith("_"):
                continue

            if self.load_custom_strategy(str(strategy_file)):
                count += 1

        log.info(f"📊 {count} stratégie(s) custom chargée(s)")
        return count

    def set_strategy(self, strategy_name: str) -> bool:
        """Changer la stratégie active"""
        if strategy_name not in self.loaded_strategies:
            log.error(f"❌ Stratégie non trouvée: {strategy_name}")
            return False

        self.current_strategy = strategy_name
        log.info(f"✅ Stratégie activée: {self.loaded_strategies[strategy_name]['name']}")
        return True

    def analyze(self, df: pd.DataFrame):
        """Analyser avec la stratégie actuelle"""
        if not self.current_strategy or self.current_strategy not in self.loaded_strategies:
            log.error("❌ Aucune stratégie active")
            return None

        try:
            strategy_func = self.loaded_strategies[self.current_strategy]["func"]
            return strategy_func(df)
        except Exception as e:
            log.error(f"❌ Erreur analyse stratégie: {e}", exc_info=True)
            return None

    def list_strategies(self) -> List[Dict]:
        """Lister toutes les stratégies disponibles"""
        return [
            {
                "name": key,
                "display_name": info["name"],
                "description": info["description"],
                "type": info["type"],
                "active": key == self.current_strategy,
            }
            for key, info in self.loaded_strategies.items()
        ]

    def get_current_strategy(self) -> Dict:
        """Obtenir la stratégie active"""
        if self.current_strategy in self.loaded_strategies:
            return self.loaded_strategies[self.current_strategy]
        return None


class SimpleBacktester:
    """Backtesteur simple pour valider une stratégie"""

    def __init__(self, strategy_manager: StrategyManager):
        self.strategy_manager = strategy_manager

    def backtest(
        self,
        df: pd.DataFrame,
        initial_balance: float = 1000.0,
        trade_amount: float = 20.0,
        strategy_name: str = None
    ) -> Dict:
        """
        Faire un backtest simple
        """
        if strategy_name:
            self.strategy_manager.set_strategy(strategy_name)

        balance = initial_balance
        position = None
        trades = []
        equity_curve = [initial_balance]

        try:
            for idx, row in df.iterrows():
                # Analyse
                result = self.strategy_manager.analyze(df.iloc[:idx+1])
                if not result:
                    continue

                current_price = result.price

                # Gestion position
                if position:
                    # Calculer P&L
                    pnl = (current_price - position["entry"]) * position["qty"]

                    # Vente sur signal
                    if result.signal == Signal.SELL:
                        trades.append({
                            "entry": position["entry"],
                            "exit": current_price,
                            "qty": position["qty"],
                            "pnl": pnl,
                            "pnl_pct": (pnl / (position["entry"] * position["qty"])) * 100,
                            "type": "sell",
                        })
                        balance += pnl
                        position = None

                else:
                    # Achat sur signal
                    if result.signal == Signal.BUY and balance >= trade_amount:
                        qty = trade_amount / current_price
                        position = {"entry": current_price, "qty": qty}

                equity_curve.append(balance)

            # Résumé
            winning = len([t for t in trades if t["pnl"] > 0])
            total_return = ((balance - initial_balance) / initial_balance) * 100

            return {
                "initial_balance": initial_balance,
                "final_balance": balance,
                "total_return": total_return,
                "trades": len(trades),
                "winning_trades": winning,
                "losing_trades": len(trades) - winning,
                "win_rate": (winning / len(trades) * 100) if trades else 0,
                "total_pnl": balance - initial_balance,
                "equity_curve": equity_curve,
                "trades": trades,
            }

        except Exception as e:
            log.error(f"❌ Erreur backtest: {e}", exc_info=True)
            return None


# Instance globale
strategy_manager = StrategyManager()
backtester = SimpleBacktester(strategy_manager)
