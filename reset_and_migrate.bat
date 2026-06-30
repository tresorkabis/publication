@echo off
REM Script pour réinitialiser la base de données et générer les migrations
REM Utilisation : double-clic ou reset_and_migrate.bat

setlocal enabledelayedexpansion

echo ============================================
echo   Réinitialisation ESFORCA - Windows
echo ============================================
echo.

REM 1. Supprimer la base de données SQLite
if exist "db.sqlite3" (
    echo [SUPPRESSION] Base de donnees : db.sqlite3
    del /f /q "db.sqlite3"
    echo [OK] Base de donnees supprimee.
) else (
    echo [INFO] Base de donnees non trouvee : db.sqlite3
)

REM 2. Supprimer les anciennes migrations (sauf __init__.py)
echo.
echo [SUPPRESSION] Anciennes migrations...
if exist "app\migrations" (
    for /f "tokens=*" %%f in ('dir /b "app\migrations\*.py" 2^>nul ^| findstr /v "__init__"') do (
        del /f /q "app\migrations\%%f"
    )
    echo [OK] Anciennes migrations supprimees.
) else (
    echo [INFO] Repertoire des migrations non trouve : app\migrations
)

REM 3. Générer les migrations
echo.
echo [MIGRATIONS] Generation des nouvelles migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la generation des migrations.
    pause
    exit /b 1
)
echo [OK] Migrations generees.

REM 4. Appliquer les migrations
echo.
echo [MIGRATIONS] Application des migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'application des migrations.
    pause
    exit /b 1
)
echo [OK] Migrations appliquees.

REM 5. Générer les données de démonstration
echo.
echo [SEED] Generation des donnees de demonstration...
python manage.py seed_demo_data
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la generation des donnees.
    pause
    exit /b 1
)
echo [OK] Donnees de demonstration generees.

echo.
echo ============================================
echo   REINITIALISATION TERMINEE AVEC SUCCES
echo ============================================
echo.
echo Pour demarrer le serveur : run.bat
echo.
echo === Comptes de demonstration (mot de passe : demo) ===
echo   Super Admin : admin@esforca.cd
echo   Admin       : admin2@esforca.cd
echo   Secretaire  : secretaire@esforca.cd
echo   Chef filiere: chef.inf@esforca.cd
echo   Enseignant  : enseignant.inf1@esforca.cd
echo   Etudiant    : etudiant.inf.1@esforca.cd
echo.

pause