# Push Changes Scripts

Automatisierte Skripte für das Clearen von Notebook-Outputs und Git-Operations.

## 📋 Was machen die Skripte?

Die Skripte führen automatisch folgende Schritte aus:

1. **🧹 Notebook Outputs clearen**: Alle `.ipynb` Dateien werden mit `nbstripout` bereinigt
2. **📊 Git Status prüfen**: Überprüfung auf Änderungen im Repository
3. **➕ Git Add**: Staging aller geänderten Dateien
4. **💾 Git Commit**: Commit mit der angegebenen Message
5. **🚀 Git Push**: Push zum Remote Repository

## 🔧 Verwendung

### Linux/macOS (Bash)

```bash
# Skript ausführbar machen (einmalig)
chmod +x push_changes.sh

# Verwendung
./push_changes.sh "Deine Commit-Message"

# Beispiele
./push_changes.sh "Feature: Neue Datenanalyse hinzugefügt"
./push_changes.sh "Fix: Fehler in Datenvorbereitung behoben"
./push_changes.sh "Update: EDA erweitert"
```

### Windows (Batch)

```cmd
# Verwendung
push_changes.bat "Deine Commit-Message"

# Beispiele
push_changes.bat "Feature: Neue Datenanalyse hinzugefügt"
push_changes.bat "Fix: Fehler in Datenvorbereitung behoben"
push_changes.bat "Update: EDA erweitert"
```

## ⚙️ Voraussetzungen

-   **Git Repository**: Das Verzeichnis muss ein Git Repository sein
-   **nbstripout**: Wird automatisch installiert falls nicht vorhanden
-   **Python Virtual Environment**: Wird automatisch aktiviert falls vorhanden (`venv/`)

## 🎨 Features

-   ✅ **Automatisches Notebook-Cleaning**: Entfernt alle Outputs vor dem Commit
-   ✅ **Farbige Ausgabe**: Übersichtliche Status-Nachrichten (Linux/macOS)
-   ✅ **Error Handling**: Behandelt häufige Git-Probleme (z.B. upstream setzen)
-   ✅ **Virtual Environment Support**: Aktiviert automatisch venv falls vorhanden
-   ✅ **Cross-Platform**: Funktioniert auf Linux, macOS und Windows
-   ✅ **Smart File Detection**: Ignoriert venv und .git Ordner

## 📁 Verarbeitete Dateitypen

-   **Jupyter Notebooks** (`.ipynb`): Outputs werden gecleart
-   **Alle anderen Dateien**: Werden normal zum Git hinzugefügt

## 🔍 Beispiel-Output

```
[INFO] Starte automatisierten Commit- und Push-Prozess...
📝 Commit Message: Update: Datenvorbereitung optimiert

[INFO] Schritt 1: Clearing Notebook Outputs...
[INFO] Aktiviere Virtual Environment...
[INFO] Gefundene Notebooks:
  - ./01_data_preparation.ipynb
  - ./02_eda.ipynb
  - ./03_modeling.ipynb

[SUCCESS] ✓ ./01_data_preparation.ipynb outputs cleared
[SUCCESS] ✓ ./02_eda.ipynb outputs cleared
[SUCCESS] ✓ ./03_modeling.ipynb outputs cleared

[INFO] Schritt 2: Git Status überprüfen...
[INFO] Geänderte Dateien:
   M 01_data_preparation.ipynb
   M requirements.txt
  ?? push_changes.sh

[INFO] Schritt 3: Staging aller Änderungen...
[SUCCESS] ✓ Alle Änderungen gestaged

[INFO] Schritt 4: Erstelle Commit...
[SUCCESS] ✓ Commit erfolgreich erstellt

[INFO] Schritt 5: Push zu Remote Repository...
[SUCCESS] ✓ Push erfolgreich abgeschlossen

🚀 Alle Schritte erfolgreich abgeschlossen!
```

## 🛠 Troubleshooting

### Problem: "nbstripout nicht gefunden"

**Lösung**: Das Skript installiert nbstripout automatisch, aber du kannst es auch manuell installieren:

```bash
pip install nbstripout
```

### Problem: "Kein Git Repository gefunden"

**Lösung**: Initialisiere ein Git Repository:

```bash
git init
git remote add origin <your-repo-url>
```

### Problem: "Push fehlgeschlagen"

**Lösung**: Das Skript versucht automatisch upstream zu setzen. Falls das nicht funktioniert:

```bash
git push --set-upstream origin main
```

