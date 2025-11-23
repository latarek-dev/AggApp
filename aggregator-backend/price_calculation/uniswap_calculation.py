from decimal import Decimal

def uniswap_calculation(decimals_token, decimals_base, slot0_data):
    sqrt_price_x96 = slot0_data[0]
    sqrt_price = Decimal(sqrt_price_x96) / Decimal(2 ** 96)
    price_in_base = sqrt_price ** 2
    if decimals_token > decimals_base:
        price = price_in_base / Decimal(10 ** (decimals_token - decimals_base))
        inverse_price = Decimal(1) / price if price != 0 else Decimal(0)
    else:
        price = price_in_base * Decimal(10 ** (decimals_base - decimals_token))
        inverse_price = Decimal(1) / price if price != 0 else Decimal(0)

    return price, inverse_price