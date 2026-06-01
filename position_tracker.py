"""
Suivi avancé des positions avec notifications en temps réel
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from logger import log


@dataclass
class Position:
    """Représente une position ouverte"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime
    amount_invested: float

    @property
    def current_price(self) -> float:
        """Prix actuel (doit être mis à jour de l'extérieur)"""
        return self._current_price

    @property
    def pnl(self) -> float:
        """Profit/Loss en USDT"""
        return (self.current_price - self.entry_price) * self.quantity

    @property
    def pnl_pct(self) -> float:
        """Profit/Loss en pourcentage"""
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

    @property
    def duration(self) -> float:
        """Durée de la position en minutes"""
        elapsed = datetime.now() - self.entry_time
        return elapsed.total_seconds() / 60


class PositionTracker:
    """Gestion avancée des positions"""

    def __init__(self):
        self.position: Optional[Position] = None
        self.max_loss_notified = False
        self.max_gain_notified = False

    def open_position(
        self,
        symbol: str,
        entry_price: float,
        quantity: float,
        amount: float,
    ):
        """Ouvrir une nouvelle position"""
        self.position = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            amount_invested=amount,
        )
        self.position._current_price = entry_price
        self.max_loss_notified = False
        self.max_gain_notified = False

        log.info(
            f"Position ouverte: {symbol} | "
            f"Prix entrée: {entry_price:.4f} | "
            f"Quantité: {quantity:.8f}"
        )

    def close_position(self):
        """Fermer la position actuelle"""
        if not self.position:
            log.warning("Aucune position à fermer")
            return None

        closed = self.position
        log.info(
            f"Position fermée: {closed.symbol} | "
            f"Prix sortie: {closed.current_price:.4f} | "
            f"P&L: {closed.pnl:+.4f} ({closed.pnl_pct:+.2f}%) | "
            f"Durée: {closed.duration:.0f}min"
        )

        self.position = None
        return closed

    def update_price(self, current_price: float):
        """Mettre à jour le prix actuel"""
        if self.position:
            self.position._current_price = current_price

    def check_extreme_moves(self, max_loss_pct: float = -5.0, max_gain_pct: float = 10.0):
        """Vérifier les mouvements extrêmes et envoyer des notifications"""
        if not self.position:
            return

        pnl_pct = self.position.pnl_pct

        # Perte importante
        if pnl_pct <= max_loss_pct and not self.max_loss_notified:
            log.warning(
                f"⚠️ ALERTE: Perte importante atteinte! "
                f"{self.position.symbol} à {pnl_pct:.2f}%"
            )
            self.max_loss_notified = True

        # Gain important
        if pnl_pct >= max_gain_pct and not self.max_gain_notified:
            log.info(
                f"🎯 ALERTE: Gain important atteint! "
                f"{self.position.symbol} à {pnl_pct:+.2f}%"
            )
            self.max_gain_notified = True

    def get_position_info(self) -> dict:
        """Récupérer les infos de la position actuelle"""
        if not self.position:
            return {}

        p = self.position
        return {
            "symbol": p.symbol,
            "entry_price": p.entry_price,
            "current_price": p.current_price,
            "quantity": p.quantity,
            "amount_invested": p.amount_invested,
            "pnl": p.pnl,
            "pnl_pct": p.pnl_pct,
            "duration_minutes": p.duration,
            "entry_time": p.entry_time.isoformat(),
        }

    def is_position_open(self) -> bool:
        """Vérifier si une position est ouverte"""
        return self.position is not None
