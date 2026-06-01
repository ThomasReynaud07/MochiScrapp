"""
Risk Management Avancé v2.1.0
- Position sizing dynamique (Kelly Criterion)
- Drawdown management
- Daily loss limit
- Equity curve monitoring
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
import config
from logger import log


@dataclass
class RiskMetrics:
    """Métriques de risque"""
    position_size: float
    kelly_fraction: float
    max_position_size: float
    daily_loss_limit: float
    current_daily_loss: float
    max_drawdown: float
    current_drawdown: float
    equity_peak: float
    equity_current: float


class AdvancedRiskManager:
    """Gestion du risque avancée"""

    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.equity_peak = initial_balance
        self.equity_history = []
        self.daily_start_balance = initial_balance
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.last_date = None

    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """
        Calculer la fraction Kelly pour position sizing dynamique
        f* = (bp - q) / b
        où:
        - b = ratio gain/perte
        - p = probabilité de gain
        - q = probabilité de perte = 1 - p
        - f* est multiplié par kelly_fraction pour être conservateur
        """
        if avg_loss == 0 or win_rate == 0:
            return 0.02  # 2% par défaut

        win_rate = min(max(win_rate / 100, 0.01), 0.99)  # Clamp entre 1% et 99%
        loss_rate = 1 - win_rate

        if avg_loss > 0 and avg_win > 0:
            b = avg_win / avg_loss
            kelly = (b * win_rate - loss_rate) / b if b > 0 else 0
            kelly = max(min(kelly, 0.25), 0.01)  # Clamp entre 1% et 25%
            kelly = kelly * kelly_fraction  # Fractional Kelly

            return kelly
        return 0.02

    def calculate_position_size(
        self,
        balance: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """Calculer la taille de position dynamique"""
        kelly = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss, kelly_fraction)
        position_size = balance * kelly
        return position_size

    def update_equity(self, current_balance: float):
        """Mettre à jour l'équité et calculer le drawdown"""
        self.current_balance = current_balance

        # Vérifier si nouveau jour
        today = date.today()
        if self.last_date != today:
            self.daily_start_balance = current_balance
            self.last_date = today

        # Mise à jour equity peak
        if current_balance > self.equity_peak:
            self.equity_peak = current_balance

        # Calcul drawdown
        if self.equity_peak > 0:
            self.current_drawdown = ((self.equity_peak - current_balance) / self.equity_peak) * 100

        # Mise à jour max drawdown
        if self.current_drawdown > self.max_drawdown:
            self.max_drawdown = self.current_drawdown

        # Historique
        self.equity_history.append({
            "timestamp": datetime.now().isoformat(),
            "equity": current_balance,
            "drawdown": self.current_drawdown
        })

    def get_daily_loss(self) -> float:
        """Obtenir la perte du jour"""
        return self.daily_start_balance - self.current_balance

    def check_daily_loss_limit(self, daily_loss_limit_pct: float = 5.0) -> bool:
        """Vérifier si on a atteint la limite de perte journalière"""
        daily_loss = self.get_daily_loss()
        daily_loss_pct = (daily_loss / self.daily_start_balance) * 100

        if daily_loss_pct >= daily_loss_limit_pct:
            log.error(
                f"❌ ALERTE: Limite de perte journalière atteinte! "
                f"{daily_loss_pct:.2f}% (limite: {daily_loss_limit_pct}%)"
            )
            return True

        return False

    def check_drawdown_limit(self, max_drawdown_limit_pct: float = 20.0) -> bool:
        """Vérifier si le drawdown max est dépassé"""
        if self.max_drawdown >= max_drawdown_limit_pct:
            log.error(
                f"❌ ALERTE: Max drawdown atteint! "
                f"{self.max_drawdown:.2f}% (limite: {max_drawdown_limit_pct}%)"
            )
            return True

        return False

    def get_risk_metrics(self) -> RiskMetrics:
        """Obtenir les métriques de risque actuelles"""
        daily_loss = self.get_daily_loss()
        daily_loss_pct = (daily_loss / self.daily_start_balance) * 100

        return RiskMetrics(
            position_size=self.current_balance * 0.05,  # 5% par défaut
            kelly_fraction=0.25,
            max_position_size=self.current_balance * 0.10,  # 10% max
            daily_loss_limit=self.daily_start_balance * 0.05,  # 5% du solde du jour
            current_daily_loss=daily_loss,
            max_drawdown=self.max_drawdown,
            current_drawdown=self.current_drawdown,
            equity_peak=self.equity_peak,
            equity_current=self.current_balance,
        )

    def reset_daily_metrics(self):
        """Réinitialiser les métriques journalières"""
        self.daily_start_balance = self.current_balance
        self.last_date = date.today()
        log.info("📊 Métriques journalières réinitialisées")

    def get_equity_curve(self, limit: int = 100) -> list:
        """Obtenir la courbe d'équité"""
        return self.equity_history[-limit:]
