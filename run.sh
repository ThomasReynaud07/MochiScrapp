#!/bin/bash

# ========================================
# MochiBot — Script de démarrage macOS/Linux
# ========================================

echo ""
echo "============================================================"
echo "  🤖 MochiBot — Bot de Trading Automatisé pour Binance"
echo "============================================================"
echo ""

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé."
    echo "    Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "    ✅ Environnement créé"
    echo ""
fi

# Activer venv
source venv/bin/activate

# Vérifier requirements
echo "⏳ Vérification des dépendances..."
pip install -q -r requirements.txt

# Vérifier .env
if [ ! -f ".env" ]; then
    echo ""
    echo "❌ Fichier .env non trouvé!"
    echo ""
    echo "    Créé depuis .env.example:"
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Édite le fichier .env avec tes clés API Binance"
    echo "    avant de redémarrer le bot."
    echo ""
    exit 1
fi

# Démarrer le bot
echo ""
echo "✅ Démarrage du bot..."
echo ""
python bot.py

# Si le bot crash, affiche le code erreur
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Le bot s'est arrêté avec une erreur."
    exit 1
fi
