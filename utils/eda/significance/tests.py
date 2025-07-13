import numpy as np
from scipy.stats import ttest_ind, f_oneway, chi2_contingency
from typing import Dict, List

from .bootstrap import permutation_pvalue

def ttest_two_samples(
    x: np.ndarray,
    y: np.ndarray,
    equal_var: bool = False,
    num_permutations: int = 10_000,
) -> Dict[str, float]:
    """
    Classical Welch/Student t plus permutation-based p-value in one call.
    Returns a dict with sample sizes, means, t-statistic, classical p-value, and permutation p-value.
    """
    # perform parametric two-sample t-test
    t_stat, p_classic = ttest_ind(x, y, equal_var=equal_var)

    # prepare statistic function for permutation: returns the t-statistic
    stat_func = lambda groups: ttest_ind(groups[0], groups[1], equal_var=equal_var)[0]

    # estimate p-value by randomly shuffling labels
    p_perm = permutation_pvalue([x, y], stat_func, num_samples=num_permutations)

    return {
        "N_x": x.size,
        "N_y": y.size,
        "Mean_x": x.mean(),
        "Mean_y": y.mean(),
        "t_stat": t_stat,
        "p_classic": p_classic,
        f"p_perm_{num_permutations:,}": p_perm,
    }


def _f_statistic(groups: List[np.ndarray]) -> float:
    """Compute one-way ANOVA F statistic for a list of samples."""
    k = len(groups)                             # number of groups
    N = sum(len(a) for a in groups)             # total observations
    all_data = np.concatenate(groups)
    grand_mean = all_data.mean()                # overall mean

    # between-group variability
    ss_between = sum(len(a) * (a.mean() - grand_mean) ** 2 for a in groups)
    # within-group variability
    ss_within = sum(((a - a.mean())**2).sum() for a in groups)

    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (N - k)

    return ms_between / ms_within


def anova_oneway(
    groups: List[np.ndarray],
    num_permutations: int = 10_000,
    random_seed: int | None = None,
) -> Dict[str, float]:
    """
    Classical parametric one-way ANOVA plus permutation p-value.
    `groups` is a list of numeric arrays (k ≥ 2, each length ≥ 2).
    """
    # get F-statistic and parametric p-value
    f_obs, p_classic = f_oneway(*groups)

    # estimate permutation p-value for F (only large values increase significance)
    p_perm = permutation_pvalue(
        groups,
        _f_statistic,
        num_samples=num_permutations,
        two_sided=False,
        random_seed=random_seed,
    )

    return {
        "f_statistic": f_obs,
        "p_parametric": p_classic,
        "p_perm": p_perm,
    }


def _chi2_statistic(groups: List[np.ndarray]) -> float:
    """Compute Pearson chi-square statistic for categorical data."""
    # identify all category levels
    levels = np.unique(np.concatenate(groups))
    level_idx = {lvl: i for i, lvl in enumerate(levels)}

    # build contingency table
    table = np.zeros((len(groups), len(levels)), dtype=int)
    for row, arr in enumerate(groups):
        vals, counts = np.unique(arr, return_counts=True)
        for val, cnt in zip(vals, counts):
            table[row, level_idx[val]] = cnt

    chi2, _, _, _ = chi2_contingency(table, correction=False)
    return chi2


def chi2_independence(
    groups: List[np.ndarray],
    num_permutations: int = 10_000,
    random_seed: int | None = None,
) -> Dict[str, float]:
    """
    Pearson chi-square test plus permutation p-value for an arbitrary contingency.
    `groups` is a list where each array contains category labels for one factor level.
    """
    # compute chi-square statistic for observed table
    chi2_stat = _chi2_statistic(groups)

    # rebuild same contingency table for classical p-value
    levels = np.unique(np.concatenate(groups))
    table = np.zeros((len(groups), len(levels)), dtype=int)
    for row, arr in enumerate(groups):
        vals, counts = np.unique(arr, return_counts=True)
        for val, cnt in zip(vals, counts):
            table[row, np.where(levels == val)[0][0]] = cnt

    # classical chi-square test without continuity correction
    _, p_param, _, _ = chi2_contingency(table, correction=False)

    # permutation-based p-value for chi-square
    p_perm = permutation_pvalue(
        groups,
        _chi2_statistic,
        num_samples=num_permutations,
        two_sided=False,
        random_seed=random_seed,
    )

    return {
        "chi2_statistic": chi2_stat,
        "p_parametric": p_param,
        "p_perm": p_perm,
    }
