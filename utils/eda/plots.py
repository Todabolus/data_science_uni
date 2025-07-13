import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple
import numpy as np
from scipy.stats import gaussian_kde

def boxplot(
    df: pd.DataFrame,
    top_times: List[str],
    abs_return_col: str = "|Return|",
    raw_return_col: str = "Return",
    event_col: str = "event_count",
    time_col: str = "time",
    figsize: Tuple[int, int] = (14, 6),
) -> None:
    """
    Boxplots of absolute & raw returns for top slots,
    split by news presence, plus combined "All Times" panel.
    """
    # restrict data to the selected time slots
    df_top = df[df[time_col].isin(top_times)].copy()

    # create a flag for whether each row has news
    df_top["news_flag"] = df_top[event_col].gt(0).map({True: "With News", False: "Without News"})

    # prepare absolute return data, including combined panel
    abs_df = df_top[[time_col, abs_return_col, "news_flag"]].rename(columns={abs_return_col: "value", time_col: "slot"})
    abs_combined = abs_df.copy()
    abs_combined["slot"] = "All Times"
    abs_plot = pd.concat([abs_df, abs_combined], ignore_index=True)

    # plot boxplot for absolute returns
    plt.figure(figsize=figsize)
    sns.boxplot(data=abs_plot, x="slot", y="value", hue="news_flag")
    plt.title("Boxplot: |Return| by Time (Top Slots & Combined)")
    plt.xlabel("Time Slot")
    plt.ylabel("|Return|")
    plt.xticks(rotation=45)
    plt.legend(title="News", loc="upper right")
    plt.tight_layout()
    plt.show()

    # prepare raw return data, including combined panel
    raw_df = df_top[[time_col, raw_return_col, "news_flag"]].rename(columns={raw_return_col: "value", time_col: "slot"})
    raw_combined = raw_df.copy()
    raw_combined["slot"] = "All Times"
    raw_plot = pd.concat([raw_df, raw_combined], ignore_index=True)

    # plot boxplot for raw returns
    plt.figure(figsize=figsize)
    sns.boxplot(data=raw_plot, x="slot", y="value", hue="news_flag")
    plt.title("Boxplot: Return by Time (Top Slots & Combined)")
    plt.xlabel("Time Slot")
    plt.ylabel("Return")
    plt.xticks(rotation=45)
    plt.legend(title="News", loc="upper right")
    plt.tight_layout()
    plt.show()


def return_histogram(
    df: pd.DataFrame,
    top_times: List[str],
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    figsize: Tuple[int, int] = (10, 5),
    bins: int = 100,
    kde_grid: int = 1000,
) -> None:
    """
    Histogram + KDE of absolute returns in top slots,
    split by news presence, with peak lines.
    """
    # filter to top slots and label news presence
    data = df[df[time_col].isin(top_times)].copy()
    data["News_Label"] = np.where(data[event_col] > 0, "With News", "Without News")

    # separate return arrays
    returns_with = data.loc[data["News_Label"] == "With News", return_col].dropna().to_numpy()
    returns_without = data.loc[data["News_Label"] == "Without News", return_col].dropna().to_numpy()

    # compute KDE peaks for each group
    max_val = data[return_col].max()
    x_grid = np.linspace(0, max_val, kde_grid)
    peak_with = x_grid[np.argmax(gaussian_kde(returns_with)(x_grid))] if returns_with.size else np.nan
    peak_without = x_grid[np.argmax(gaussian_kde(returns_without)(x_grid))] if returns_without.size else np.nan

    # plot histogram with KDE curves
    plt.figure(figsize=figsize)
    sns.histplot(
        data=data,
        x=return_col,
        hue="News_Label",
        bins=bins,
        kde=True,
        element="step",
        stat="count",
    )
    # add vertical lines at KDE peaks
    if not np.isnan(peak_with):
        plt.axvline(peak_with, color="orange", linestyle="--", linewidth=2, label=f"Peak With News ({peak_with:.4f})")
    if not np.isnan(peak_without):
        plt.axvline(peak_without, color="purple", linestyle="--", linewidth=2, label=f"Peak Without News ({peak_without:.4f})")

    plt.title("Histogram of |Return| at Top Slots (With / Without News)")
    plt.xlabel("Absolute Return")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.show()


def scatter_plot(
    df: pd.DataFrame,
    top_times: List[str],
    impact_col: str = "impact_sum",
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    figsize: Tuple[int, int] = (10, 6),
) -> None:
    """
    Scatter plot of news impact vs. absolute return
    for news-only rows in selected top slots.
    """
    # select only rows with news in top slots
    news_only = df[(df[time_col].isin(top_times)) & (df[event_col] > 0)][[impact_col, return_col]]

    # plot scatter of impact vs. return
    plt.figure(figsize=figsize)
    sns.scatterplot(data=news_only, x=impact_col, y=return_col)
    plt.title(f"Scatter: {impact_col} vs. {return_col} (News Only)")
    plt.xlabel(impact_col.replace('_', ' ').title())
    plt.ylabel(return_col)
    plt.tight_layout()
    plt.show()


def hexbin_plot(
    df: pd.DataFrame,
    top_times: List[str],
    impact_col: str = "impact_sum",
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    figsize: Tuple[int, int] = (10, 6),
    gridsize: int = 30,
    cmap: str = "viridis",
) -> None:
    """
    Hexbin plot of news impact vs. absolute return
    for news-only rows in top slots.
    """
    # filter to news-only rows in top slots
    news_only = df[(df[time_col].isin(top_times)) & (df[event_col] > 0)][[impact_col, return_col]]

    # plot hexbin of impact vs. return
    plt.figure(figsize=figsize)
    plt.hexbin(news_only[impact_col], news_only[return_col], gridsize=gridsize, cmap=cmap)
    plt.colorbar(label="Count")
    plt.xlabel(impact_col.replace("_", " ").title())
    plt.ylabel(return_col)
    plt.title(f"Hexbin: {impact_col} vs. {return_col} (News Only)")
    plt.tight_layout()
    plt.show()
