import pandas as pd
from IPython.display import display
from typing import List, Dict, Any

from .tests import ttest_two_samples, anova_oneway, chi2_independence

import numpy as np
import pandas as pd
from IPython.display import display

def show_news_ttests(
    df: pd.DataFrame,
    top_times: List[str],
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    num_permutations: int = 10_000,
    equal_var: bool = False,
    alpha: float = 0.05,
) -> List[str]:
    """
    Welch/Student two-sample t (classical & permutation) for each slot.
    Keeps only those slots whose permutation-p < alpha.
    Returns filtered time-slot list (excluding 'All Times').
    """
    rows, groups = [], top_times + ["All Times"]

    for slot in groups:
        # select returns for slots with and without news
        if slot == "All Times":
            mask = df[time_col].isin(top_times)
        else:
            mask = df[time_col] == slot
        with_news = df.loc[mask & (df[event_col] > 0), return_col].dropna().to_numpy()
        no_news   = df.loc[mask & (df[event_col] == 0), return_col].dropna().to_numpy()

        # run two-sample t-test with permutation fallback
        stats = ttest_two_samples(with_news, no_news,
                                   equal_var=equal_var,
                                   num_permutations=num_permutations)
        rows.append({"Time": slot, **stats})

    # assemble and format results
    res = (
        pd.DataFrame(rows)
          .round(6)
          .set_index("Time")
          .rename(columns={
              "Mean_x":   "Mean_with",
              "Mean_y":   "Mean_without",
              "N_x":      "N_with",
              "N_y":      "N_without",
              "p_classic":"p_val_classic_t",
              f"p_perm_{num_permutations:,}": "p_val_perm_t",
          })
    )

    # identify significant slots by permutation test
    sig_times = res.index[
        (res.index != "All Times") & (res["p_val_perm_t"] < alpha)
    ].tolist()

    print(
        f"\nTwo-sample *t*-tests, {num_permutations:,} permutations  "
        f"(α = {alpha}) – keeping {len(sig_times)} significant slots\n"
    )
    display(res)

    return sig_times


def show_category_anova(
    df: pd.DataFrame,
    top_times: List[str],
    categories: List[str],
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    num_permutations: int = 10_000,
    random_seed: int | None = 123,
) -> Dict[str, Any]:
    """
    One-way ANOVA of |Return| across dominant news categories
    within top time slots that have at least one news item.
    Returns summary dict with p-values and group sizes.
    """
    # filter rows in top times with any news
    df_news = df[df[time_col].isin(top_times) & (df[event_col] > 0)].copy()

    # count active categories per row and keep single-category cases
    cat_cols = [f"cat_{c}_event_count" for c in categories]
    df_news["n_cat_active"] = df_news[cat_cols].gt(0).sum(axis=1)
    df_one = df_news[df_news["n_cat_active"] == 1].copy()

    # assign dominant category label
    def _dominant(row):
        for c in categories:
            if row[f"cat_{c}_event_count"] > 0:
                return c
        return np.nan
    df_one["dominant_cat"] = df_one.apply(_dominant, axis=1)

    # group returns by dominant category and drop small groups
    groups_dict = {
        cat: df_one.loc[df_one["dominant_cat"] == cat, return_col]
                    .dropna().to_numpy()
        for cat in categories
    }
    groups_dict = {k: v for k, v in groups_dict.items() if v.size > 1}
    if len(groups_dict) < 2:
        raise ValueError("Need at least two categories with ≥2 observations each.")

    groups = list(groups_dict.values())

    # perform one-way ANOVA with permutation
    res = anova_oneway(groups,
                       num_permutations=num_permutations,
                       random_seed=random_seed)
    res.update(
        num_groups=len(groups_dict),
        group_sizes={k: int(v.size) for k, v in groups_dict.items()},
    )

    # print concise summary
    print("\nOne-way ANOVA (|Return| across dominant news categories)")
    print("Rows: top time slots, single-category news only")
    print(f"Parametric F = {res['f_statistic']:.4f},  p = {res['p_parametric']:.6f}")
    print(f"Permutation p ({num_permutations:,} shuffles) = {res['p_perm']:.6f}\n")
    print("Group sizes:", res["group_sizes"])

    return res


