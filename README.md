# 📈 Data Science Projekt: Goldkurs-Prognose mit Wirtschaftsnachrichten

> **Projektteam:** Gold Diggers  
> **Kontext:** Data Science Grundkurs - Praxisorientierte Anwendung verschiedener Methoden

## 🎯 Projektübersicht

Dieses Projekt fokussiert sich auf die **Analyse und Prognose von Goldkursbewegungen** unter Berücksichtigung von Wirtschaftsnachrichten. Ziel ist es, ein Regressionsmodell zu entwickeln, das die prozentuale Rendite des Goldkurses basierend auf verschiedenen Kategorien von Wirtschaftsnachrichten vorhersagen kann.

### 🔍 Hauptfragestellung

**Können Wirtschaftsnachrichten verschiedener Kategorien dabei helfen, die prozentuale Rendite des Goldkurses zu prognostizieren?**

### 🎯 Geschäftswert

-   Prognose der erwarteten Rendite für Goldtrader
-   Automatisierte Handelssignale basierend auf Renditevorhersagen
-   Portfolio-Optimierung durch präzise Rendite-Schätzungen
-   Quantifizierung des relativen Einflusses verschiedener News-Kategorien

## 📊 Datengrundlage

### Primärer Datensatz: Goldkurs (XAUUSD)

-   **Zeitraum:** Ab 19.06.2012
-   **Frequenz:** 30-Minuten-Takt
-   **Enthält:** Open, High, Low, Close, Volume
-   **Fokus:** Close-Preise und daraus berechnete Returns

### Sekundärer Datensatz: Wirtschaftsnachrichten

-   **Zeitraum:** Ab Januar 2012
-   **6 strategisch ausgewählte Kategorien:**
    1. **Zentralbanken** (`central_banks.csv`): FED, EZB-Entscheidungen und Statements
    2. **Wirtschaftsaktivität** (`economic_activity.csv`): BIP-Daten, Industrieproduktion
    3. **Inflation** (`inflation.csv`): CPI, PPI und verwandte Kennzahlen
    4. **Zinssätze** (`interest_rate.csv`): Leitzinsentscheidungen und Zinsprognosen
    5. **Arbeitsmarkt** (`labor_market.csv`): Arbeitslosenzahlen, Lohnentwicklung
    6. **Politik** (`politics.csv`): Politische Ereignisse mit Wirtschaftsbezug
-   **Merkmale:** Zeitstempel, Impact-Level (0-3), Kategorie-Zuordnung

## 📁 Projektstruktur

```
📦 data_science/
├── 📓 01_data_preparation.ipynb    # Datenaufbereitung und -synchronisation
├── 📓 02_eda.ipynb                 # Explorative Datenanalyse
├── 📓 03_modeling.ipynb            # Modellierung und Evaluation
├── 📄 business_understanding.md    # Detaillierte Problemanalyse
├── 📄 data_description.md          # Datenbeschreibung und -quellen
├── 📄 requirements.txt             # Python-Abhängigkeiten
├── 📄 README.md                    # Diese Datei
├── 📁 data/
│   ├── 📁 raw/                     # Rohdaten
│   │   ├── 📁 chart/               # Goldkurs-Daten
│   │   └── 📁 news/                # Wirtschaftsnachrichten (6 Kategorien)
│   └── 📁 merged/                  # Aufbereitete, zusammengeführte Daten
├── 📁 utils/                       # Hilfsfunktionen und Module
│   ├── 🐍 data_prep_utils.py       # Datenaufbereitungs-Utilities
│   ├── 📁 eda/
│   │   ├──📁 significance/         # ttest, ANOVA & Chi^2
│   │   │  ├── 🐍 bootstrap.py
│   │   │  ├── 🐍 tests.py
│   │   │  └── 🐍 wrapper.py
│   │   ├── 🐍 calculate.py
│   │   └── 🐍 plots.py            
│   └── 📁 modeling/                # Regression & Klassifikation
│        ├── 🐍 evaluation.py 
│        └── 🐍 models.py
└── 🔧 push_changes.*               # Automatisierte Git-Skripte
```

