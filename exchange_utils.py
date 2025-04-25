from decimal import Decimal
from typing import Optional, List
from models import TransactionOption
from token_manager import TokenManager
from config import w3
from services import CoinGeckoService
from pools_config import TOKENS

token_manager = TokenManager(TOKENS)

def calculate_exchange_amount(token_from: str, tokens: list, amount: Decimal,
                              price_base: Decimal, price_tokens: Decimal) -> Decimal:
    if token_from == tokens[0]:
        return Decimal(amount) * price_tokens
    else:
        return Decimal(amount) * price_base

async def process_prices(coin_gecko_service, token_addresses, redis_cache_service):
    prices = {}
    missing_tokens_addresses = []

    for address in token_addresses:
        cache_key = f"coingecko_{address.lower()}"
        cached_price = await redis_cache_service.get_cached_price(cache_key)
        if cached_price is not None:
            prices[address] = float(cached_price)
        else:
            missing_tokens_addresses.append(address)

    if missing_tokens_addresses:
        print("Pobieram brakujące: ", missing_tokens_addresses)
        new_prices = {address: coin_gecko_service.get_price(address) for address in missing_tokens_addresses}

        for address, price in new_prices.items():
            if price is not None:
                cache_key = f"coingecko_{address.lower()}"
                await redis_cache_service.set_cached_price(cache_key, price)
                prices[address] = float(price)

    print(f"Pobrane ceny z cache + CoinGecko: {prices}")
    return prices

async def get_or_cache_price(redis_cache_service, pool_address, pool_name: str, dex_service, token_decimals, data: dict):
    # Sprawdzamy, czy cena jest w cache
    cached_price = await redis_cache_service.get_cached_price(pool_name)
    if cached_price is None:
        price_base, price_token = dex_service.get_pair_price(pool_address, token_decimals)
        if price_base and price_token:
            await redis_cache_service.set_cached_price(pool_name, price_base)
            cached_price = price_base
        else:
            price_base, price_token = Decimal(0), Decimal(0)
    else:
        price_base = Decimal(cached_price)
        price_token = Decimal(1) / Decimal(price_base) if price_base > 0 else Decimal(0)

    return price_base, price_token

async def process_dex_pools(dex_name: str,
                            pools: dict, 
                            dex_service, 
                            token_from: str, 
                            token_to: str, 
                            amount: float, 
                            redis_cache_service,
                            coin_gecko_service) -> List[TransactionOption]:

    results = []

    for pair, data in pools.items():

        tokens = pair.split('/')
        if set(tokens) != {token_from, token_to}:
            continue

        pool_address = data.get("address")
        token_addresses = token_manager.get_pool_addresses(dex_service, pool_address)
        print("Adresy: ", token_addresses)

        token_decimals = token_manager.get_decimals_for_pool(token_addresses)

        prices = await process_prices(coin_gecko_service, token_addresses, redis_cache_service)
        pool_name = f"{dex_name.lower()}_{pair}"

        price_base, price_token = await get_or_cache_price(redis_cache_service, pool_address, pool_name, dex_service, token_decimals, data)
        print("token_from:", token_from)
        print("tokens:", tokens)
        print("amount:", amount)
        print("price_base:", price_base)
        print("price_token:", price_token)
        exchange_amount = calculate_exchange_amount(token_from, tokens, amount, price_base, price_token)
        print("exchange_amount:", exchange_amount)

        # Płynność
        liquidity = dex_service.get_liquidity(pool_address, token_addresses, token_decimals, prices)
        print("Tyle wynosi liquidity", liquidity)

        # Koszt transakcji
        tx_cost = dex_service.get_transaction_cost(pool_address, token_decimals)
        print("Tyle wynosi tx cost", tx_cost)

        token_from_address = token_manager.get_address_by_symbol(token_from)
        token_to_address = token_manager.get_address_by_symbol(token_to)

        print("prices:", prices)
        token_from_price = prices.get(token_from_address, 1)
        token_to_price = prices.get(token_to_address, 1)
        print("token_from_price:", token_from_price)
        print("token_to_price:", token_to_price)

        value_from_usd = amount * float(token_from_price)
        value_to_usd = float(exchange_amount) * float(token_to_price)

        option = TransactionOption(
            dex=dex_name,
            pool=pair,
            price=float(price_base if token_from == tokens[1] else price_token),
            slippage=0.0,
            liquidity=liquidity,
            tx_cost=tx_cost,
            amount_from=amount,
            amount_to=float(exchange_amount), 
            value_from_usd=value_from_usd, 
            value_to_usd=value_to_usd
        )

        results.append(option)

    return results