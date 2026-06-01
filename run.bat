@echo off
REM ========================================
REM MochiBot — Script de démarrage Windows
REM ========================================

echo.
echo ============================================================
echo  🤖 MochiBot — Bot de Trading Automatisé pour Binance
echo ============================================================
echo.

REM Vérifier si venv existe
if not exist "venv" (
    echo ⚠️  Environnement virtuel non trouvé.
    echo    Création de l'environnement virtuel...
    python -m venv venv
    echo    ✅ Environnement créé
    echo.
)

REM Activer venv
call venv\Scripts\activate.bat

REM Vérifier requirements
echo ⏳ Vérification des dépendances...
pip install -q -r requirements.txt

REM Vérifier .env
if not exist ".env" (
    echo.
    echo ❌ Fichier .env non trouvé!
    echo.
    echo    Créé depuis .env.example:
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Édite le fichier .env avec tes clés API Binance
    echo    avant de redémarrer le bot.
    echo.
    pause
    exit /b 1
)

REM Démarrer le bot
echo.
echo ✅ Démarrage du bot...
echo.
python bot.py

REM Si le bot crash, affiche l'erreur
if %errorlevel% neq 0 (
    echo.
    echo ❌ Le bot s'est arrêté avec une erreur.
    echo    Appuie sur une touche pour fermer...
    pause
    exit /b %errorlevel%
)

pause
