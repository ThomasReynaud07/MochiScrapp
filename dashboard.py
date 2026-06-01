"""
Dashboard Web v2.1.0 — Interface de monitoring et contrôle
Serveur Flask avec interface web responsive
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

from api import api as trading_api
from database_sql import db
from logger import log


class Dashboard:
    """Dashboard Web pour le bot"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.app = Flask(__name__)
        CORS(self.app)
        self.host = host
        self.port = port
        self.exchange = None

        self.setup_routes()

    def setup_routes(self):
        """Configurer les routes du dashboard"""

        @self.app.route("/")
        def index():
            return self.get_dashboard_html()

        @self.app.route("/api/dashboard/summary")
        def dashboard_summary():
            """Résumé principal du dashboard"""
            try:
                perf = db.get_performance()
                position = db.get_open_position()
                usdt = self.exchange.get_usdt_balance() if self.exchange else 0

                return jsonify({
                    "status": "running",
                    "balance_usdt": usdt,
                    "position": position,
                    "performance": perf,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                log.error(f"Erreur dashboard summary: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/dashboard/trades")
        def dashboard_trades():
            """Historique des trades"""
            limit = request.args.get("limit", 20, type=int)
            trades = db.get_trades_history(limit=limit)
            return jsonify({"trades": trades})

        @self.app.route("/api/dashboard/chart-data")
        def chart_data():
            """Données pour les charts"""
            trades = db.get_trades_history(limit=100)

            # Préparer les données pour les charts
            labels = [t["exit_time"].split("T")[0] for t in trades]
            equity = [t["pnl"] for t in trades]
            win_rate_data = [100 if t["pnl"] > 0 else 0 for t in trades]

            return jsonify({
                "labels": labels,
                "equity": equity,
                "win_rate": win_rate_data,
            })

    def set_exchange(self, exchange):
        """Définir l'instance d'exchange"""
        self.exchange = exchange

    def get_dashboard_html(self):
        """Retourner l'HTML du dashboard"""
        html = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 MochiBot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            color: white;
            margin-bottom: 30px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card h2 {
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }

        .card .subtext {
            font-size: 0.85em;
            color: #999;
            margin-top: 10px;
        }

        .status-running {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .status-running h2 {
            color: rgba(255,255,255,0.9);
        }

        .positive {
            color: #27ae60;
        }

        .negative {
            color: #e74c3c;
        }

        .neutral {
            color: #3498db;
        }

        .table-container {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e9ecef;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: white;
            font-size: 1.2em;
        }

        .error {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 MochiBot Dashboard</h1>
            <p>Bot de Trading Automatisé pour Binance</p>
        </header>

        <div id="error-container"></div>

        <div class="grid">
            <div class="card status-running">
                <h2>Statut du Bot</h2>
                <div class="value" id="status">Chargement...</div>
                <div class="subtext" id="status-time"></div>
            </div>

            <div class="card">
                <h2>Balance USDT</h2>
                <div class="value neutral" id="balance">-</div>
                <div class="subtext">Solde disponible</div>
            </div>

            <div class="card">
                <h2>Position Actuelle</h2>
                <div class="value" id="position">Aucune</div>
                <div class="subtext" id="position-info"></div>
            </div>

            <div class="card">
                <h2>Total Trades</h2>
                <div class="value neutral" id="total-trades">-</div>
                <div class="subtext" id="trades-info"></div>
            </div>

            <div class="card">
                <h2>Win Rate</h2>
                <div class="value" id="win-rate">-</div>
                <div class="subtext">Taux de réussite</div>
            </div>

            <div class="card">
                <h2>Total P&L</h2>
                <div class="value" id="total-pnl">-</div>
                <div class="subtext">Profit/Loss global</div>
            </div>
        </div>

        <div class="table-container">
            <h2 style="margin-bottom: 20px;">📊 Historique des Trades</h2>
            <table id="trades-table">
                <thead>
                    <tr>
                        <th>Paire</th>
                        <th>Prix Entrée</th>
                        <th>Prix Sortie</th>
                        <th>Quantité</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                        <th>Date Sortie</th>
                    </tr>
                </thead>
                <tbody id="trades-body">
                    <tr><td colspan="7" style="text-align: center; padding: 30px;">Chargement...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Refresh les données toutes les 5 secondes
        async function updateDashboard() {
            try {
                const response = await fetch('/api/dashboard/summary');
                const data = await response.json();

                // Mettre à jour les valeurs
                document.getElementById('status').innerText = '✅ Actif';
                document.getElementById('status-time').innerText = new Date(data.timestamp).toLocaleString();
                document.getElementById('balance').innerText = data.balance_usdt.toFixed(2) + ' USDT';

                // Position
                if (data.position) {
                    document.getElementById('position').innerText = data.position.symbol;
                    document.getElementById('position-info').innerText =
                        `Entrée: ${data.position.entry_price.toFixed(4)} | Qty: ${data.position.quantity.toFixed(8)}`;
                } else {
                    document.getElementById('position').innerText = 'Aucune';
                    document.getElementById('position-info').innerText = '';
                }

                // Performance
                const perf = data.performance;
                document.getElementById('total-trades').innerText = perf.total_trades || 0;
                document.getElementById('trades-info').innerText =
                    `${perf.winning_trades || 0}G / ${perf.losing_trades || 0}P`;

                const winRate = perf.win_rate || 0;
                const winRateEl = document.getElementById('win-rate');
                winRateEl.innerText = winRate.toFixed(1) + '%';
                winRateEl.className = 'value ' + (winRate >= 50 ? 'positive' : 'negative');

                const pnl = perf.total_profit_loss || 0;
                const pnlEl = document.getElementById('total-pnl');
                pnlEl.innerText = pnl.toFixed(4);
                pnlEl.className = 'value ' + (pnl >= 0 ? 'positive' : 'negative');

                // Tableau des trades
                await updateTradesTable();

            } catch (error) {
                console.error('Erreur:', error);
                document.getElementById('error-container').innerHTML =
                    '<div class="error">❌ Erreur de connexion à l\'API</div>';
            }
        }

        async function updateTradesTable() {
            try {
                const response = await fetch('/api/dashboard/trades?limit=10');
                const data = await response.json();
                const tbody = document.getElementById('trades-body');

                if (!data.trades || data.trades.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">Aucun trade</td></tr>';
                    return;
                }

                tbody.innerHTML = data.trades.map(trade => `
                    <tr>
                        <td>${trade.symbol}</td>
                        <td>${trade.entry_price.toFixed(4)}</td>
                        <td>${trade.exit_price.toFixed(4)}</td>
                        <td>${trade.quantity.toFixed(8)}</td>
                        <td class="${trade.pnl >= 0 ? 'positive' : 'negative'}">
                            ${trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(4)}
                        </td>
                        <td class="${trade.pnl_pct >= 0 ? 'positive' : 'negative'}">
                            ${trade.pnl_pct >= 0 ? '+' : ''}${trade.pnl_pct.toFixed(2)}%
                        </td>
                        <td>${new Date(trade.exit_time).toLocaleString()}</td>
                    </tr>
                `).join('');

            } catch (error) {
                console.error('Erreur tableau:', error);
            }
        }

        // Première mise à jour
        updateDashboard();

        // Mise à jour automatique
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
        """
        return html

    def start(self):
        """Démarrer le dashboard"""
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True,
            )
        except Exception as e:
            log.error(f"Erreur dashboard: {e}")


# Instance globale
dashboard = Dashboard(
    host=os.getenv("DASHBOARD_HOST", "0.0.0.0"),
    port=int(os.getenv("DASHBOARD_PORT", 8080))
)
