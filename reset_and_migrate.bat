@echo off
REM Script pour réinitialiser la base de données et générer les migrations
REM Utilisation : double-clic ou reset_and_migrate.bat
setlocal enabledelayedexpansion

echo ============================================
echo   Reinitialisation ESFORCA - Windows
echo ============================================
echo.

REM 1. Supprimer la base de données SQLite
if exist "db.sqlite3" (
    echo [INFO] Suppression de la base de donnees : db.sqlite3
    del /f /q "db.sqlite3"
    echo [OK] Base de donnees supprimee avec succes.
) else (
    echo [INFO] Base de donnees db.sqlite3 non trouvee.
)

REM 2. Supprimer les anciennes migrations (sauf __init__.py)
echo.
echo [INFO] Suppression des anciennes migrations...
if exist "app\migrations" (
    for /f "tokens=*" %%f in ('dir /b "app\migrations\*.py" 2^>nul ^| findstr /v "__init__"') do (
        del /f /q "app\migrations\%%f"
    )
    echo [OK] Anciennes migrations supprimees.
) else (
    echo [INFO] Repertoire des migrations non trouve.
)

REM 3. Générer les migrations
echo.
echo [ACTION] Generation des nouvelles migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la generation des migrations.
    pause
    exit /b 1
)

REM 4. Appliquer les migrations
echo.
echo [ACTION] Application des migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'application des migrations.
    pause
    exit /b 1
)

REM 5. Générer les données de démonstration
echo.
echo [ACTION] Generation des donnees de demonstration...
python manage.py seed_demo_data
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la generation des donnees.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   REINITIALISATION TERMINEE AVEC SUCCES !
echo ============================================
echo.
echo Pour demarrer le serveur : run.bat
echo.
echo === Comptes de demonstration (mot de passe : demo) ===
echo   - Super Admin : admin
echo   - Admin       : admin2
echo   - President   : president
echo   - Secretaire  : secretaire
echo   - Chef Filiere: chef_gl, chef_rtm, ...
echo   - Enseignant  : ens_gl1, ens_rtm1, ...
echo   - Etudiant    : etud_gl_1, etud_rtm_1, ...
echo.

pause