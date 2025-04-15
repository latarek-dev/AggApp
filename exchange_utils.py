from decimal import Decimal
from typing import Optional, List
from models import TransactionOption

def calculate_exchange_amount(token_from: str, tokens: list, amount: float, price_base: Decimal, price_tokens: Decimal):
    if token_from == tokens[0]:
        return Decimal(amount) * Decimal(price_token)
    else:
        return Decimal(amount) * Decimal(price_base)

async def process_dex_pools(dex_name: str,
                            pools: dict, 
                            dex_service, 
                            price_method: str, 
                            token_from: str, 
                            token_to: str, 
                            amount: float, 
                            redis_cache_service, 
                            prices: dict) -> List[TransactionOption]:

    results = []

    for pair, data in pools.items():
        tokens = pair.split('/')
        if set(tokens) == {token_from, token_to}:
            pool_name = f"{dex_name.lower()}_{pair}"

            # Sprawdzamy, czy cena jest w cache
            cached_price = await redis_cache_service.get_cached_price(pool_name)
            if cached_price is None:
                price_base, price_token = getattr(dex_service, price_method)(data["address"], data["decimals"])
                if price_base and price_token:
                    await redis_cache_service.set_cached_price(pool_name, price_base)
                    cached_price = price_base
                else:
                    price_base = Decimal(0)
                    price_token = Decimal(0)
            else:
                price_base = cached_price
                price_token = Decimal(1) / Decimal(price_base) if price_base > 0 else Decimal(0)

            exchange_amount = calculate_exchange_amount(token_from, tokens, amount, price_base, price_token)

            # Płynność
            liquidity = dex_service.get_liquidity(data["address"])

            # Koszt transakcji
            tx_cost = dex_service.get_transaction_cost(data["address"])

            token_from_price = prices.get(token_from, 1)
            token_to_price = prices.get(token_to, 1)

            value_from_usd = amount * float(token_from_price)
            value_to_usd = float(exchange_amount) * float(token_to_price)

            option = TransactionOption(
                dex=dex_name,
                pool=pair,
                price=float(price_base if token_from == tokens[1] else price_token),
                slippage=0.0,
                liquidity=0.0,
                tx_cost=0.0,
                amount_from=amount,
                amount_to=float(exchange_amount), 
                value_from_usd=value_from_usd, 
                value_to_usd=value_to_usd
            )

            results.append(option)

    return results

async def process_prices(coin_gecko_service, token_ids, redis_cache_service):
    prices = {}
    missing_tokens_ids = []

    for token_id in token_ids:
        cached_price = await redis_cache_service.get_cached_price(f"coingecko_{token_id}")
        if cached_price is not None:
            prices[token_id] = float(cached_price)
        else:
            missing_tokens_ids.append(token_id)

    if missing_tokens_ids:
        print("Pobieram brakujące: ", missing_tokens_ids)
        new_prices = {token_id: coin_gecko_service.get_price(token_id) for token_id in missing_tokens_ids}

        for token_id, price in new_prices.items():
            if price is not None:
                await redis_cache_service.set_cached_price(f"coingecko_{token_id}", price)
                prices[token_id] = float(price)

    print(f"Pobrane ceny z cache + CoinGecko: {prices}")
    return prices