@echo off
setlocal

:: =========================================================================
:: Configuration ZAP Scanner
:: Definissez votre cle API ZAP ici ou via la variable d'environnement ZAP_API_KEY
:: =========================================================================
if "%ZAP_API_KEY%"=="" (
    set ZAP_API_KEY=YOUR_ZAP_API_KEY
)

if "%ZAP_PORT%"=="" (
    set ZAP_PORT=8080
)

if "%ZAP_PATH%"=="" (
    set ZAP_PATH=%ProgramFiles%\ZAP\Zed Attack Proxy\ZAP.exe
)

echo ===================================================
echo   Demarrage d'OWASP ZAP en mode daemon
echo ===================================================
echo Port      : %ZAP_PORT%
echo Chemin ZAP: %ZAP_PATH%
echo.

if not exist "%ZAP_PATH%" (
    echo [ERREUR] L'executable ZAP est introuvable a l'emplacement :
    echo "%ZAP_PATH%"
    echo.
    echo Veuillez installer OWASP ZAP ou definir la variable ZAP_PATH.
    pause
    exit /b 1
)

start "" "%ZAP_PATH%" ^
  -daemon ^
  -port %ZAP_PORT% ^
  -config api.key=%ZAP_API_KEY%

echo ZAP est en cours de demarrage...
echo Veuillez patienter 20 a 30 secondes avant de lancer l'interface web (python app.py).
pause