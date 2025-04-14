from typing import List
from models import TransactionOptionRaw

def rank_options(options: List[TransactionOptionRaw]) -> List[TransactionOptionRaw]:
    """
    Mock algorytm decyzyjny.
    Zwraca listę opcji posortowaną malejąco wg amount_to (czyli ilości tokenów otrzymywanych).
    """
    if not options:
        return []

    sorted_options = sorted(options, key=lambda opt: opt.amount_to, reverse=True)

    print("Opcje wymiany po sortowaniu:")
    for idx, opt in enumerate(sorted_options):
        print(f"{idx}: {opt}")

    return sorted_options
