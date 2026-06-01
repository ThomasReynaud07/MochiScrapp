# 📖 Guide de Configuration — MochiBot

Guide complet pour configurer et démarrer MochiBot.

---

## 🔧 Étape 1: Préparation Binance

### Créer une clé API Binance

1. Aller sur: https://www.binance.com/en/account/api-management
2. Cliquer sur **"Create API"** (ou "Nouveau API Key")
3. Remplir avec:
   - **Label**: "MochiBot" (ou n'importe quel nom)
   - **Restrictions**: Sélectionner **"Spot Trading"** seulement
   - **Restrictions IP**: (Optionnel - ajouter ton IP pour plus de sécurité)

4. Confirmer avec ton authentification 2FA

**RÉSULTAT:**
```
API Key:    abc123xyz...
Secret Key: def456uvw...
```

⚠️ **Sauvegarde ces clés dans un endroit sûr!**

---

## 🔔 Étape 2: Configuration Telegram (Optionnel)

### Créer un Bot Telegram

1. Ouvrir Telegram et chercher **@BotFather**
2. Envoyer: `/newbot`
3. Répondre aux questions:
   - **Name**: "MochiBot" (ou ton nom)
   - **Username**: "mochitradingbot" (doit être unique)

**RÉSULTAT:**
```
HTTP API:   https://api.telegram.org/bot123:ABC...
Token:      123:ABCdef...
```

4. Copier le **Token**

### Récupérer ton Chat ID

1. Envoyer un message au bot: `/start`
2. Envoyer un message quelconque (ex: "test")
3. Aller sur: `https://api.telegram.org/bot<TON_TOKEN>/getUpdates`
   - Remplacer `<TON_TOKEN>` par ton token
4. Chercher `"chat":{"id":123456789`
   - **123456789** = ton Chat ID

**RÉSULTAT:**
```
Bot Token:  123:ABCdef...
Chat ID:    123456789
```

---

## 💻 Étape 3: Installation Python

### 3a. Télécharger Python

1. Aller sur: https://www.python.org/downloads/
2. Télécharger **Python 3.10+** (ou Plus récent)
3. Installer en cochant **"Add Python to PATH"**

### 3b. Vérifier l'installation

```bash
python --version
# Doit afficher: Python 3.10.x ou plus
```

---

## 📥 Étape 4: Installation du Projet

### 4a. Cloner le repo

```bash
# Windows (PowerShell)
git clone https://github.com/your-repo/MochiBot.git
cd MochiBot

# macOS/Linux (Terminal)
git clone https://github.com/your-repo/MochiBot.git
cd MochiBot
```

### 4b. Créer l'environnement virtuel

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS/Linux (Terminal)
python3 -m venv venv
source venv/bin/activate
```

### 4c. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🔐 Étape 5: Configuration `.env`

### 5a. Créer le fichier `.env`

```bash
# Windows (PowerShell)
copy .env.example .env

# macOS/Linux (Terminal)
cp .env.example .env
```

### 5b. Éditer `.env`

Ouvrir le fichier `.env` avec un éditeur (VS Code, Notepad, etc.)

Remplir avec tes valeurs:

```env
# ========================================
# BINANCE (REQUIS)
# ========================================
BINANCE_API_KEY=abc123xyz...
BINANCE_API_SECRET=def456uvw...

# ========================================
# TRADING
# ========================================
SYMBOL=BTCUSDT          # Paire à trader
INTERVAL=15m            # Intervalle (1m, 5m, 15m, 1h, 4h, 1d)
TRADE_AMOUNT_USDT=20    # Montant par trade (en USDT)

# ========================================
# RISQUE
# ========================================
STOP_LOSS_PCT=2.0       # Stop loss: 2%
TAKE_PROFIT_PCT=4.0     # Take profit: 4%

# ========================================
# TELEGRAM (OPTIONNEL)
# ========================================
TELEGRAM_BOT_TOKEN=123:ABCdef...
TELEGRAM_CHAT_ID=123456789

# ========================================
# API REST (OPTIONNEL)
# ========================================
API_HOST=0.0.0.0
API_PORT=5000
```

💡 **Conseils de Configuration:**

- **BTCUSDT**: Bitcoin — Grand volume, mouvements importants
- **ETHUSDT**: Ethereum — Plus volatile
- **SOLUSDT**: Solana — Plus risqué mais rapide
- **INTERVAL=15m**: Bon pour débuter. 1h pour moins de stress
- **TRADE_AMOUNT_USDT=20**: Petit montant pour tester. Augmente si confiant
- **STOP_LOSS_PCT=2%**: Protège contre les pertes
- **TAKE_PROFIT_PCT=4%**: Verrouille les gains

---

## ▶️ Étape 6: Démarrage

### Méthode 1: Script automatique (Recommandé)

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

### Méthode 2: Manuel

```bash
# Activer venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Démarrer
python bot.py
```

### Sortie attendue:
```
============================================================
  🤖 MochiBot — Bot de Trading Automatisé
============================================================
  Paire          : BTCUSDT
  Intervalle     : 15m
  Montant/trade  : 20 USDT
  Stop Loss      : 2.0%
  Take Profit    : 4.0%
  API REST       : http://0.0.0.0:5000
============================================================
💰 Solde USDT disponible: 500.00 USDT
🔄 Premier cycle en cours...
✅ Boucle principale active — cycle toutes les 15m
Appuyez sur Ctrl+C pour arrêter le bot
```

✅ **BOT ACTIF!**

---

## 🧪 Étape 7: Test & Vérification

### Test API REST

```bash
# Dans un autre terminal
curl http://localhost:5000/api/status
```

**Réponse attendue:**
```json
{
  "status": "running",
  "exchange": "binance",
  "symbol": "BTCUSDT",
  "interval": "15m"
}
```

### Test Telegram

1. Envoyer `/start` au bot dans Telegram
2. Envoyer `/status`
3. Vérifier que tu reçois la réponse

### Test Binance

Le bot affiche le solde USDT au démarrage. Vérifie que c'est correct!

---

## 🎯 Étape 8: Configuration Avancée

### Changer la Paire et l'Intervalle

```env
SYMBOL=ETHUSDT          # Ethereum
INTERVAL=1h             # Hourly
TRADE_AMOUNT_USDT=50    # Plus élevé
```

### Ajuster le Risque

```env
STOP_LOSS_PCT=1.5       # Plus agressif
TAKE_PROFIT_PCT=5.0     # Plus patient
```

### Paramètres Stratégie

```env
RSI_PERIOD=21           # RSI sur 21 (au lieu de 14)
RSI_OVERSOLD=30         # Seuil plus bas
RSI_OVERBOUGHT=70       # Seuil plus haut

EMA_FAST=7              # EMA rapide plus courte
EMA_SLOW=25             # EMA lente plus longue
```

---

## 🐛 Troubleshooting

### ❌ "API keys invalid"
**Cause**: Clés Binance incorrectes
**Solution**:
1. Vérifie tes clés sur Binance
2. Copie exactement (sans espaces)
3. Redémarre le bot

### ❌ "Insufficient balance"
**Cause**: Pas assez de USDT sur Binance
**Solution**:
1. Dépose des USDT sur Binance Spot
2. Attends la confirmation de dépôt
3. Redémarre le bot

### ❌ "Unauthorized request"
**Cause**: IP non whitelistée sur Binance
**Solution**:
1. Va dans Binance API Management
2. Ajoute ton IP publique
3. Attends ~30 secondes
4. Redémarre le bot

### ❌ Pas de notifications Telegram
**Cause**: Token ou Chat ID invalide
**Solution**:
1. Vérifie le token du bot (@BotFather)
2. Vérifie le Chat ID (getUpdates)
3. Envoie `/start` au bot
4. Redémarre le bot

### ❌ "Address already in use" (Port 5000)
**Cause**: Un autre process utilise le port 5000
**Solution**:
1. Change le port dans .env:
   ```env
   API_PORT=5001
   ```
2. Redémarre le bot

---

## ✅ Checklist de Démarrage

- [ ] Clés API Binance obtenues
- [ ] Clés API Telegram obtenues (optionnel)
- [ ] Python 3.8+ installé
- [ ] Repository cloné
- [ ] Venv créé et activé
- [ ] Requirements installés
- [ ] Fichier `.env` créé et rempli
- [ ] Solde USDT vérifié sur Binance
- [ ] Bot démarré avec succès
- [ ] API accessible sur http://localhost:5000
- [ ] Telegram reçoit les notifications (optionnel)

---

## 📊 Premiers Pas

1. **Jour 1**: Laisse le bot tourner en mode observation
   - Vérifie les logs
   - Assure-toi que les notifications Telegram arrivent

2. **Jour 2-3**: Valide la stratégie
   - Est-ce que les signaux ont du sens?
   - Les Stop Loss/Take Profit fonctionnent?

3. **Jour 4+**: Augmente progressivement les montants
   - Passe de 20 USDT à 50 USDT
   - Puis 100 USDT si confiant

⚠️ **IMPORTANT**: Ne mets jamais TOUTES tes économies sur un bot!

---

## 🆘 Besoin d'Aide?

- 📚 Lire le [README.md](README.md) complet
- 🐛 Vérifier les logs dans `trading_bot.log`
- 💬 Créer une issue GitHub
- 📧 Envoyer un email

---

**Dernière mise à jour**: 01/06/2024
