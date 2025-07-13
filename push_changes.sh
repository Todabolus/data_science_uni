#!/bin/bash

# Push Changes Script für Data Science Projekt
# Verwendung: ./push_changes.sh "commit message"
# oder: bash push_changes.sh "commit message"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für Status-Nachrichten
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Überprüfe ob Commit-Message angegeben wurde
if [ $# -eq 0 ]; then
    print_error "Bitte gebe eine Commit-Message an!"
    echo "Verwendung: ./push_changes.sh \"Deine Commit-Message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

print_status "Starte automatisierten Commit- und Push-Prozess..."
echo "📝 Commit Message: $COMMIT_MESSAGE"
echo ""

# Schritt 1: Notebook Outputs clearen
print_status "Schritt 1: Clearing Notebook Outputs..."

# Aktiviere Python Virtual Environment falls vorhanden
if [ -f "venv/bin/activate" ]; then
    print_status "Aktiviere Virtual Environment..."
    source venv/bin/activate
fi

# Finde alle .ipynb Dateien und cleane sie
NOTEBOOKS=$(find . -name "*.ipynb" -not -path "./venv/*" -not -path "./.git/*")

if [ -z "$NOTEBOOKS" ]; then
    print_warning "Keine Jupyter Notebooks gefunden."
else
    print_status "Gefundene Notebooks:"
    echo "$NOTEBOOKS" | sed 's/^/  - /'
    echo ""
    
    # Cleane jedes Notebook
    for notebook in $NOTEBOOKS; do
        print_status "Clearing outputs in: $notebook"
        if command -v nbstripout &> /dev/null; then
            nbstripout "$notebook"
            if [ $? -eq 0 ]; then
                print_success "✓ $notebook outputs cleared"
            else
                print_warning "⚠ Fehler beim Clearen von $notebook"
            fi
        else
            print_error "nbstripout ist nicht installiert!"
            print_status "Installiere nbstripout..."
            pip install nbstripout
            nbstripout "$notebook"
        fi
    done
fi

echo ""

# Schritt 2: Git Status prüfen
print_status "Schritt 2: Git Status überprüfen..."
git status --porcelain > /dev/null 2>&1
if [ $? -ne 0 ]; then
    print_error "Kein Git Repository gefunden!"
    exit 1
fi

# Zeige geänderte Dateien
CHANGED_FILES=$(git status --porcelain)
if [ -z "$CHANGED_FILES" ]; then
    print_warning "Keine Änderungen gefunden. Nichts zu committen."
    exit 0
fi

print_status "Geänderte Dateien:"
echo "$CHANGED_FILES" | sed 's/^/  /'
echo ""

# Schritt 3: Git Add
print_status "Schritt 3: Staging aller Änderungen..."
git add .
if [ $? -eq 0 ]; then
    print_success "✓ Alle Änderungen gestaged"
else
    print_error "✗ Fehler beim Staging der Dateien"
    exit 1
fi

# Schritt 4: Git Commit
print_status "Schritt 4: Erstelle Commit..."
git commit -m "$COMMIT_MESSAGE"
if [ $? -eq 0 ]; then
    print_success "✓ Commit erfolgreich erstellt"
else
    print_error "✗ Fehler beim Erstellen des Commits"
    exit 1
fi

# Schritt 5: Git Push
print_status "Schritt 5: Push zu Remote Repository..."
git push
if [ $? -eq 0 ]; then
    print_success "✓ Push erfolgreich abgeschlossen"
else
    print_error "✗ Fehler beim Push"
    print_status "Versuche git push mit upstream..."
    
    # Versuche den aktuellen Branch zu ermitteln und upstream zu setzen
    CURRENT_BRANCH=$(git branch --show-current)
    git push --set-upstream origin "$CURRENT_BRANCH"
    
    if [ $? -eq 0 ]; then
        print_success "✓ Push mit upstream erfolgreich"
    else
        print_error "✗ Push fehlgeschlagen. Bitte manuell überprüfen."
        exit 1
    fi
fi

echo ""
print_success "🚀 Alle Schritte erfolgreich abgeschlossen!"
print_status "Repository Status nach Push:"
git log --oneline -3
echo ""
print_status "Remote Status:"
git remote -v
