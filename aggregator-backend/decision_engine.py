import numpy as np
from typing import List
from models import TransactionOptionRaw

def rank_options(options: List[TransactionOptionRaw]) -> List[TransactionOptionRaw]:
    if not options:
        return []

    # Krok 1: Macierz decyzyjna
    matrix = np.array([
        [opt.amount_to, opt.slippage, opt.liquidity, opt.dex_fee, opt.gas_cost]
        for opt in options
    ])

    # Krok 2: Normalizacja macierzy
    epsilon = 1e-10
    norm_matrix = matrix / (np.sqrt((matrix ** 2).sum(axis=0)) + epsilon)

    # Krok 3: Wagi (ważność kryteriów – możesz je dostosować)
    # Więcej amount_to i liquidity = lepiej, mniej slippage, fee, gas = lepiej
    weights = np.array([0.35, 0.2, 0.2, 0.15, 0.1])

    # Krok 4: Macierz ważona
    weighted_matrix = norm_matrix * weights

    # Krok 5: Ideał pozytywny i negatywny
    ideal_best = np.array([
        np.max(weighted_matrix[:, 0]),  # amount_to – max
        np.min(weighted_matrix[:, 1]),  # slippage – min
        np.max(weighted_matrix[:, 2]),  # liquidity – max
        np.min(weighted_matrix[:, 3]),  # dex_fee – min
        np.min(weighted_matrix[:, 4])   # gas_cost – min
    ])

    ideal_worst = np.array([
        np.min(weighted_matrix[:, 0]),
        np.max(weighted_matrix[:, 1]),
        np.min(weighted_matrix[:, 2]),
        np.max(weighted_matrix[:, 3]),
        np.max(weighted_matrix[:, 4])
    ])

    # Krok 6: Odległość od ideału
    dist_best = np.linalg.norm(weighted_matrix - ideal_best, axis=1)
    dist_worst = np.linalg.norm(weighted_matrix - ideal_worst, axis=1)

    # Krok 7: Obliczenie wyniku TOPSIS
    scores = dist_worst / (dist_best + dist_worst)

    # Krok 8: Posortuj opcje według wyniku
    ranked_options = [
        (score, option) for score, option in zip(scores, options)
    ]
    ranked_options.sort(reverse=True, key=lambda x: x[0])

    print("Opcje wymiany wg TOPSIS:")
    for idx, (score, opt) in enumerate(ranked_options):
        print(f"{idx}: score={score:.4f}, {opt}")

    return [opt for _, opt in ranked_options]
