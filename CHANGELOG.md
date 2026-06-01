# 📝 Changelog — MochiBot

## 🚀 v2.1.0 — 01/06/2024

### ✨ Nouvelles Fonctionnalités

#### 🗄️ Base de Données Robuste (SQLite)
- Migration complète vers SQLAlchemy + SQLite
- Modèles ORM pour Positions, Trades, Performance
- Backups automatiques avec timestamps
- Export CSV des trades

#### 📊 Dashboard Web Interactif
- Interface web responsive sur http://localhost:8080
- Monitoring en temps réel des positions
- Historique des trades interactif
- Graphiques de performance
- Rafraîchissement auto toutes les 5 secondes

#### 🎯 Risk Management Avancé
- **Kelly Criterion** pour position sizing dynamique
- Drawdown management avec tracking max drawdown
- Daily loss limits (configuration par %)
- Equity curve monitoring en temps réel
- Alertes automatiques sur limites atteintes

#### 🤖 Stratégies Custom & Backtesting
- Support complet des stratégies custom (*.py)
- Chargement dynamique de stratégies
- **Hot-swap** de stratégie sans redémarrage
- Backtesteur simple intégré
- Exemple stratégie MACD inclus

#### 🔗 Discord Webhooks
- Webhooks Discord pour notifications
- Embeds colorés avec détails
- Alertes de risque (daily loss, drawdown)
- Rapports de performance
- Notifications changement de stratégie

### 🔧 Améliorations Techniques

- **database_sql.py**: ORM SQLAlchemy avec backup/export
- **risk_advanced.py**: Kelly Criterion + Drawdown management
- **strategy_manager.py**: Manager stratégies + backtester
- **discord_webhooks.py**: Intégration Discord complète
- **dashboard.py**: Dashboard web Flask
- **strategies/example_macd.py**: Exemple stratégie custom

### 📚 Documentation Mise à Jour

- Ajout guide stratégies custom
- Documentation Discord webhooks
- Tutoriel dashboard web
- Guide Kelly Criterion

### 🔐 Sécurité

- Validation des stratégies custom
- Paramètres de risque limités
- Gestion sécurisée des webhooks

---

## v2.0.0 — 01/06/2024

### ✅ Fonctionnalités Principales

- Trading automatisé Binance Spot
- Stratégie RSI + EMA Crossover
- Intégration Telegram complète
- API REST Flask
- Persistance JSON des données
- Suite de tests automatisés
- Scripts de démarrage (Windows/Linux)
- Documentation complète

---

## 📊 Comparaison des Versions

| Feature | v1.0 | v2.0 | v2.1 |
|---------|------|------|------|
| Trading Automatisé | ✅ | ✅ | ✅ |
| Telegram | ❌ | ✅ | ✅ |
| API REST | ❌ | ✅ | ✅ |
| Dashboard Web | ❌ | ❌ | ✅ |
| SQLite DB | ❌ | ❌ | ✅ |
| Kelly Criterion | ❌ | ❌ | ✅ |
| Stratégies Custom | ❌ | ❌ | ✅ |
| Discord Webhooks | ❌ | ❌ | ✅ |
| Backtesting | ❌ | ❌ | ✅ |

---

## 🚀 Utilisation v2.1.0

### Dashboard Web
```bash
# Accéder à http://localhost:8080
# Monitoring en temps réel de toutes les métriques
```

### Stratégies Custom
```python
from strategy_manager import strategy_manager

# Charger une stratégie custom
strategy_manager.load_custom_strategy("strategies/ma_strategie.py")
strategy_manager.set_strategy("ma_strategie")

# Lister toutes les stratégies
strategies = strategy_manager.list_strategies()
```

### Backtesting
```python
from strategy_manager import backtester
import pandas as pd

# Charger données
df = ...  # pandas DataFrame

# Faire un backtest
results = backtester.backtest(df, initial_balance=1000, strategy_name="builtin")

print(f"Win Rate: {results['win_rate']:.1f}%")
print(f"Total Return: {results['total_return']:.2f}%")
```

### Risk Management Avancé
```python
from risk_advanced import AdvancedRiskManager

risk = AdvancedRiskManager(initial_balance=1000)

# Calculer position size avec Kelly
kelly_pct = risk.calculate_kelly_criterion(
    win_rate=60.0,  # 60%
    avg_win=1.5,    # Ratio gain/perte
    avg_loss=1.0,
    kelly_fraction=0.25
)

# Vérifier limites de risque
if risk.check_daily_loss_limit(daily_loss_limit_pct=5.0):
    print("Stop: limite perte du jour atteinte")

if risk.check_drawdown_limit(max_drawdown_limit_pct=20.0):
    print("Stop: max drawdown atteint")
```

### Discord Webhooks
```bash
# Ajouter DISCORD_WEBHOOK_URL dans .env

# Les notifications sont envoyées automatiquement:
# - Signaux buy/sell
# - Alertes de risque
# - Rapports de performance
```

---

## 🔄 Migration de v2.0 à v2.1

### Étapes

1. **Sauvegarde**: Copier `trading_data.json` en backup
2. **Update**: `pip install -r requirements.txt` (SQLAlchemy ajouté)
3. **Config**: Ajouter variables v2.1 dans `.env` (optionnel)
4. **Migration**: La DB SQLite est créée auto au démarrage
5. **Redémarrage**: `python bot.py`

### Compatibilité Arrière

✅ Les anciennes positions JSON sont conservées
✅ L'API REST reste identique
✅ Telegram fonctionne sans changement

---

## 🎯 Prochaines Étapes (v2.2+)

- [ ] Email notifications
- [ ] Push notifications mobile
- [ ] Multiple exchange support (Kraken, Coinbase)
- [ ] Futures trading support
- [ ] ML-based signal prediction
- [ ] Auto-parameter optimization
- [ ] Community strategy sharing
- [ ] Paper trading mode

---

## 📞 Support

- 🐛 Issues: GitHub Issues
- 💬 Questions: Créer une discussion
- 📚 Docs: README.md + SETUP.md
- 🤝 Contributions: PRs bienvenues

---

**Dernière mise à jour**: 01/06/2024
**Auteur**: Thomas (MochiBot Team)
