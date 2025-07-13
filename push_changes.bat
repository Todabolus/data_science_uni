@echo off
REM Push Changes Script für Data Science Projekt (Windows Version)
REM Verwendung: push_changes.bat "commit message"

setlocal enabledelayedexpansion

REM Überprüfe ob Commit-Message angegeben wurde
if "%~1"=="" (
    echo [ERROR] Bitte gebe eine Commit-Message an!
    echo Verwendung: push_changes.bat "Deine Commit-Message"
    exit /b 1
)

set "COMMIT_MESSAGE=%~1"

echo [INFO] Starte automatisierten Commit- und Push-Prozess...
echo Commit Message: %COMMIT_MESSAGE%
echo.

REM Schritt 1: Notebook Outputs clearen
echo [INFO] Schritt 1: Clearing Notebook Outputs...

REM Aktiviere Python Virtual Environment falls vorhanden
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Aktiviere Virtual Environment...
    call venv\Scripts\activate.bat
)

REM Finde alle .ipynb Dateien und cleane sie
echo [INFO] Suche nach Jupyter Notebooks...
for /r %%i in (*.ipynb) do (
    set "notebook=%%i"
    REM Überspringe venv und .git Ordner
    echo !notebook! | findstr /i "venv" >nul
    if errorlevel 1 (
        echo !notebook! | findstr /i ".git" >nul
        if errorlevel 1 (
            echo [INFO] Clearing outputs in: !notebook!
            nbstripout "!notebook!"
            if !errorlevel! equ 0 (
                echo [SUCCESS] Outputs cleared: !notebook!
            ) else (
                echo [WARNING] Fehler beim Clearen von !notebook!
            )
        )
    )
)

echo.

REM Schritt 2: Git Status prüfen
echo [INFO] Schritt 2: Git Status überprüfen...
git status >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Kein Git Repository gefunden!
    exit /b 1
)

REM Schritt 3: Git Add
echo [INFO] Schritt 3: Staging aller Änderungen...
git add .
if errorlevel 1 (
    echo [ERROR] Fehler beim Staging der Dateien
    exit /b 1
) else (
    echo [SUCCESS] Alle Änderungen gestaged
)

REM Schritt 4: Git Commit
echo [INFO] Schritt 4: Erstelle Commit...
git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo [ERROR] Fehler beim Erstellen des Commits
    exit /b 1
) else (
    echo [SUCCESS] Commit erfolgreich erstellt
)

REM Schritt 5: Git Push
echo [INFO] Schritt 5: Push zu Remote Repository...
git push
if errorlevel 1 (
    echo [WARNING] Standard Push fehlgeschlagen, versuche mit upstream...
    for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
    git push --set-upstream origin !CURRENT_BRANCH!
    if errorlevel 1 (
        echo [ERROR] Push fehlgeschlagen. Bitte manuell überprüfen.
        exit /b 1
    ) else (
        echo [SUCCESS] Push mit upstream erfolgreich
    )
) else (
    echo [SUCCESS] Push erfolgreich abgeschlossen
)

echo.
echo [SUCCESS] Alle Schritte erfolgreich abgeschlossen!
echo [INFO] Repository Status nach Push:
git log --oneline -3

endlocal
