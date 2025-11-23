import numpy as np
from typing import List
from models import TransactionOptionRaw

def rank_options(options: List[TransactionOptionRaw]) -> List[TransactionOptionRaw]:
    """Ranking TOPSIS: amount_to, liquidity, fee, gas."""
    if not options:
        return []

    matrix = np.array([
        [opt.amount_to, np.log1p(opt.liquidity), opt.dex_fee, opt.gas_cost]
        for opt in options
    ])

    epsilon = 1e-10
    norm_matrix = matrix / (np.sqrt((matrix ** 2).sum(axis=0)) + epsilon)

    weights = np.array([0.7, 0.2, 0.08, 0.02])
    weighted_matrix = norm_matrix * weights

    ideal_best = np.array([
        np.max(weighted_matrix[:, 0]),
        np.max(weighted_matrix[:, 1]),
        np.min(weighted_matrix[:, 2]),
        np.min(weighted_matrix[:, 3])
    ])

    ideal_worst = np.array([
        np.min(weighted_matrix[:, 0]),
        np.min(weighted_matrix[:, 1]),
        np.max(weighted_matrix[:, 2]),
        np.max(weighted_matrix[:, 3])
    ])

    dist_best = np.linalg.norm(weighted_matrix - ideal_best, axis=1)
    dist_worst = np.linalg.norm(weighted_matrix - ideal_worst, axis=1)

    scores = dist_worst / (dist_best + dist_worst)

    ranked_options = [(score, option) for score, option in zip(scores, options)]
    ranked_options.sort(reverse=True, key=lambda x: x[0])

    return [opt for _, opt in ranked_options]
