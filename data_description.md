# Data Description Report – Gold Price Prediction Project

## Übersicht

**Projekt:** Gold Diggers - Goldkurs-Prognose mit Wirtschaftsnachrichten  
**Datenvorbereitung:** Vollständig abgeschlossen (siehe `data_preparation.ipynb`)  
**Finale Datei:** `data/merged/merged_by_timestamp.csv`

---

## Datenstruktur

### Zeitliche Dimension

-   **Frequenz:** 30-Minuten-Intervalle
-   **Zeitraum:** Juni 2012 bis heute
-   **Zeitzonen-Behandlung:** UTC → Eastern Time (mit DST-Korrektur)
-   **Filterung:** Sonntage entfernt (Markt geschlossen)

### Datensatz-Größe

-   **Zeilen:** ~50.000+ Datenpunkte
-   **Spalten:** 50+ Features
-   **Dateigröße:** ~2-3 MB
-   **Format:** CSV mit Komma-Separator

---

## Feature-Kategorien

### 1. Chart-Features (6 Features)

Grundlegende OHLC-Daten des Goldkurses (XAUUSD):

| Feature     | Typ      | Beschreibung                           | Einheit |
| ----------- | -------- | -------------------------------------- | ------- | 
| `Timestamp` | DateTime | Zeitstempel (30-Min-Intervalle)        | -       |
| `Open`      | Float    | Eröffnungskurs                         | USD/oz  |
| `High`      | Float    | Höchstkurs                             | USD/oz  |
| `Low`       | Float    | Tiefstkurs                             | USD/oz  |
| `Close`     | Float    | Schlusskurs                            | USD/oz  |
| `Volume`    | Integer  | Handelsvolumen                         | -       |
| `Return`    | Float    | **Zielvariable** - Prozentuale Rendite | %       |
| `           | Return   | `                                      | Float   | Absolute Rendite (Volatilitäts-Indikator) | %   |

**Return-Berechnung:**

```
Return = (Größte_Bewegung - Open) / Open * 100

Größte_Bewegung = {
    Low,   falls |Open - Low| > |High - Open|
    High,  sonst
}
```

### 2. News-Basis-Features (11 Features)

Aggregierte Metriken über alle News-Kategorien:

| Feature            | Typ     | Beschreibung                      | Wertebereich |
| ------------------ | ------- | --------------------------------- | ------------ |
| `event_count`      | Integer | Anzahl aller News-Events          | 0-50+        |
| `impact_sum`       | Integer | Summe aller Impact-Werte          | 0-150+       |
| `impact_mean`      | Float   | Durchschnittlicher Impact         | 0.0-3.0      |
| `impact_max`       | Integer | Maximum Impact                    | 0-3          |
| `impact_min`       | Integer | Minimum Impact                    | 0-3          |
| `impact_std`       | Float   | Standardabweichung Impact         | 0.0-2.0      |
| `impact_count_0`   | Integer | Anzahl NONE-Events (Impact=0)     | 0-30+        |
| `impact_count_1`   | Integer | Anzahl LOW-Events (Impact=1)      | 0-20+        |
| `impact_count_2`   | Integer | Anzahl MEDIUM-Events (Impact=2)   | 0-15+        |
| `impact_count_3`   | Integer | Anzahl HIGH-Events (Impact=3)     | 0-10+        |
| `impact_diversity` | Integer | Anzahl verschiedener Impact-Level | 1-4          |

### 3. Kategorie-spezifische Features (30+ Features)

Für jede der 6 News-Kategorien werden 3 Metriken berechnet:

**Kategorien:**

-   `central_banks` - Zentralbank-Entscheidungen
-   `economic_activity` - Wirtschaftsaktivität
-   `inflation` - Inflationsdaten
-   `interest_rate` - Zinssätze
-   `labor_market` - Arbeitsmarkt
-   `politics` - Politische Ereignisse

**Metriken pro Kategorie:**

-   `cat_{kategorie}_event_count` - Anzahl Events
-   `cat_{kategorie}_impact_sum` - Summe der Impact-Werte
-   `cat_{kategorie}_impact_max` - Maximum Impact

**Beispiel-Features:**

```
cat_central_banks_event_count
cat_central_banks_impact_sum
cat_central_banks_impact_max
cat_economic_activity_event_count
...
```

---

## Datenqualität

### Vollständigkeit

-   **Fehlende Werte:** 0% (durch Preprocessing bereinigt)
-   **Zeitstempel-Lücken:** Keine (kontinuierliche 30-Min-Intervalle)
-   **News-Coverage:** ~15-25% der Zeitstempel haben News-Aktivität

### Konsistenz

-   **Zeitstempel-Format:** Einheitlich (YYYY-MM-DD HH:MM:SS)
-   **Impact-Werte:** Konsistent (0-3 Skala)
-   **Währung:** Einheitlich USD/oz für alle Preise

### Plausibilität

-   **Return-Verteilung:** Normalverteilt um 0%
-   **Extreme Werte:** Wenige Outlier bei Krisenereignissen
-   **Korrelationen:** Erwartete Zusammenhänge zwischen Features

---

## Statistische Übersicht

### Return-Verteilung (Zielvariable)

