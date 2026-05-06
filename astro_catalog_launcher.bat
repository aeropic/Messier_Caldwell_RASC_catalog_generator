@echo off
:: Se place dans le dossier où se trouve le fichier .bat
cd /d "%~dp0"

echo thumbnails generation with 'astro_catalog_generator.py'
echo =======================================================

:: Lance Python sur le script RASC
"C:\Program Files\Siril\python\python.exe" "astro_catalog_generator.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Le script 'astro_catalog_generator.py' est introuvable dans : %cd%
    echo Verifiez que le nom du fichier est exactement 'astro_catalog_generator.py'
    pause
) else (
    echo Planche mise a jour !
    start astro_catalog.html
	@echo off
    :: echo Le script va se fermer dans 7 secondes...
    timeout /t 7 
    exit
)
