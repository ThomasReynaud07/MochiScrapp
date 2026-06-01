from dataclasses import dataclass, field
from typing import Optional

import config
from logger import log


@dataclass
class Position:
    entry_price: float
    quantity: float
    stop_loss: float = field(init=False)
    take_profit: float = field(init=False)

    def __post_init__(self):
        self.stop_loss = self.entry_price * (1 - config.STOP_LOSS_PCT)
        self.take_profit = self.entry_price * (1 + config.TAKE_PROFIT_PCT)
        log.info(
            f"Position ouverte @ {self.entry_price:.4f} | "
            f"SL: {self.stop_loss:.4f} | TP: {self.take_profit:.4f}"
        )

    def pnl_pct(self, current_price: float) -> float:
        return (current_price - self.entry_price) / self.entry_price * 100

    def should_stop_loss(self, current_price: float) -> bool:
        return current_price <= self.stop_loss

    def should_take_profit(self, current_price: float) -> bool:
        return current_price >= self.take_profit


class RiskManager:
    def __init__(self):
        self.position: Optional[Position] = None

    @property
    def in_position(self) -> bool:
        return self.position is not None

    def open_position(self, entry_price: float, quantity: float):
        self.position = Position(entry_price, quantity)

    def close_position(self):
        self.position = None

    def check_exit(self, current_price: float) -> Optional[str]:
        if not self.position:
            return None

        if self.position.should_stop_loss(current_price):
            pnl = self.position.pnl_pct(current_price)
            log.warning(f"STOP LOSS déclenché @ {current_price:.4f} | PnL: {pnl:.2f}%")
            return "stop_loss"

        if self.position.should_take_profit(current_price):
            pnl = self.position.pnl_pct(current_price)
            log.info(f"TAKE PROFIT déclenché @ {current_price:.4f} | PnL: {pnl:.2f}%")
            return "take_profit"

        return None
