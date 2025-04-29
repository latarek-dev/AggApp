from decimal import Decimal
from typing import Optional

def calculate_liquidity(
    balance0: int,
    balance1: int,
    decimals0: int,
    decimals1: int,
    price0: Decimal,
    price1: Decimal
) -> Decimal:
    """Oblicza całkowitą wartość płynności na podstawie sald i cen tokenów."""
    balance0_normalized = Decimal(balance0) / (10 ** decimals0)
    balance1_normalized = Decimal(balance1) / (10 ** decimals1)

    value0 = balance0_normalized * price0
    value1 = balance1_normalized * price1

    return value0 + value1
