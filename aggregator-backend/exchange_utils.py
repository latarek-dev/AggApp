from decimal import Decimal
from typing import Optional, List
from models import TransactionOption
from token_manager import TokenManager
from config import w3
from services import CoinGeckoService
from pools_config import TOKENS, get_pool_fee
from services.calculation_service import slippage_from_mid_and_actual

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
    eth_price = Decimal(eth_price) if eth_price else Decimal("0")

    return filtered_prices, eth_price

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
        
        print(pair)
        
        token_addresses = token_manager.get_pool_addresses(pair)
        
        if not token_addresses or len(token_addresses) != 2:
            print(f"Nie można wyprowadzić tokenów z pary {pair}, pomijam.")
            continue
        
        token_decimals = token_manager.get_decimals_for_pool(token_addresses)
        
        print(f"Para {pair}: tokens=[{token_addresses[0][:8]}..., {token_addresses[1][:8]}...]")

        prices, eth_price = await process_prices(coin_gecko_service, token_addresses, redis_cache_service, eth_address)
        pool_name = f"{dex_name.lower()}_{pair}"

        print("token_from:", token_from)
        print("tokens:", tokens)
        print("amount:", amount)

        # 1. Pobierz mid-price z cache lub blockchain
        cached_mid_price = await redis_cache_service.get_cached_price(pool_name)
        
        if cached_mid_price is None:
            # Brak w cache - pobierz z blockchain (slot0/globalState)
            print(f"Brak mid-price w cache dla {pool_name}, pobieram z blockchain...")
            mid_price = dex_service.get_mid_price(pool_address, token_from, token_to, token_decimals, token_addresses)
            
            if mid_price and mid_price > 0:
                # Zapisz w cache
                await redis_cache_service.set_cached_price(pool_name, mid_price)
                print(f"Zapisano mid-price {mid_price} w cache dla {pool_name}")
            else:
                print(f"Błąd pobierania mid-price z blockchain dla {pool_name}")
                continue
        else:
            # Mamy w cache - użyj bez ponownych obliczeń
            print(f"Użyto mid-price z cache dla {pool_name}: {cached_mid_price}")
            mid_price = Decimal(cached_mid_price)
        
        if mid_price <= 0:
            print(f"Brak mid-price dla {pool_address}, pomijam.")
            continue

        # 2. Pobierz dokładny quote z Quoter (już z fee)

        pool_fee = get_pool_fee(dex_name, pair)
        
        amount_out = dex_service.quote_exact_in(
            pool_address, token_from, token_to, Decimal(amount), 
            token_decimals, token_addresses, pool_fee, pair
        )
        if amount_out is None or amount_out == 0:
            print(f"Brak quote lub amount_out=0 dla {pool_address}, pomijam.")
            continue

        print(f"Mid-price: {mid_price}, Amount out: {amount_out}")

        # 3. Oblicz slippage porównując mid-price z actual output
        slippage = slippage_from_mid_and_actual(Decimal(amount), mid_price, amount_out)
        print(f"Slippage: {slippage}")

        # 4. Płynność
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

        # 5. Koszty transakcji
        dex_fee, gas_cost = dex_service.get_transaction_cost(pool_address, token_from_address, liquidity_usd, eth_price)

        if dex_fee is None or gas_cost is None:
            print(f"Brak kosztów dla {pool_address}, pomijam.")
            continue

        token_from_price = prices.get(token_from_address, 1)
        token_to_price = prices.get(token_to_address, 1)

        # 6. Wartości USD
        value_from_usd = amount * float(token_from_price)
        value_to_usd = float(amount_out) * float(token_to_price)

        # 7. Utwórz TransactionOption
        option = TransactionOption(
            dex=dex_name,
            pool=pair,
            price=float(mid_price),
            slippage=float(slippage),
            liquidity=liquidity_usd,
            dex_fee=float(dex_fee),
            gas_cost=float(gas_cost),
            amount_from=amount,
            amount_to=float(amount_out),  # amount_out z Quoter (już z fee)
            value_from_usd=value_from_usd, 
            value_to_usd=value_to_usd
        )

        results.append(option)

    return results