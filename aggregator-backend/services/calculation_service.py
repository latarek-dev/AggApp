from decimal import Decimal
from typing import Optional

Q96 = 2 ** 96

def mid_price_from_univ3_sqrt(
    sqrt_price_x96: int,
    dec0: int,
    dec1: int,
    is_token0_in: bool,
) -> Decimal:
    """Oblicza mid-price z sqrtPriceX96 dla Uniswap V3."""
    ratio = Decimal(sqrt_price_x96) / Decimal(Q96)
    price_chain = ratio * ratio  # token1/token0
    scale = Decimal(10) ** (dec0 - dec1)
    p0_to_1 = price_chain * scale
    return p0_to_1 if is_token0_in else (Decimal(1) / p0_to_1)

