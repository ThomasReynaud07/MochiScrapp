"""
Base de données SQLite robuste avec SQLAlchemy
Remplace database.py pour persistance plus robuste
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import shutil

from logger import log

# Configuration
DB_PATH = "trading_data.db"
BACKUP_DIR = Path("backups")

Base = declarative_base()


class Position(Base):
    """Modèle Position"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    entry_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    entry_time = Column(DateTime, default=datetime.now)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    status = Column(String(20), default="open")  # open, closed


class Trade(Base):
    """Modèle Trade"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    pnl = Column(Float, nullable=False)
    pnl_pct = Column(Float, nullable=False)
    reason = Column(String(100))


class Performance(Base):
    """Modèle Performance"""
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_profit_loss = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    daily_loss = Column(Float, default=0.0)
    equity = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SQLDatabase:
    """Gestion base de données SQLite"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.Session = sessionmaker(bind=self.engine)

        # Créer les tables
        Base.metadata.create_all(self.engine)

        # Initialiser performance si vide
        session = self.Session()
        if session.query(Performance).count() == 0:
            perf = Performance()
            session.add(perf)
            session.commit()
        session.close()

        log.info(f"✅ Base de données SQLite initialisée: {db_path}")

    def open_position(self, symbol: str, entry_price: float, quantity: float, amount: float) -> Position:
        """Ouvrir une position"""
        session = self.Session()
        try:
            position = Position(
                symbol=symbol,
                entry_price=entry_price,
                quantity=quantity,
                amount=amount,
                entry_time=datetime.now(),
                status="open"
            )
            session.add(position)
            session.commit()
            log.info(f"Position ouverte: {symbol} @ {entry_price:.4f}")
            return position
        finally:
            session.close()

    def close_position(self, exit_price: float, reason: str = "") -> dict:
        """Fermer la position ouverte"""
        session = self.Session()
        try:
            # Trouver la position ouverte
            position = session.query(Position).filter_by(status="open").first()
            if not position:
                log.warning("Aucune position ouverte à fermer")
                return None

            # Calculer P&L
            entry = position.entry_price
            quantity = position.quantity
            pnl = (exit_price - entry) * quantity
            pnl_pct = ((exit_price - entry) / entry) * 100

            # Créer le trade
            trade = Trade(
                symbol=position.symbol,
                entry_price=entry,
                exit_price=exit_price,
                quantity=quantity,
                entry_time=position.entry_time,
                exit_time=datetime.now(),
                pnl=pnl,
                pnl_pct=pnl_pct,
                reason=reason
            )

            # Mettre à jour la position
            position.exit_price = exit_price
            position.exit_time = datetime.now()
            position.pnl = pnl
            position.pnl_pct = pnl_pct
            position.status = "closed"

            # Mettre à jour performance
            perf = session.query(Performance).first()
            perf.total_trades += 1
            if pnl > 0:
                perf.winning_trades += 1
            else:
                perf.losing_trades += 1
            perf.total_profit_loss += pnl
            if perf.total_trades > 0:
                perf.win_rate = (perf.winning_trades / perf.total_trades) * 100

            session.add(trade)
            session.commit()

            log.info(
                f"Position fermée: {position.symbol} | "
                f"P&L: {pnl:+.4f} ({pnl_pct:+.2f}%) | {reason}"
            )

            return {
                "id": trade.id,
                "symbol": trade.symbol,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "reason": reason
            }
        finally:
            session.close()

    def get_open_position(self) -> dict:
        """Récupérer la position ouverte"""
        session = self.Session()
        try:
            position = session.query(Position).filter_by(status="open").first()
            if position:
                return {
                    "id": position.id,
                    "symbol": position.symbol,
                    "entry_price": position.entry_price,
                    "quantity": position.quantity,
                    "amount": position.amount,
                    "entry_time": position.entry_time.isoformat(),
                }
            return None
        finally:
            session.close()

    def get_performance(self) -> dict:
        """Récupérer les stats de performance"""
        session = self.Session()
        try:
            perf = session.query(Performance).first()
            if perf:
                return {
                    "total_trades": perf.total_trades,
                    "winning_trades": perf.winning_trades,
                    "losing_trades": perf.losing_trades,
                    "total_profit_loss": perf.total_profit_loss,
                    "win_rate": perf.win_rate,
                    "max_drawdown": perf.max_drawdown,
                    "daily_loss": perf.daily_loss,
                    "equity": perf.equity,
                }
            return {}
        finally:
            session.close()

    def get_trades_history(self, limit: int = 10) -> list:
        """Récupérer l'historique des trades"""
        session = self.Session()
        try:
            trades = session.query(Trade).order_by(Trade.id.desc()).limit(limit).all()
            return [
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "quantity": t.quantity,
                    "pnl": t.pnl,
                    "pnl_pct": t.pnl_pct,
                    "entry_time": t.entry_time.isoformat(),
                    "exit_time": t.exit_time.isoformat(),
                    "reason": t.reason,
                }
                for t in reversed(trades)
            ]
        finally:
            session.close()

    def update_drawdown(self, max_drawdown: float):
        """Mettre à jour le drawdown max"""
        session = self.Session()
        try:
            perf = session.query(Performance).first()
            if perf:
                perf.max_drawdown = max(perf.max_drawdown, max_drawdown)
                session.commit()
        finally:
            session.close()

    def update_daily_loss(self, loss: float):
        """Mettre à jour la perte du jour"""
        session = self.Session()
        try:
            perf = session.query(Performance).first()
            if perf:
                perf.daily_loss = loss
                session.commit()
        finally:
            session.close()

    def backup(self):
        """Créer une sauvegarde de la DB"""
        try:
            BACKUP_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"trading_data_{timestamp}.db"
            shutil.copy(self.db_path, backup_file)
            log.info(f"✅ Sauvegarde créée: {backup_file}")
        except Exception as e:
            log.error(f"❌ Erreur sauvegarde: {e}")

    def export_csv(self, filename: str = "trades_export.csv"):
        """Exporter les trades en CSV"""
        try:
            import csv

            session = self.Session()
            trades = session.query(Trade).all()

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Symbol", "Entry Price", "Exit Price", "Quantity",
                    "P&L", "P&L %", "Entry Time", "Exit Time", "Reason"
                ])
                for trade in trades:
                    writer.writerow([
                        trade.id,
                        trade.symbol,
                        f"{trade.entry_price:.8f}",
                        f"{trade.exit_price:.8f}",
                        f"{trade.quantity:.8f}",
                        f"{trade.pnl:.8f}",
                        f"{trade.pnl_pct:.2f}",
                        trade.entry_time.isoformat(),
                        trade.exit_time.isoformat(),
                        trade.reason,
                    ])

            log.info(f"✅ Export CSV créé: {filename}")
            session.close()
            return True
        except Exception as e:
            log.error(f"❌ Erreur export CSV: {e}")
            return False


# Instance globale
db = SQLDatabase()
