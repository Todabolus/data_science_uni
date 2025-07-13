# Business Understanding – Data Science Projekt

## Projektübersicht

**Projektteam:** Gold Diggers  
**Kontext:** Data Science Grundkurs - Praxisorientierte Anwendung verschiedener Methoden

Das Projekt fokussiert sich auf die Analyse und Prognose von Goldkursbewegungen unter Berücksichtigung von Wirtschaftsnachrichten. Während es sich um ein Lehrprojekt handelt, verfolgen wir das Ziel, realistische und anwendbare Erkenntnisse zu gewinnen, die in der Finanzwelt von praktischem Nutzen sein könnten.

---

## Problemstellung und Motivation

**Kernproblem:** Goldpreis-Volatilität und die Herausforderung der Vorhersage  
**Geschäftsszenario:** Trader, Analysten und Finanzinstitutionen benötigen bessere Werkzeuge zur Einschätzung von Goldkursbewegungen

**Hauptfragestellung:** Können Wirtschaftsnachrichten verschiedener Kategorien dabei helfen, die prozentuale Rendite des Goldkurses zu prognostizieren?

---

## Datengrundlage

**Primärer Datensatz:** Goldkurs (XAUUSD) im 30-Minuten-Takt  
- Zeitraum: Ab 19.06.2012  
- Enthält: Open, High, Low, Close, Volume  
- Fokus: Close-Preise und daraus berechnete Returns

**Sekundärer Datensatz:** Wirtschaftsnachrichten (6 Kategorien)  
- Zeitraum: Ab Januar 2012
- Kategorien: Zentralbanken, Wirtschaftsaktivität, Inflation, Zinssätze, Arbeitsmarkt, Politik
- Merkmale: Zeitstempel, Impact-Level (0-3), Kategorie-Zuordnung

---

## Datenquellen und Kategorisierung

**Strategische Auswahl:** Bewusst keine Kaggle-Datensätze zur Erfüllung der Kursanforderungen

**News-Kategorien mit unterschiedlicher Marktrelevanz:**
1. **Zentralbanken** (central_banks.csv): FED, EZB-Entscheidungen und Statements
2. **Wirtschaftsaktivität** (economic_activity.csv): BIP-Daten, Industrieproduktion
3. **Inflation** (inflation.csv): CPI, PPI und verwandte Kennzahlen
4. **Zinssätze** (interest_rate.csv): Leitzinsentscheidungen und Zinsprognosen
5. **Arbeitsmarkt** (labor_market.csv): Arbeitslosenzahlen, Lohnentwicklung
6. **Politik** (politics.csv): Politische Ereignisse mit Wirtschaftsbezug

**Goldpreis-Daten:** API-basierte historische Intraday-Daten (30-Minuten-Intervall)

---

## Business Objectives

### Primärziel: Rendite-Prognose
**Hauptziel:** Entwicklung eines Regressionsmodells zur Vorhersage der prozentualen Goldkurs-Rendite (Return)

**Methodischer Ansatz:** Verwendung der absoluten Rendite |Return| als Trainingsparameter zur Modellierung der Volatilität, um die tatsächliche prozentuale Rendite besser prognostizieren zu können

**Geschäftswert:**
- Prognose der erwarteten Rendite für Goldtrader
- Automatisierte Handelssignale basierend auf Renditevorhersagen
- Portfolio-Optimierung durch präzise Rendite-Schätzungen

### Sekundärziel: Kategorie-Gewichtung
**Ziel:** Quantifizierung des relativen Einflusses verschiedener News-Kategorien

**Anwendung:**
- Priorisierung von Nachrichtenquellen
- Risiko-Scoring für verschiedene Wirtschaftsereignisse
- Optimierung von Trading-Algorithmen

---

## Business Success Criteria

### Quantitative Kriterien
- **Realistische Modellgüte:** R² > 0.15 für Testdaten (realistisch für Finanzmarkt-Prognosen)
- **Stabilität:** Konsistente Performance über verschiedene Zeiträume
- **Praktikabilität:** Vorhersagen in unter 1 Sekunde generierbar

### Qualitative Kriterien
- **Interpretierbarkeit:** Klare Zuordnung des Einflusses einzelner Kategorien
- **Plausibilität:** Ergebnisse müssen ökonomisch sinnvoll sein
- **Robustheit:** Modell soll auch bei ungewöhnlichen Marktbedingungen funktionieren

