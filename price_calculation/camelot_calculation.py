from decimal import Decimal

def camelot_calculation(decimals_token, decimals_base, global_state):
    sqrt_price = Decimal(global_state[0]) / Decimal(2 ** 96)
    price = sqrt_price ** 2
    if decimals_token > decimals_base:
        price = price / Decimal(10 ** (decimals_token - decimals_base))
    else:
        price = price * Decimal(10 ** (decimals_base - decimals_token))
    inverse_price = Decimal(1) / price if price > 0 else Decimal(0)

    return price, inverse_price