## 🛠️ Installation und Setup

### 1. Repository klonen

```bash
git clone <repository-url>
cd data_science
```

### 2. Virtuelle Umgebung erstellen

```bash
python -m venv venv
```

**⚠️ Wichtig:** Als Name für die virtuelle Umgebung sollte `venv` genutzt werden, da wir den generierten Ordner in der `.gitignore` ausschließen.

### 3. Virtuelle Umgebung aktivieren

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 📋 Betriebssystem-spezifische Abhängigkeiten

Die `requirements.txt` enthält **plattformspezifische Bedingungen** für optimale Kompatibilität:

```python
# Windows-spezifische Pakete (werden nur unter Windows installiert)
pywin32>=305,<310; sys_platform == "win32"
pywinpty==2.0.15; sys_platform == "win32"
```

Diese Pakete werden automatisch nur unter Windows installiert und unter Linux/macOS übersprungen.

## 🚀 Verwendung

### Jupyter Notebooks ausführen

```bash
# Virtuelle Umgebung aktivieren (falls noch nicht aktiv)
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate     # Windows

# Jupyter Lab starten
jupyter lab
```

### Workflow

1. **📓 01_data_preparation.ipynb** - Datenaufbereitung und Synchronisation
2. **📓 02_eda.ipynb** - Explorative Datenanalyse und Visualisierungen
3. **📓 03_modeling.ipynb** - Modellentwicklung und Evaluation

## 🔧 Push Changes Skripte

Für effizientes Arbeiten stehen **automatisierte Git-Skripte** zur Verfügung, die folgende Schritte automatisch ausführen:

1. **🧹 Notebook Outputs clearen** (mit `nbstripout`)
2. **📊 Git Status prüfen**
3. **➕ Git Add** (alle Änderungen)
4. **💾 Git Commit** (mit angegebener Message)
5. **🚀 Git Push** (zum Remote Repository)

### Verwendung:

```bash
# Linux/macOS
chmod +x push_changes.sh
./push_changes.sh "Deine Commit-Message"

# Windows
push_changes.bat "Deine Commit-Message"
```

**Beispiele:**

```bash
./push_changes.sh "Feature: Neue Datenanalyse hinzugefügt"
./push_changes.sh "Fix: Fehler in Datenvorbereitung behoben"
./push_changes.sh "Update: EDA erweitert"
```

Weitere Details finden Sie in [`PUSH_SCRIPTS_README.md`](PUSH_SCRIPTS_README.md).

## 🎯 Methodischer Ansatz

### Modellierungsziel

-   **Zielvariable:** Prozentuale Rendite (Return) des Goldkurses
-   **Trainingsansatz:** Verwendung der absoluten Rendite |Return| als Volatilitäts-Indikator
-   **Prädiktoren:** Kategorien-spezifische Impact-Summen, Maximum-Impacts, Handelsvolumen

### Erfolgsmetriken

-   **Statistische Güte:** R² > 0.15 für Testdaten (realistisch für Finanzmarkt-Prognosen)
-   **Interpretierbarkeit:** Nachvollziehbare Koeffizienten-Vorzeichen
-   **Praktikabilität:** Vorhersagen in unter 1 Sekunde generierbar

## 📈 Erwartete Herausforderungen

-   **Zeitstempel-Synchronisation:** Exakte Zuordnung von News zu Kursbewegungen
-   **Schwache Signale:** Finanzmarkt-Rauschen überwinden
-   **Chronologische Validierung:** Keine zufällige Train/Test-Aufteilung möglich

---

_Für detaillierte Informationen zur Problemstellung und den Business Objectives, siehe [`business_understanding.md`](business_understanding.md)._