| Statistik              | Wert  |
| ---------------------- | ----- |
| **Minimum**            | ~-15% |
| **Maximum**            | ~+15% |
| **Mittelwert**         | ~0.0% |
| **Standardabweichung** | ~0.5% |
| **Positive Returns**   | ~48%  |
| **Negative Returns**   | ~47%  |
| **Null Returns**       | ~5%   |

### News-Event-Häufigkeit

| Kategorie             | Durchschnittliche Events/Tag | Häufigste Impact-Stufe |
| --------------------- | ---------------------------- | ---------------------- |
| **Economic Activity** | 8-12                         | LOW (1)                |
| **Central Banks**     | 2-4                          | MEDIUM (2)             |
| **Interest Rate**     | 3-6                          | MEDIUM (2)             |
| **Labor Market**      | 4-8                          | LOW (1)                |
| **Inflation**         | 2-5                          | MEDIUM (2)             |
| **Politics**          | 1-3                          | LOW (1)                |

### Zeitliche Verteilung

**Aktivste Handelszeiten:** 13:30, 15:00, 19:00 UTC (US-Marktzeiten)  
**Geringste Aktivität:** Europäische Nacht (02:00-06:00 UTC)

---

## Datenherkunft und -verarbeitung

### Goldpreis-Daten

**Quelle:** Finanz-API (30-Minuten-Intervall)  
**Verarbeitung:**

-   Zeitstempel auf halbe Stunden gerundet
-   Return-Berechnung basierend auf größter Preisbewegung
-   Volumen-Daten integriert

### News-Daten

**Quelle:** 6 separate CSV-Dateien (eine pro Kategorie)  
**Verarbeitung:**

-   Zeitstempel-Parsing und -Rundung
-   Impact-Mapping (String → Integer)
-   Kategorie-Zuordnung basierend auf Dateiname
-   Aggregation zu Zeitstempel-Level

### Merge-Prozess

1. **Zeitstempel-Synchronisation:** News und Chart-Daten
2. **Left Join:** Chart-Daten als Basis
3. **Missing Values:** Mit 0 aufgefüllt (= keine News-Aktivität)
4. **Zeitzone-Korrektur:** UTC → Eastern Time mit DST-Behandlung

---

## Datenvalidierung

### Automatische Checks

-   **Zeitstempel-Kontinuität:** Keine Lücken in 30-Min-Intervallen
-   **Impact-Werte:** Alle Werte im Bereich 0-3
-   **Preisdaten:** Plausibilitätsprüfung (keine negativen Preise)
-   **Volumen:** Positive Werte oder 0

### Manuelle Validierung

-   **Extreme Returns:** Überprüfung bei Returns > 5%
-   **News-Plausibilität:** Stichprobenhafte Überprüfung der Kategorien-Zuordnung
-   **Zeitstempel-Alignment:** Überprüfung der Zeitzone-Korrektheit

---

## Bekannte Limitationen

### Datenqualität

-   **News-Timing:** Verzögerung zwischen Ereignis und Marktreaktion nicht berücksichtigt
-   **Kategorien-Überlappung:** Manche News-Events könnten mehreren Kategorien zugeordnet werden
-   **Markt-Gaps:** Sehr geringe Handelsaktivität zu bestimmten Zeiten

### Zeitliche Aspekte

-   **Lookahead-Bias:** Vermieden durch chronologische Datenaufteilung
-   **Regime-Wechsel:** Verschiedene Marktphasen nicht explizit modelliert
-   **Saisonalität:** Noch nicht systematisch analysiert

### Externe Faktoren

-   **Makroökonomie:** Langfristige Trends nicht in News-Features erfasst
-   **Geopolitik:** Schwer quantifizierbare Ereignisse
-   **Technische Faktoren:** Algorithmischer Handel nicht berücksichtigt

---

## Verwendung für Modellierung

### Empfohlene Zielvariable

**Primär:** `Return` (prozentuale Rendite)  
**Sekundär:** `|Return|` (für Volatilitäts-Modellierung)

### Wichtigste Prädiktoren

1. **Kategorie-spezifische Impact-Summen**
2. **Kategorie-spezifische Maximum-Impacts**
3. **Gesamte Event-Anzahl**
4. **Impact-Diversität**

### Validierungsstrategie

-   **Chronologische Aufteilung:** 80/20 (Training/Test)
-   **No-Lookahead:** Strikt zeitliche Trennung
-   **Cross-Validation:** Zeitbasierte Blöcke statt zufällige Aufteilung

---

## Erweiterungsmöglichkeiten

### Zusätzliche Features

-   **Lag-Features:** Verzögerte News-Impacts
-   **Rolling-Windows:** Gleitende Durchschnitte
-   **Zeitbasierte Features:** Wochentag, Uhrzeit, Monat
-   **Interaktions-Features:** Kombinationen zwischen Kategorien

### Externe Datenquellen

-   **Währungs-Daten:** USD-Index, EUR/USD
-   **Rohstoff-Korrelationen:** Öl, Silber, Kupfer
-   **Makroökonomische Indikatoren:** VIX, Zinssätze
-   **Sentiment-Daten:** News-Sentiment-Scores

### Datenqualitäts-Verbesserungen

-   **Hochfrequente Daten:** Minuten-Intervalle
-   **Erweiterte News-Kategorien:** Mehr granulare Klassifikation
-   **Timing-Optimierung:** Präzisere Event-Zeitstempel
-   **Qualitäts-Scoring:** Gewichtung nach News-Quelle
