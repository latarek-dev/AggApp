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

async def fetch_token_prices(coin_gecko_service, token_addresses: List[str], redis_cache_service) -> dict:
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

async def process_prices(coin_gecko_service, token_addresses, redis_cache_service, eth_address):
    # ceny dla wszystkich tokenów z puli (czyli 2 + ewentualnie ETH)
    tokens_to_fetch = set(token_addresses)
    if eth_address:
        tokens_to_fetch.add(eth_address)

    all_prices = await fetch_token_prices(coin_gecko_service, list(tokens_to_fetch), redis_cache_service)

    filtered_prices = {
        address: all_prices[address]
        for address in token_addresses
        if address in all_prices
    }

    eth_price = all_prices.get(eth_address) if eth_address else None
    eth_price = Decimal(eth_price)

    return filtered_prices, eth_price

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

    eth_address = token_manager.get_address_by_symbol("ETH")

    for pair, data in pools.items():

        tokens = pair.split('/')
        if set(tokens) != {token_from, token_to}:
            continue

        pool_address = data.get("address")
        token_addresses = token_manager.get_pool_addresses(dex_service, pool_address)

        token_decimals = token_manager.get_decimals_for_pool(token_addresses)

        prices, eth_price = await process_prices(coin_gecko_service, token_addresses, redis_cache_service, eth_address)
        pool_name = f"{dex_name.lower()}_{pair}"

        price_base, price_token = await get_or_cache_price(redis_cache_service, pool_address, pool_name, dex_service, token_decimals, data)
        print("token_from:", token_from)
        print("tokens:", tokens)
        print("amount:", amount)
        print("price_base:", price_base)
        print("price_token:", price_token)
        amount_out_expected = calculate_exchange_amount(token_from, tokens, amount, price_base, price_token)
        print("exchange_amount:", amount_out_expected)

        # Płynność
        liquidity = dex_service.get_liquidity(pool_address, token_addresses, token_decimals, prices)

        if liquidity is None:
            print(f"Pominięto pulę {pool_address} z powodu braku płynności.")
            continue

        balance0, balance1 = liquidity

        # Przelicz salda na wartość płynności w USD
        token0_address, token1_address = token_addresses
        token0_price = Decimal(str(prices.get(token0_address, 0)))
        token1_price = Decimal(str(prices.get(token1_address, 0)))

        if token0_price == 0 or token1_price == 0:
            print(f"Brak cen dla tokenów w puli {pool_address}, pomijam.")
            continue

        liquidity_usd = (balance0 * token0_price) + (balance1 * token1_price)

        token_from_address = token_manager.get_address_by_symbol(token_from)
        token_to_address = token_manager.get_address_by_symbol(token_to)

        dex_fee, gas_cost = dex_service.get_transaction_cost(pool_address, token_from_address, liquidity_usd, eth_price)

        token_from_price = prices.get(token_from_address, 1)
        token_to_price = prices.get(token_to_address, 1)

        print(token_from_address.lower())
        print(token_addresses[0].lower())
        
        # Oblicz slippage
        is_token0_from = token_from_address.lower() == token_addresses[0].lower()
        print("Czy token 0 jest from", is_token0_from)
        slippage_data = dex_service.get_slippage(pool_address, Decimal(amount), token_from, token_to, token_decimals)

        if slippage_data:
            amount_out = slippage_data["amount_out"]
            slippage = slippage_data["slippage"]
            price_before = slippage_data["price_before"]
            print("amount_out", amount_out, "slippage", slippage, "price_before", price_before)
        else:
            amount_out, slippage, price_before = None, None, None

        exchange_amount = amount_out_expected * (1 - dex_fee)
        if slippage is not None:
            exchange_amount = exchange_amount * (1 - slippage)
        else:
            print("Pominięto pulę z powodu braku slippage.")
            continue

        value_from_usd = amount * float(token_from_price)
        value_to_usd = float(exchange_amount) * float(token_to_price)

        option = TransactionOption(
            dex=dex_name,
            pool=pair,
            price=float(price_base if token_from == tokens[1] else price_token),
            slippage=slippage,
            liquidity=liquidity_usd,
            dex_fee=dex_fee,
            gas_cost=gas_cost,
            amount_from=amount,
            amount_to=float(exchange_amount), 
            value_from_usd=value_from_usd, 
            value_to_usd=value_to_usd
        )

        results.append(option)

    return results