"""
Exemple de Stratégie Custom: MACD
Copie ce fichier dans le dossier strategies/ et change le nom
Renomme-le en ma_strategie.py pour l'utiliser!

Comment charger:
from strategy_manager import strategy_manager
strategy_manager.load_custom_strategy("strategies/ma_strategie.py")
strategy_manager.set_strategy("ma_strategie")
"""

from dataclasses import dataclass
from enum import Enum
import pandas as pd
import pandas_ta

# Constantes requises
STRATEGY_NAME = "MACD Crossover"
STRATEGY_DESCRIPTION = "Stratégie basée sur le croisement MACD"


class Signal(Enum):
    """Signaux possibles"""
    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass
class AnalysisResult:
    """Résultat de l'analyse"""
    signal: Signal
    price: float
    reason: str
    strength: float  # 0-100


def analyze(df: pd.DataFrame) -> AnalysisResult:
    """
    Analyser avec la stratégie MACD

    Args:
        df: DataFrame avec OHLCV

    Returns:
        AnalysisResult avec signal et raison
    """
    if df is None or len(df) < 30:
        return AnalysisResult(
            signal=Signal.HOLD,
            price=0,
            reason="Pas assez de données",
            strength=0
        )

    current_price = df['close'].iloc[-1]

    # Calculer MACD
    macd = pd.Series(pandas_ta.macd(df['close'], fast=12, slow=26, signal=9)[0:3]).values
    macd_line = macd[0] if len(macd) > 0 else 0
    macd_signal = macd[1] if len(macd) > 1 else 0
    macd_hist = macd[2] if len(macd) > 2 else 0

    # Calculer RSI pour confirmation
    rsi = pandas_ta.rsi(df['close'], length=14).iloc[-1]

    # Logique du signal
    signal = Signal.HOLD
    reason = ""
    strength = 50

    # BUY: MACD line > Signal line + RSI < 70
    if macd_line > macd_signal and rsi < 70:
        signal = Signal.BUY
        reason = f"MACD Crossover Haut (RSI: {rsi:.1f})"
        strength = min(100, 50 + (macd_hist * 100))

    # SELL: MACD line < Signal line + RSI > 30
    elif macd_line < macd_signal and rsi > 30:
        signal = Signal.SELL
        reason = f"MACD Crossover Bas (RSI: {rsi:.1f})"
        strength = min(100, 50 + (abs(macd_hist) * 100))

    else:
        signal = Signal.HOLD
        reason = f"MACD Neutre | RSI: {rsi:.1f}"
        strength = 50

    return AnalysisResult(
        signal=signal,
        price=current_price,
        reason=reason,
        strength=strength
    )


# Tu peux ajouter d'autres paramètres personnalisables
PARAMS = {
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
}
