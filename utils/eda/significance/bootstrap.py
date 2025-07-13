import numpy as np
from typing import List, Callable

def permutation_pvalue(
    groups,                                
    stat_func,                            
    num_samples=10_000,
    two_sided=False,
    random_seed=None,                      
):
    """
    Generic label-permutation p-value.
    """
    import numpy as np

    if random_seed is not None:
        np.random.seed(random_seed)

    t_obs  = stat_func(groups)
    flat   = np.concatenate(groups)
    sizes  = [g.size for g in groups]
    hits   = 0

    for _ in range(num_samples):
        np.random.shuffle(flat)
        res = np.split(flat, np.cumsum(sizes)[:-1])
        t   = stat_func(res)
        hits += (abs(t) >= abs(t_obs)) if two_sided else (t >= t_obs)

    return hits / num_samples
