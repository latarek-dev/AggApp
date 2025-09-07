from decimal import Decimal
from typing import Optional

Q96 = 2 ** 96

def mid_price_from_univ3_sqrt(
    sqrt_price_x96: int,
    dec0: int,
    dec1: int,
    is_token0_in: bool,
) -> Decimal:
    """
    Oblicza mid-price z sqrtPriceX96 dla Uniswap V3.
    
    Args:
        sqrt_price_x96: sqrt(price) * 2^96 z slot0
        dec0: decimals token0
        dec1: decimals token1  
        is_token0_in: czy token0 jest tokenem wejściowym
        
    Returns:
        Decimal: mid-price (token_out / token_in)
    """
    ratio = Decimal(sqrt_price_x96) / Decimal(Q96)
    price_chain = ratio * ratio  # token1/token0
    scale = Decimal(10) ** (dec0 - dec1)
    p0_to_1 = price_chain * scale
    return p0_to_1 if is_token0_in else (Decimal(1) / p0_to_1)

def slippage_from_mid_and_actual(
    amount_in: Decimal, mid_price: Decimal, actual_out: Decimal
) -> Decimal:
    """
    Oblicza slippage porównując mid-price z actual output z Quoter.
    
    Args:
        amount_in: ilość tokenów wejściowych
        mid_price: mid-price z slot0/globalState
        actual_out: rzeczywisty output z Quoter (już z fee)
        
    Returns:
        Decimal: slippage (0-1)
    """
    if amount_in <= 0 or mid_price <= 0:
        return Decimal(0)
    ideal_out = amount_in * mid_price
    if ideal_out <= 0:
        return Decimal(0)
    s = (ideal_out - actual_out) / ideal_out
    return s if s > 0 else Decimal(0)