---

## Data Mining Goals

### Zielvariable
**Prozentuale Rendite (Return):** Prognose der erwarteten Kursbewegung in Prozent
- Hauptziel: Vorhersage der tatsächlichen Rendite
- Trainingsansatz: Verwendung der absoluten Rendite |Return| als Volatilitäts-Indikator
- Praxisrelevanz: Direkte Anwendung für Handelsentscheidungen

### Prädiktoren
**Hauptfeatures:**
- Kategorien-spezifische Impact-Summen
- Kategorien-spezifische Maximum-Impacts
- Verschobenes Handelsvolumen (Lag-1)
- Kategorie-spezifische Gewichtungen

**Abgeleitete Features:**
- Gewichteter Kategorie-Score
- Interaktionsterme zwischen Kategorien
- Zeitbasierte Merkmale (Uhrzeit-Filterung)

---

## Data Mining Success Criteria

### Statistische Güte
- **R² (Test):** > 0.10 (angemessen für Finanzmarkt-Prognosen)
- **Interpretierbarkeit:** Nachvollziehbare Koeffizienten-Vorzeichen
- **Kategorien-Ranking:** Plausible Gewichtungsreihenfolge

### Modell-Robustheit
- **Chronologische Validierung:** Performance auf zeitlich späteren Daten
- **Residualanalyse:** Keine systematischen Muster in Residuen
- **Gewichtungseffekt:** Verbesserung durch kategorie-spezifische Gewichtung

### Praktische Anwendbarkeit
- **Echtzeitfähigkeit:** Vorhersage innerhalb von Sekunden
- **Interpretierbarkeit:** Nachvollziehbare Koeffizienten
- **Skalierbarkeit:** Erweiterbar auf andere Edelmetalle oder Märkte

---

## Methodischer Ansatz

### 1. Datenaufbereitung
- **Zeitstempel-Synchronisation:** Chartdaten und News-Events
- **Feature Engineering:** Kategorie-spezifische Aggregate (Summe, Maximum, Anzahl)
- **Zeitfilterung:** Fokus auf nachrichtenreiche Uhrzeiten (13:30, 15:00, 19:00)

### 2. Modellierungsansatz
- **Baseline-Modell:** Einfache Multiple Lineare Regression
- **Erweiterte Modelle:** Gewichtete Regression basierend auf Kategorien-Performance
- **Validierung:** Chronologische 20/80-Aufteilung (Training/Test)

### 3. Gewichtungsstrategie
- **Empirische Basis:** Statistische Analyse der historischen Performance
- **Skalierung:** Lineare Transformation auf [-100, +100] Skala
- **Adaptive Gewichtung:** Kategorien-spezifische Gewichtung basierend auf Baseline-Abweichung

---

## Erwartete Herausforderungen

### Datenqualität
- **Zeitstempel-Synchronisation:** Exakte Zuordnung von News zu Kursbewegungen
- **Missing Values:** Umgang mit fehlenden Handelsdaten
- **Outlier-Behandlung:** Extreme Marktbewegungen bei Krisenereignissen

### Modellierung
- **Schwache Signale:** Finanzmarkt-Rauschen überwinden
- **Multikollinearität:** Korrelierte News-Kategorien
- **Zeitliche Instabilität:** Sich ändernde Marktdynamiken

### Validierung
- **Chronologische Abhängigkeit:** Keine zufällige Train/Test-Aufteilung möglich
- **Regime-Wechsel:** Verschiedene Marktphasen berücksichtigen
- **Externe Validität:** Generalisierbarkeit auf andere Zeiträume

---

## Ausblick und Erweiterungsmöglichkeiten

### Kurzfristige Verbesserungen
- **Regularisierung:** Ridge/Lasso Regression zur Overfitting-Reduktion
- **Ensemble-Methoden:** Kombination verschiedener Modelle
- **Erweiterte Gewichtung:** Dynamische Anpassung basierend auf Marktsituation

### Langfristige Entwicklungen
- **Machine Learning:** Random Forest, XGBoost für non-lineare Zusammenhänge
- **Deep Learning:** LSTM für zeitliche Abhängigkeiten
- **NLP-Integration:** Sentiment-Analyse der News-Texte