def show_category_ttests(
    df: pd.DataFrame,
    top_times: List[str],
    categories: List[str],
    return_col: str = "|Return|",
    event_col: str = "event_count",
    time_col: str = "time",
    num_permutations: int = 10_000,
    equal_var: bool = False,
    alpha: float = 0.05,
) -> List[str]:
    """
    Welch t-tests (classical & permutation) for each news category
    against baseline of top-time slots with no news.
    Applies Holm–Bonferroni correction and returns significant categories.
    """
    # baseline: returns when no news in top times
    mask_base = df[time_col].isin(top_times) & (df[event_col] == 0)
    baseline = df.loc[mask_base, return_col].dropna().to_numpy()

    rows = []
    for cat in categories:
        col = f"cat_{cat}_event_count"
        mask_cat = df[time_col].isin(top_times) & (df[col] > 0)
        group = df.loc[mask_cat, return_col].dropna().to_numpy()

        # require minimum sample size
        if group.size >= 5 and baseline.size >= 5:
            stats = ttest_two_samples(group, baseline,
                                       equal_var=equal_var,
                                       num_permutations=num_permutations)
            rows.append({
                "Category": cat,
                "N_with": group.size,
                "N_baseline": baseline.size,
                "Mean_with": stats["Mean_x"],
                "Mean_baseline": stats["Mean_y"],
                "t_stat": stats["t_stat"],
                "p_perm": stats[f"p_perm_{num_permutations:,}"],
                "Cohen_d": (
                    stats["Mean_x"] - stats["Mean_y"]
                ) / np.sqrt((group.var(ddof=1) + baseline.var(ddof=1)) / 2),
            })

    if not rows:
        raise ValueError("No category had ≥5 observations in both groups.")

    # compile and correct p-values
    res = (
        pd.DataFrame(rows)
          .round(6)
          .sort_values("p_perm")
          .reset_index(drop=True)
    )
    m = len(res)
    holm_factors = m - np.arange(m)
    holm_p = np.minimum(1, res["p_perm"].to_numpy() * holm_factors)
    res["p_perm_holm"] = holm_p

    sig_cats = res.loc[res["p_perm_holm"] < alpha, "Category"].tolist()

    print(
        f"\nCategory-specific Welch *t* tests vs. baseline "
        f"(top-time slots, {num_permutations:,} permutations)\n"
        f"Holm-adjusted α = {alpha}\n"
    )
    display(res.rename(columns={
        "N_with": "N with News",
        "N_baseline": "N Baseline",
        "Mean_with": "Mean with News",
        "Mean_baseline": "Mean Baseline",
        "t_stat": "t-Statistic",
        "p_perm": "p-Value (perm)",
        "p_perm_holm": "p-Value (Holm)",
        "Cohen_d": "Cohen's d"
    }))

    return sig_cats


def show_priority_return_chi2(
    df: pd.DataFrame,
    top_times: List[str],
    prio_map: Dict[str, int],
    event_col: str = "event_count",
    return_col: str = "|Return|",
    time_col: str = "time",
    absret_threshold: str | float = "median",
    num_permutations: int = 10_000,
    alpha: float = 0.05,
    random_seed: int | None = None,
):
    """
    Wrapper that prepares data and runs chi2_independence
    for news priority vs. high absolute returns.
    """
    # subset and compute news priority per row
    rows = df[df[time_col].isin(top_times)].copy()
    rows["News_Prio"] = rows.apply(
        lambda r: max(
            (prio_map[c] for c in prio_map
             if r[f"cat_{c}_event_count"] > 0),
            default=np.nan
        ),
        axis=1,
    )

    # determine threshold for high absolute return
    abs_ret = rows[return_col] if return_col in rows else rows["Return"].abs()
    thr = abs_ret.median() if absret_threshold == "median" else float(absret_threshold)
    rows["HighAbsRet"] = (abs_ret >= thr).astype(int)
    rows = rows.dropna(subset=["News_Prio"])

    # group binary outcomes by priority level
    groups = [
        rows.loc[rows["News_Prio"] == prio, "HighAbsRet"].to_numpy()
        for prio in sorted(rows["News_Prio"].unique())
    ]

    # run chi-square independence test with permutation
    res = chi2_independence(
        groups,
        num_permutations=num_permutations,
        random_seed=random_seed,
    )

    print("\nChi-square test: News priority vs. High |Return|")
    print(f"Permutations: {num_permutations:,}   α = {alpha}\n")
    for k, v in res.items():
        if isinstance(v, float):
            print(f"{k:>15}: {v:.6f}")
        else:
            print(f"{k:>15}: {v}")
    print("significant:", res["p_perm"] < alpha)

    return res
