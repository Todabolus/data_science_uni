"""
Data Preparation Utilities

This module contains utility functions for data preparation and processing
used in the data science project.

Functions:
    - load_and_process_news_data: Load and unify news CSV files
    - round_up_to_next_half_hour: Round timestamps to next half hour
    - aggregate_news_data: Create base and category-specific aggregations
    - analyze_column_quality: Analyze data quality and identify null columns
    - process_chart_data: Load and process OHLC chart data
    - merge_and_finalize_data: Merge datasets and apply final processing
"""

import os
import glob
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import pytz
from IPython.display import display, Markdown


def load_and_process_news_data(
    csv_folder: str, 
    impact_mapping: Dict[str, int],
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and process news CSV files from a folder.
    
    Args:
        csv_folder: Path to folder containing news CSV files
        impact_mapping: Dictionary mapping impact strings to integers
        verbose: Whether to print processing information
    
    Returns:
        Tuple of (processed_dataframe, processing_statistics)
    """
    # Scan CSV files
    csv_files = glob.glob(os.path.join(csv_folder, "*.csv"))
    
    if verbose:
        print(f"Found CSV files: {len(csv_files)}")
        for file in csv_files:
            print(f"{os.path.basename(file)}")
    
    combined_data: List[pd.DataFrame] = []
    processing_info = []
    
    # Process each CSV file
    for file_path in csv_files:
        # Extract category from filename
        category = os.path.splitext(os.path.basename(file_path))[0]
        
        # Load and process CSV
        df = pd.read_csv(file_path)
        original_rows = len(df)
        
        # Convert timestamp (Format: MM/DD/YYYY HH:MM:SS)
        df["Timestamp"] = pd.to_datetime(df["Start"], format="%m/%d/%Y %H:%M:%S")
        
        # Add category and convert impact
        df["Category"] = category
        df["Impact"] = df["Impact"].map(impact_mapping)
        
        # Keep relevant columns
        processed_df = df[["Timestamp", "Category", "Impact"]].copy()
        combined_data.append(processed_df)
        
        # Collect processing statistics
        processing_info.append({
            'Kategorie': category,
            'Ursprüngliche Zeilen': original_rows,
            'Verarbeitete Zeilen': len(processed_df),
            'Eindeutige Timestamps': processed_df['Timestamp'].nunique()
        })
    
    # Merge all dataframes
    if verbose:
        print("\nMerging DataFrames...")
    
    final_df = pd.concat(combined_data, ignore_index=True)
    final_df.sort_values("Timestamp", inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    
    # Create statistics dataframe
    stats_df = pd.DataFrame(processing_info)
    
    if verbose:
        print(f"\nSuccessfully processed:")
        print(f"   Total records: {len(final_df):,}")
        print(f"   Period: {final_df['Timestamp'].min()} to {final_df['Timestamp'].max()}")
        print(f"   Categories: {final_df['Category'].nunique()}")
    
    return final_df, stats_df


def round_up_to_next_half_hour(timestamp: pd.Timestamp) -> pd.Timestamp:
    """
    Round timestamp up to the next half hour.
    
    Args:
        timestamp: Input timestamp
        
    Returns:
        Rounded timestamp
    """
    ts = pd.to_datetime(timestamp)
    minute = ts.minute
    second = ts.second
    microsecond = ts.microsecond
    
    # Already exactly on half hour or full hour
    if (minute == 0 or minute == 30) and second == 0 and microsecond == 0:
        return ts
    
    # Round up to next half hour
    if minute < 30:
        return ts.replace(minute=30, second=0, microsecond=0)
    else:
        # Round up to next full hour
        return ts.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=1)


def aggregate_news_data(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Aggregate news data by timestamp with base and category-specific metrics.
    
    Args:
        df: DataFrame with Timestamp, Category, and Impact columns
        verbose: Whether to print processing information
    
    Returns:
        Aggregated DataFrame with all metrics
    """
    # Apply timestamp rounding
    if verbose:
        print("Runde Zeitstempel auf halbe Stunden...")
    
    original_timestamps = df["Timestamp"].copy()
    df["Timestamp"] = df["Timestamp"].apply(round_up_to_next_half_hour)
    
    if verbose:
        print(f"   Ursprüngliche einzigartige Timestamps: {original_timestamps.nunique():,}")
        print(f"   Gerundete einzigartige Timestamps: {df['Timestamp'].nunique():,}")
        print(f"   Komprimierung: {(1 - df['Timestamp'].nunique() / original_timestamps.nunique()) * 100:.1f}%")
    
    # Base aggregation (all categories combined)
    if verbose:
        print("\nErstelle Basis-Aggregation...")
    
    base_agg = df.groupby("Timestamp").agg(
        event_count       = ("Impact", "count"),
        impact_sum        = ("Impact", "sum"),
        impact_mean       = ("Impact", "mean"),
        impact_max        = ("Impact", "max"),
        impact_min        = ("Impact", "min"),
        impact_std        = ("Impact", "std"),
        impact_count_0    = ("Impact", lambda x: (x == 0).sum()),
        impact_count_1    = ("Impact", lambda x: (x == 1).sum()),
        impact_count_2    = ("Impact", lambda x: (x == 2).sum()),
        impact_count_3    = ("Impact", lambda x: (x == 3).sum()),
        impact_diversity  = ("Impact", "nunique"),
    )
    
    if verbose:
        print(f"   Basis-Aggregation erstellt: {len(base_agg)} Zeitstempel")
    
    # Category-specific aggregation
    if verbose:
        print("\nErstelle kategorie-spezifische Metriken...")
        categories = df['Category'].unique()
        print(f"   Kategorien: {', '.join(categories)}")
    
    cat_stats = (
        df
        .groupby(["Timestamp", "Category"])["Impact"]
        .agg(event_count="count", impact_sum="sum", impact_max="max")
        .unstack(level="Category", fill_value=0)
    )
    
    # Structure column names
    cat_stats.columns = [
        f"cat_{category}_{metric}" 
        for metric, category in cat_stats.columns
    ]
    
    if verbose:
        print(f"   Kategorie-Metriken erstellt: {len(cat_stats.columns)} Spalten")
    
    # Merge all metrics
    if verbose:
        print("\nFühre alle Metriken zusammen...")
    
    agg = base_agg.join(cat_stats, how="left")
    agg["impact_std"] = agg["impact_std"].fillna(0)
    agg = agg.reset_index()
    
    if verbose:
        print(f"   Finale Aggregation: {len(agg)} Zeilen, {len(agg.columns)} Spalten")
    
    return agg


def analyze_column_quality(df: pd.DataFrame, verbose: bool = True) -> Tuple[List[str], pd.DataFrame]:
    """
    Analyze data quality and identify zero-only columns.
    
    Args:
        df: DataFrame to analyze
        verbose: Whether to print and display results
    
    Returns:
        Tuple of (zero_only_columns, column_statistics)
    """
    if verbose:
        print("Analysiere Spalten auf Null-Werte...")
    
    only_zero_cols = []
    column_stats = []
    
    for col in df.columns:
        if col == 'Timestamp':
            continue
            
        # Get unique values (without NaN)
        unique_values = pd.unique(df[col].dropna())
        
        # Collect statistics
        stats = {
            'Spalte': col,
            'Eindeutige_Werte': len(unique_values),
            'Nur_Nullen': len(unique_values) == 1 and unique_values[0] == 0,
            'Min_Wert': df[col].min(),
            'Max_Wert': df[col].max(),
            'Summe': df[col].sum(),
            'Nicht_Null_Anzahl': (df[col] != 0).sum()
        }
        column_stats.append(stats)
        
        # Add to zero columns if applicable
        if stats['Nur_Nullen']:
            only_zero_cols.append(col)
    
    # Create statistics DataFrame
    stats_df = pd.DataFrame(column_stats)
    stats_df = stats_df.sort_values('Nicht_Null_Anzahl', ascending=True)
    
    if verbose:
        # Display results
        if only_zero_cols:
            print(f"\nGefundene Null-Spalten: {len(only_zero_cols)}")
            md = "### Spalten mit ausschließlich Null-Werten:\n\n"
            
            basis_nulls = [col for col in only_zero_cols if not col.startswith('cat_')]
            cat_nulls = [col for col in only_zero_cols if col.startswith('cat_')]
            
            if basis_nulls:
                md += "**Basis-Metriken:**\n"
                md += "\n".join(f"- `{col}`" for col in basis_nulls) + "\n\n"
            
            if cat_nulls:
                md += "**Kategorie-Metriken:**\n"
                md += "\n".join(f"- `{col}`" for col in cat_nulls) + "\n\n"
            
            md += f"**Empfehlung**: Diese {len(only_zero_cols)} Spalten könnten für das Machine Learning entfernt werden."
        else:
            md = "**Keine Null-Spalten gefunden** - Alle Spalten enthalten informative Werte!"
        
        display(Markdown(md))
        
        # Show low activity columns
        low_activity_cols = stats_df[stats_df['Nicht_Null_Anzahl'] < len(df) * 0.1]
        
        if len(low_activity_cols) > 0:
            print(f"\nSpalten mit geringer Aktivität (<10% nicht-null Werte):")
            display(low_activity_cols[['Spalte', 'Nicht_Null_Anzahl', 'Max_Wert', 'Summe']])
        else:
            print("Alle Spalten haben gute Aktivität (>10% nicht-null Werte)")
        
        # Summary
        print(f"\nZusammenfassung:")
        print(f"   Gesamt Spalten: {len(stats_df)}")
        print(f"   Null-Spalten: {len(only_zero_cols)}")
        print(f"   Spalten mit geringer Aktivität: {len(low_activity_cols)}")
        print(f"   Aktive Spalten: {len(stats_df) - len(only_zero_cols) - len(low_activity_cols)}")
    
    return only_zero_cols, stats_df


def process_chart_data(chart_data_path: str, verbose: bool = True) -> pd.DataFrame:
    """
    Load and process OHLC chart data with return calculations.
    
    Args:
        chart_data_path: Path to chart data CSV file
        verbose: Whether to print processing information
    
    Returns:
        Processed chart DataFrame
    """
    if verbose:
        print("Lade Chart-Daten...")
    
    df_chart = pd.read_csv(chart_data_path, parse_dates=["Timestamp"])
    
    if verbose:
        print(f"   Chart-Daten geladen: {len(df_chart):,} Zeilen")
        print(f"   Zeitraum: {df_chart['Timestamp'].min()} bis {df_chart['Timestamp'].max()}")
    
    # Extract basic chart features
    if verbose:
        print("\nVerarbeite OHLC-Daten...")
    
    df_chart_small = df_chart[["Timestamp", "Open", "High", "Low", "Close"]].copy()
    
    # Calculate returns: largest price movement as percentage change
    if verbose:
        print("   Berechne Returns...")
    
    price_down = np.abs(df_chart_small["Open"] - df_chart_small["Low"])
    price_up = np.abs(df_chart_small["High"] - df_chart_small["Open"])
    
    # Return based on largest movement
    df_chart_small["Return"] = np.where(
        price_down > price_up,
        (df_chart_small["Low"] - df_chart_small["Open"]) / df_chart_small["Open"] * 100,
        (df_chart_small["High"] - df_chart_small["Open"]) / df_chart_small["Open"] * 100
    )
    
    # Add absolute return and volume
    df_chart_small["|Return|"] = df_chart_small["Return"].abs()
    df_chart_small["Volume"] = df_chart["Volume"]
    
    if verbose:
        print(f"   Chart-Features erstellt: {list(df_chart_small.columns)}")
        print(f"   Return-Statistiken: Min={df_chart_small['Return'].min():.2f}%, Max={df_chart_small['Return'].max():.2f}%")
    
    return df_chart_small


def merge_and_finalize_data(
    df_chart: pd.DataFrame, 
    df_news: pd.DataFrame, 
    output_path: str,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Merge chart and news data, apply timezone adjustments, and save final dataset.
    
    Args:
        df_chart: Processed chart DataFrame
        df_news: Aggregated news DataFrame
        output_path: Path to save final merged dataset
        verbose: Whether to print processing information
    
    Returns:
        Final merged DataFrame
    """
    # Merge data
    if verbose:
        print("Führe Chart- und News-Daten zusammen...")
    
    df_merged = pd.merge(
        left=df_chart,
        right=df_news,
        on="Timestamp",
        how="left"
    ).fillna(0)
    
    if verbose:
        print(f"   Merge abgeschlossen: {len(df_merged):,} Zeilen, {len(df_merged.columns):,} Spalten")
        
        # Analyze news coverage
        news_coverage = (df_merged[df_news.columns.drop('Timestamp')].sum(axis=1) > 0).mean()
        print(f"   News-Coverage: {news_coverage:.1%} der Zeitpunkte haben News-Aktivität")
    
    # Timezone adjustment (UTC → Eastern Time)
    if verbose:
        print("\nFühre Zeitzone-Anpassung durch...")
    
    eastern = pytz.timezone("US/Eastern")
    
    # Convert UTC to Eastern Time
    df_merged["Timestamp_ET"] = (
        df_merged["Timestamp"]
        .dt.tz_localize("UTC")
        .dt.tz_convert(eastern)
    )
    
    # Detect Daylight Saving Time (DST)
    df_merged["is_dst"] = df_merged["Timestamp_ET"].apply(
        lambda x: x.dst().total_seconds() != 0
    )
    
    if verbose:
        dst_periods = df_merged["is_dst"].sum()
        non_dst_periods = (~df_merged["is_dst"]).sum()
        print(f"   DST-Perioden: {dst_periods:,} ({dst_periods/len(df_merged):.1%})")
        print(f"   Standard-Perioden: {non_dst_periods:,} ({non_dst_periods/len(df_merged):.1%})")
    
    # Adjust timestamps (DST = +1 hour to UTC)
    df_merged["Timestamp_Adjusted"] = df_merged.apply(
        lambda row: row["Timestamp"] + pd.Timedelta(hours=1) if row["is_dst"] else row["Timestamp"],
        axis=1
    )
    
    df_merged["Timestamp"] = df_merged["Timestamp_Adjusted"]
    df_merged = df_merged.drop(columns=["Timestamp_ET", "is_dst", "Timestamp_Adjusted"])
    
    if verbose:
        print("   Zeitzone-Anpassung abgeschlossen")
    
    # Final filtering
    if verbose:
        print("\nFühre finale Filterung durch...")
    
    original_length = len(df_merged)
    df_merged = df_merged[df_merged["Timestamp"].dt.weekday != 6]  # Remove Sundays
    filtered_length = len(df_merged)
    
    if verbose:
        removed_sundays = original_length - filtered_length
        print(f"   Sonntage entfernt: {removed_sundays:,} Zeilen ({removed_sundays/original_length:.1%})")
        print(f"   Verbleibende Daten: {filtered_length:,} Zeilen")
    
    # Save data
    if verbose:
        print(f"\nSpeichere finale Daten...")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if verbose:
            print(f"   Ordner erstellt: {output_dir}")
    
    # Remove existing file and save new one
    if os.path.exists(output_path):
        os.remove(output_path)
        if verbose:
            print(f"   Alte Datei entfernt")
    
    df_merged.to_csv(output_path, index=False)
    
    if verbose:
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"   Datei gespeichert: {output_path}")
        print(f"   Dateigröße: {file_size_mb:.1f} MB")
    
    return df_merged


def print_final_summary(df_merged: pd.DataFrame, verbose: bool = True) -> None:
    """
    Print comprehensive summary of the final dataset.
    
    Args:
        df_merged: Final merged DataFrame
        verbose: Whether to print detailed summary
    """
    if not verbose:
        return
    
    print(f"\nDATENVORBEREITUNG ABGESCHLOSSEN!")
    print(f"=" * 50)
    print(f"Finale Dataset-Statistiken:")
    print(f"   • Zeilen: {len(df_merged):,}")
    print(f"   • Spalten: {len(df_merged.columns):,}")
    print(f"   • Zeitraum: {df_merged['Timestamp'].min()} bis {df_merged['Timestamp'].max()}")
    print(f"   • Chart-Features: 6 (Timestamp, OHLC, Return, Volume)")
    print(f"   • News-Features: {len(df_merged.columns) - 6}")
    
    # Feature overview
    feature_types = {
        'Chart': ['Open', 'High', 'Low', 'Close', 'Return', 'Volume'],
        'News-Basis': [col for col in df_merged.columns 
                       if not col.startswith('cat_') and col not in ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Return', 'Volume']],
        'News-Kategorien': [col for col in df_merged.columns if col.startswith('cat_')]
    }
    
    print(f"\nFeature-Kategorien:")
    for category, features in feature_types.items():
        print(f"   • {category}: {len(features)} Features")
    
    # Return statistics
    print(f"\nReturn-Verteilung:")
    return_stats = {
        'Min': df_merged['Return'].min(),
        'Max': df_merged['Return'].max(), 
        'Mean': df_merged['Return'].mean(),
        'Std': df_merged['Return'].std(),
        'Positive': (df_merged['Return'] > 0).sum(),
        'Negative': (df_merged['Return'] < 0).sum(),
        'Zero': (df_merged['Return'] == 0).sum()
    }
    
    for stat, value in return_stats.items():
        if stat in ['Min', 'Max', 'Mean', 'Std']:
            print(f"   • {stat}: {value:.3f}%")
        else:
            print(f"   • {stat}: {value:,} ({value/len(df_merged):.1%})")
