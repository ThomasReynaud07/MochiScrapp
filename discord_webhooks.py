"""
Intégration Discord via Webhooks v2.1.0
Notifications d'alertes avancées via Discord
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List

from logger import log


class DiscordWebhook:
    """Gestion des webhooks Discord"""

    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.enabled = bool(self.webhook_url)

        if self.enabled:
            log.info("✅ Discord Webhook activé")
        else:
            log.warning("⚠️  Discord Webhook désactivé")

    async def send_embed(self, embed: Dict) -> bool:
        """Envoyer un embed Discord"""
        if not self.enabled:
            return False

        try:
            payload = {
                "embeds": [embed],
                "timestamp": datetime.now().isoformat()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        return True
                    else:
                        log.error(f"❌ Discord error: {response.status}")
                        return False

        except Exception as e:
            log.error(f"❌ Erreur envoi Discord: {e}")
            return False

    async def send_buy_signal(self, symbol: str, price: float, amount: float, reason: str = ""):
        """Notification signal d'achat"""
        embed = {
            "title": f"🟢 SIGNAL D'ACHAT",
            "description": f"{symbol} @ {price:.4f} USDT",
            "color": 3066993,  # Vert
            "fields": [
                {"name": "Paire", "value": symbol, "inline": True},
                {"name": "Prix", "value": f"{price:.4f} USDT", "inline": True},
                {"name": "Montant", "value": f"{amount:.2f} USDT", "inline": True},
                {"name": "Raison", "value": reason or "Signal stratégie", "inline": False},
            ],
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)

    async def send_sell_signal(self, symbol: str, price: float, pnl: float, pnl_pct: float, reason: str = ""):
        """Notification signal de vente"""
        color = 15158332 if pnl < 0 else 65280  # Rouge si perte, vert si gain
        emoji = "🔴" if pnl < 0 else "🟢"

        embed = {
            "title": f"{emoji} SIGNAL DE VENTE",
            "description": f"{symbol} @ {price:.4f} USDT",
            "color": color,
            "fields": [
                {"name": "Paire", "value": symbol, "inline": True},
                {"name": "Prix", "value": f"{price:.4f} USDT", "inline": True},
                {"name": "P&L", "value": f"{pnl:+.4f} ({pnl_pct:+.2f}%)", "inline": True},
                {"name": "Raison", "value": reason or "Signal stratégie", "inline": False},
            ],
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)

    async def send_alert(self, title: str, message: str, color: int = 16776960):
        """Alerte générique"""
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)

    async def send_risk_alert(self, alert_type: str, details: Dict):
        """Alerte de risque"""
        color_map = {
            "daily_loss": 15158332,  # Rouge
            "max_drawdown": 15158332,  # Rouge
            "position_size": 16776960,  # Jaune
            "equity": 3066993,  # Vert
        }

        embed = {
            "title": f"⚠️ ALERTE: {alert_type.upper()}",
            "color": color_map.get(alert_type, 16776960),
            "fields": [
                {"name": key.replace("_", " ").title(), "value": str(value), "inline": True}
                for key, value in details.items()
            ],
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)

    async def send_performance_report(self, stats: Dict):
        """Rapport de performance"""
        embed = {
            "title": "📊 RAPPORT DE PERFORMANCE",
            "color": 3066993,  # Vert
            "fields": [
                {"name": "Total Trades", "value": str(stats.get("total_trades", 0)), "inline": True},
                {"name": "Win Rate", "value": f"{stats.get('win_rate', 0):.1f}%", "inline": True},
                {"name": "Total P&L", "value": f"{stats.get('total_pnl', 0):+.4f}", "inline": True},
                {"name": "Max Drawdown", "value": f"{stats.get('max_drawdown', 0):.2f}%", "inline": True},
                {"name": "Winning Trades", "value": str(stats.get("winning_trades", 0)), "inline": True},
                {"name": "Losing Trades", "value": str(stats.get("losing_trades", 0)), "inline": True},
            ],
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)

    async def send_strategy_update(self, strategy_name: str, description: str):
        """Notification changement de stratégie"""
        embed = {
            "title": f"🔄 CHANGEMENT STRATÉGIE",
            "description": strategy_name,
            "color": 7506394,  # Bleu
            "fields": [
                {"name": "Détails", "value": description, "inline": False},
            ],
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_embed(embed)


# Instance globale
discord_webhook = DiscordWebhook()
