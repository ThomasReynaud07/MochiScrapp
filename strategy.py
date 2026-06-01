import pandas as pd
import pandas_ta as ta
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import config


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class StrategyResult:
    signal: Signal
    rsi: float
    ema_fast: float
    ema_slow: float
    price: float
    reason: str


def analyze(df: pd.DataFrame) -> StrategyResult:
    """
    Stratégie combinée RSI + EMA Crossover.

    Signal BUY  : RSI < oversold  ET ema_fast vient de croiser au-dessus de ema_slow
    Signal SELL : RSI > overbought ET ema_fast vient de croiser en-dessous de ema_slow
    Sinon       : HOLD
    """
    if len(df) < config.EMA_SLOW + 5:
        return StrategyResult(Signal.HOLD, 0, 0, 0, df["close"].iloc[-1], "Pas assez de données")

    df = df.copy()
    df["rsi"] = ta.rsi(df["close"], length=config.RSI_PERIOD)
    df["ema_fast"] = ta.ema(df["close"], length=config.EMA_FAST)
    df["ema_slow"] = ta.ema(df["close"], length=config.EMA_SLOW)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    rsi = latest["rsi"]
    ema_fast = latest["ema_fast"]
    ema_slow = latest["ema_slow"]
    price = latest["close"]

    ema_cross_up = prev["ema_fast"] <= prev["ema_slow"] and ema_fast > ema_slow
    ema_cross_down = prev["ema_fast"] >= prev["ema_slow"] and ema_fast < ema_slow

    if rsi < config.RSI_OVERSOLD and ema_cross_up:
        return StrategyResult(
            Signal.BUY, rsi, ema_fast, ema_slow, price,
            f"RSI={rsi:.1f} < {config.RSI_OVERSOLD} + EMA croise vers le haut"
        )

    if rsi > config.RSI_OVERBOUGHT and ema_cross_down:
        return StrategyResult(
            Signal.SELL, rsi, ema_fast, ema_slow, price,
            f"RSI={rsi:.1f} > {config.RSI_OVERBOUGHT} + EMA croise vers le bas"
        )

    return StrategyResult(
        Signal.HOLD, rsi, ema_fast, ema_slow, price,
        f"RSI={rsi:.1f}, EMA{config.EMA_FAST}={ema_fast:.2f}, EMA{config.EMA_SLOW}={ema_slow:.2f}"
    )
