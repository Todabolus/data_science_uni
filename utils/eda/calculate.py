import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from typing import List, Tuple
from scipy.stats import norm

def get_top_times(
    df: pd.DataFrame,
    n_top: int = 5,
    time_col: str = "time",
    event_col: str = "event_count",
    figsize: Tuple[int, int] = (16, 6),
) -> List[str]:
    """
    Identify the most active time slots, plot their counts, and return the list of top slots.
    """
    # count days with at least one event per time slot
    counts = df[df[event_col] > 0].groupby(time_col).size()
    # select top n slots
    top_times = counts.nlargest(n_top).index.tolist()

    # plot bar chart with top slots highlighted
    plt.figure(figsize=figsize)
    colors = ["red" if t in top_times else "blue" for t in counts.index]
    counts.plot(kind="bar", color=colors)
    plt.title(f"Days with ≥1 News per Slot (Top {n_top} in Red)")
    plt.ylabel("Number of Days")
    plt.xlabel("Time Slot")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

    # report summary
    print(
        f"Top time slots: {top_times}\n"
        f"Rows in top slots: {df[time_col].isin(top_times).sum()} of {len(df)}"
    )
    return top_times

def descriptive_statistics(
    df: pd.DataFrame,
    top_times: List[str],
    time_col: str = "time",
    event_col: str = "event_count",
    return_col: str = "|Return|",
) -> None:
    """
    Compute and display descriptive stats for each top time (with/without news) and combined.
    """
    def _stats(series: pd.Series) -> dict:
        # return summary or NaNs if empty
        if series.empty:
            keys = ["count", "mean", "std", "min", "25%", "median", "75%", "max"]
            return {k: np.nan for k in keys}
        desc = series.describe()
        desc.rename({"50%": "median"}, inplace=True)
        return desc.to_dict()

    # stats per time slot and news presence
    rows = []
    for t in top_times:
        for has_news in (True, False):
            mask = (df[time_col] == t) & ((df[event_col] > 0) if has_news else (df[event_col] == 0))
            vals = df.loc[mask, return_col].dropna()
            rows.append({
                "Time": t,
                "News": "With" if has_news else "Without",
                **_stats(vals),
            })
    stats_per_time = pd.DataFrame(rows).round(4)

    # combined stats across all top slots
    combined = []
    for has_news in (True, False):
        mask = df[time_col].isin(top_times) & ((df[event_col] > 0) if has_news else (df[event_col] == 0))
        vals = df.loc[mask, return_col].dropna()
        combined.append({
            "Time": "All Times",
            "News": "With" if has_news else "Without",
            **_stats(vals),
        })
    stats_combined = pd.DataFrame(combined).round(4)

    # display results
    print("\n=== Descriptive Statistics per Top Time ===\n")
    display(stats_per_time)
    print("\n=== Combined Descriptive Statistics ===\n")
    display(stats_combined)

def confidence_intervals(
    df: pd.DataFrame,
    top_times: List[str],
    cols: List[str] | str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    confidence: float = 0.95,
    n_bootstrap: int = 10_000,
) -> pd.DataFrame:
    """
    Calculate classical (z) and bootstrap percentile CIs for specified columns
    within top time slots for groups: With News, Without News, All Times.
    """
    def _classic_ci(arr: np.ndarray) -> dict:
        # z-interval for mean; return NaNs if insufficient data
        n = arr.size
        if n < 2:
            return dict(mean=np.nan, ci_lower=np.nan, ci_upper=np.nan, n_obs=n)
        alpha = 1 - confidence
        z = norm.ppf(1 - alpha/2)
        s = arr.std(ddof=1)
        half = z * s / np.sqrt(n)
        return dict(mean=arr.mean(), ci_lower=arr.mean() - half, ci_upper=arr.mean() + half, n_obs=n)

    def _bootstrap_ci(arr: np.ndarray) -> dict:
        # percentile bootstrap CI; return NaNs if empty
        n = arr.size
        if n == 0:
            return dict(mean=np.nan, ci_lower=np.nan, ci_upper=np.nan, n_obs=0)
        alpha = 1 - confidence
        boot_means = np.random.choice(arr, (n_bootstrap, n)).mean(axis=1)
        low, high = np.quantile(boot_means, [alpha/2, 1-alpha/2])
        return dict(mean=arr.mean(), ci_lower=low, ci_upper=high, n_obs=n)

    # ensure list of columns
    if isinstance(cols, str):
        cols = [cols]

    # define masks for groups
    masks = {
        "With News":    df[time_col].isin(top_times) & (df[event_col] > 0),
        "Without News": df[time_col].isin(top_times) & (df[event_col] == 0),
        "All Times":    df[time_col].isin(top_times),
    }

    rows = []
    for grp, mask in masks.items():
        for col in cols:
            data = df.loc[mask, col].dropna().to_numpy()
            rows.append({"Group": grp, "series": col, "method": "Classical", **_classic_ci(data)})
            rows.append({"Group": grp, "series": col, "method": f"Bootstrap ({n_bootstrap:,})", **_bootstrap_ci(data)})

    result = (
        pd.DataFrame(rows)
          .round(4)
          .sort_values(["series", "Group", "method"])
          .reset_index(drop=True)
    )

    print(f"\n{int(confidence*100)}% Confidence Intervals (classical & bootstrap)\n")
    display(result)
    return result

def correlations(
    df: pd.DataFrame,
    top_times: List[str],
    impact_cols: List[str] | None = None,
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    method: str = "pearson",
    decimals: int = 4,
) -> pd.DataFrame:
    """
    Compute and display correlation matrix between return and impact metrics
    for news-only rows within top time slots.
    """
    # set default impact columns
    if impact_cols is None:
        impact_cols = ["impact_sum", "impact_mean", "impact_std"]

    # filter to relevant rows
    mask = df[time_col].isin(top_times) & (df[event_col] > 0)
    cols = [return_col] + impact_cols
    corr_matrix = df.loc[mask, cols].corr(method=method).round(decimals)

    print(f"\nCorrelation matrix ({method.title()}) for news-only in top slots:\n")
    display(corr_matrix)
    return corr_matrix

def crosstab(
    df: pd.DataFrame,
    top_times: List[str],
    categories: List[str],
    high_return_threshold: float,
    return_col: str = "Return",
    time_col: str = "time",
) -> pd.DataFrame:
    """
    Generate crosstabs of high-return flag vs. category presence
    for rows in top time slots. Cells show count and row percentage.
    """
    # flag high returns
    df2 = df.copy()
    df2["high_return"] = (df2[return_col] >= high_return_threshold).astype(int)
    df_top = df2[df2[time_col].isin(top_times)]

    summary_cols = []
    for cat in categories:
        count_col = f"cat_{cat}_event_count"
        if count_col not in df_top.columns:
            raise KeyError(f"Column '{count_col}' not found in dataframe.")
        # binary indicator for presence
        present = (df_top[count_col] > 0).astype(int)
        # build 2x2 table with margins
        ct = pd.crosstab(df_top["high_return"], present, margins=True)
        ct = ct.drop(columns="All")
        pct = (ct.div(ct.loc["All"], axis=1) * 100).round(2)
        for val in ct.columns:
            merged = ct[val].astype(str) + " (" + pct[val].astype(str) + "%)"
            summary_cols.append(merged.rename(f"{cat.replace('_',' ').title()} [{val}]"))

    final = pd.concat(summary_cols, axis=1)
    print("\n=== Crosstab: Category Presence vs. High Return (top slots) ===\n")
    display(final)
    return final
