# 🤖 MochiBot — Bot de Trading Automatisé pour Binance

Bot de trading entièrement automatisé utilisant la stratégie **RSI + EMA Crossover** avec support Telegram, API REST et persistance des données.

## 🚀 Fonctionnalités

✅ **Trading Automatisé**
- Stratégie RSI + EMA Crossover
- Gestion du risque (Stop Loss + Take Profit)
- Trading sur Binance Spot

✅ **Notifications Telegram**
- Notifications pour chaque signal d'achat/vente
- Commandes: `/status`, `/position`, `/stop`, `/help`
- Alertes d'erreur en temps réel

✅ **API REST**
- `/api/status` — État du bot
- `/api/position` — Position actuelle
- `/api/performance` — Stats de trading
- `/api/trades` — Historique des trades
- `/api/balance` — Balances Binance
- `/api/health` — Vérification de santé

✅ **Persistance des Données**
- Sauvegarde automatique des positions
- Historique complet des trades
- Statistiques de performance

---

## 📋 Installation Rapide

### 1. Prérequis
- Python 3.8+
- Compte Binance avec clés API
- Bot Telegram (optionnel)

### 2. Installation

```bash
# Cloner le repo
git clone https://github.com/your-repo/MochiBot.git
cd MochiBot

# Créer venv
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer dépendances
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec tes clés
# - BINANCE_API_KEY
# - BINANCE_API_SECRET
# - TELEGRAM_BOT_TOKEN (optionnel)
# - TELEGRAM_CHAT_ID (optionnel)
```

### 4. Démarrer

```bash
python bot.py
```

---

## 📱 Commandes Telegram

| Commande | Description |
|----------|-------------|
| `/start` | Affiche les commandes |
| `/status` | État du bot |
| `/position` | Position actuelle |
| `/stop` | Arrêter le bot |
| `/help` | Aide |

---

## 🌐 API REST

```bash
# Status
curl http://localhost:5000/api/status

# Position
curl http://localhost:5000/api/position

# Performance
curl http://localhost:5000/api/performance

# Trades
curl http://localhost:5000/api/trades?limit=10

# Balance
curl http://localhost:5000/api/balance

# Health
curl http://localhost:5000/api/health
```

---

## 📈 Stratégie

**RSI + EMA Crossover**

- **BUY**: RSI < 35 (oversold) + EMA Fast > EMA Slow
- **SELL**: RSI > 65 (overbought) OU Stop Loss/Take Profit atteint

Paramètres configurables dans `.env`

---

## 📊 Fichier de Données

`trading_data.json` — Contient:
- Positions ouvertes/fermées
- Historique des trades
- Statistiques de performance

---

## ⚠️ Important

⚠️ **Risques du trading automatisé**
- Test sur petits montants d'abord
- Utilise des clés API avec Spot Trading ONLY
- Ne partage jamais ton `.env`

---

## 🐛 Troubleshooting

| Problème | Solution |
|----------|----------|
| API keys invalid | Vérifie tes clés Binance |
| Insufficient balance | Dépôt USDT sur Binance |
| Pas de notif Telegram | Vérifie token + chat_id |
| API non accessible | Firewall? Vérifie port 5000 |

---

## 📄 License

MIT License

---

**Version**: 2.0.0