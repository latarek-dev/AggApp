from decimal import Decimal
from typing import Optional, List
import asyncio
from models import TransactionOption
from token_manager import TokenManager
from config import w3
from services import CoinGeckoService
from services.defillama_service import DefiLlamaService
from pools_config import TOKENS, DEX_CONFIGS, get_pool_fee

token_manager = TokenManager(TOKENS)
defillama_service = DefiLlamaService(chain="arbitrum")

def calculate_exchange_amount(token_from: str, tokens: list, amount: Decimal,
                              price_base: Decimal, price_tokens: Decimal) -> Decimal:
    if token_from == tokens[0]:
        return Decimal(amount) * price_tokens
    else:
        return Decimal(amount) * price_base

async def fetch_token_prices(coin_gecko_service, token_addresses: List[str], redis_cache_service) -> dict:
    """Pobiera ceny tokenów: najpierw DefiLlama (główny), potem CoinGecko (fallback)."""
    prices = {}
    missing_tokens_addresses = []

    # Sprawdzenie cache
    for address in token_addresses:
        cache_key = f"coingecko_{address.lower()}"
        cached_price = await redis_cache_service.get_cached_price(cache_key)
        if cached_price is not None:
            prices[address] = float(cached_price)
        else:
            missing_tokens_addresses.append(address)

    if missing_tokens_addresses:
        print(f"Pobieranie {len(missing_tokens_addresses)} tokenów przez batch API (DefiLlama)...")
        
        # Główny serwis: DefiLlama
        llama_prices = defillama_service.get_prices_batch(missing_tokens_addresses)
        
        still_missing = []
        for addr in missing_tokens_addresses:
            price = llama_prices.get(addr)
            if price and price > 0:
                prices[addr] = float(price)
                cache_key = f"coingecko_{addr.lower()}"
                await redis_cache_service.set_cached_price(cache_key, price, ttl=10)
            else:
                still_missing.append(addr)
        
        # Fallback - CoinGecko dla brakujących
        if still_missing:
            print(f"DefiLlama nie zwrócił {len(still_missing)} cen, próbuję CoinGecko (fallback)...")
            cg_prices = coin_gecko_service.get_prices_batch(still_missing)
            
            for addr, price in cg_prices.items():
                if price and price > 0:
                    prices[addr] = float(price)
                    cache_key = f"coingecko_{addr.lower()}"
                    await redis_cache_service.set_cached_price(cache_key, price, ttl=10)
                    print(f"CoinGecko (fallback): {addr[:8]}... = ${price}")

    print(f"Pobrane ceny ({len(prices)}/{len(token_addresses)}): {list(prices.keys())}")
    return prices

async def process_prices(coin_gecko_service, token_addresses, redis_cache_service, eth_address):
    """Pobiera ceny tokenów puli + ETH koszt gazu."""
    tokens_to_fetch = set(token_addresses)
    if eth_address:
        tokens_to_fetch.add(eth_address)

    all_prices = await fetch_token_prices(coin_gecko_service, list(tokens_to_fetch), redis_cache_service)

    filtered_prices = {addr: all_prices[addr] for addr in token_addresses if addr in all_prices}
    eth_price = Decimal(all_prices.get(eth_address, 0)) if eth_address else Decimal("0")

    return filtered_prices, eth_price

async def process_single_pool(dex_name: str,
                               pair: str,
                               data: dict,
                               dex_service,
                               token_from: str,
                               token_to: str,
                               amount: float,
                               redis_cache_service,
                               all_prices: dict,
                               eth_price: Decimal) -> Optional[TransactionOption]:
    """Przetwarza pojedynczą pulę DEX z asynchronicznymi wywołaniami blockchain."""
    
    pool_address = data.get("address")
    
    token_addresses = token_manager.get_pool_addresses(pair)
    
    if not token_addresses or len(token_addresses) != 2:
        return None
    
    token_decimals = token_manager.get_decimals_for_pool(token_addresses)
    
    print(f"Para {pair}: tokens=[{token_addresses[0][:8]}..., {token_addresses[1][:8]}...]")

    prices = {addr: all_prices.get(addr, 0) for addr in token_addresses}
    pool_name = f"{dex_name.lower()}_{pair}"

    cached_mid_price = await redis_cache_service.get_cached_price(pool_name)
    
    if cached_mid_price is None:
        print(f"Brak mid-price w cache dla {pool_name}, pobieram z blockchain...")
        mid_price = await asyncio.to_thread(
            dex_service.get_mid_price, 
            pool_address, token_from, token_to, token_decimals, token_addresses
        )
        
        if mid_price and mid_price > 0:
            await redis_cache_service.set_cached_price(pool_name, mid_price, ttl=10)
            print(f"Zapisano mid-price {mid_price} w cache dla {pool_name}")
        else:
            print(f"Błąd pobierania mid-price z blockchain dla {pool_name}")
            return None
    else:
        print(f"Użyto mid-price z cache dla {pool_name}: {cached_mid_price}")
        mid_price = Decimal(cached_mid_price)
    
    if mid_price <= 0:
        return None

    pool_fee = get_pool_fee(dex_name, pair)
    
    rounded_amount = round(amount, 2)
    quote_cache_key = f"{pool_name}_quote_{token_from}_{token_to}_{rounded_amount}"
    
    cached_quote = await redis_cache_service.get_cached_price(quote_cache_key)
    if cached_quote is not None:
        amount_out = Decimal(cached_quote)
        print(f"Użyto quote z cache dla {quote_cache_key}: {amount_out}")
    else:
        print(f"Brak quote w cache dla {quote_cache_key}, pobieram z blockchain...")
        amount_out = await asyncio.to_thread(
            dex_service.quote_exact_in,
            pool_address, token_from, token_to, Decimal(amount), 
            token_decimals, token_addresses, pool_fee, pair
        )
        if amount_out and amount_out > 0:
            # TTL 60s - spójne z resztą cache
            await redis_cache_service.set_cached_price(quote_cache_key, amount_out, ttl=10)
            print(f"Zapisano quote {amount_out} w cache dla {quote_cache_key}")
    
    if amount_out is None or amount_out == 0:
        print(f"Brak quote lub amount_out=0 dla {pool_address}, pomijam.")
        return None

    print(f"Mid-price: {mid_price}, Amount out: {amount_out}")

    liquidity_cache_key = f"{pool_name}_liquidity"
    cached_liquidity = await redis_cache_service.get_cached_price(liquidity_cache_key)
    
    if cached_liquidity is not None:
        liquidity_usd = Decimal(cached_liquidity)
        print(f"Użyto liquidity z cache dla {liquidity_cache_key}: {liquidity_usd}")
    else:
        print(f"Brak liquidity w cache dla {liquidity_cache_key}, pobieram z blockchain...")
        liquidity = await asyncio.to_thread(
            dex_service.get_liquidity,
            pool_address, token_addresses, token_decimals, prices
        )

        if liquidity is None:
            print(f"Pominięto pulę {pool_address} z powodu braku płynności.")
            return None

        balance0, balance1 = liquidity

        token0_address, token1_address = token_addresses
        token0_price = Decimal(str(prices.get(token0_address, 0)))
        token1_price = Decimal(str(prices.get(token1_address, 0)))

        if token0_price == 0 or token1_price == 0:
            return None

        liquidity_usd = (balance0 * token0_price) + (balance1 * token1_price)

        await redis_cache_service.set_cached_price(liquidity_cache_key, liquidity_usd, ttl=10)
        print(f"Zapisano liquidity {liquidity_usd} w cache dla {liquidity_cache_key}")

    token_from_address = token_manager.get_address_by_symbol(token_from)
    token_to_address = token_manager.get_address_by_symbol(token_to)
    
    token_from_decimals = token_manager.get_decimals_by_symbol(token_from)
    amount_in_wei = int(Decimal(amount) * (10 ** token_from_decimals))
    
    router_address = DEX_CONFIGS[dex_name]['contracts']['router']
    
    fee_tier = pool_fee if pool_fee else 500

    dex_fee_cache_key = f"{pool_name}_dexfee_{token_from}_{token_to}_{rounded_amount}"
    gas_cost_cache_key = f"{pool_name}_gascost_{token_from}_{token_to}_{rounded_amount}"
    
    cached_dex_fee = await redis_cache_service.get_cached_price(dex_fee_cache_key)
    cached_gas_cost = await redis_cache_service.get_cached_price(gas_cost_cache_key)
    
    if cached_dex_fee is not None and cached_gas_cost is not None:
        dex_fee = Decimal(cached_dex_fee)
        gas_cost = Decimal(cached_gas_cost)
        print(f"Użyto transaction cost z cache dla {dex_fee_cache_key}: dex_fee={dex_fee}, gas_cost={gas_cost}")
    else:
        print(f"Brak transaction cost w cache, pobieram z blockchain...")
        cost_result = await asyncio.to_thread(
            dex_service.get_transaction_cost,
            pool_address=pool_address,
            token_from_address=token_from_address,
            token_to_address=token_to_address,
            amount_in_wei=amount_in_wei,
            fee_tier=fee_tier,
            router_address=router_address,
            liquidity=liquidity_usd,
            eth_price=eth_price
        )

        if cost_result is None:
            return None
        
        dex_fee, gas_cost = cost_result
        
        if dex_fee is not None and gas_cost is not None:
            await redis_cache_service.set_cached_price(dex_fee_cache_key, dex_fee, ttl=10)
            await redis_cache_service.set_cached_price(gas_cost_cache_key, gas_cost, ttl=10)
            print(f"Zapisano transaction cost w cache: dex_fee={dex_fee}, gas_cost={gas_cost}")
        else:
            return None
    
    if dex_fee is None or gas_cost is None:
        return None

    token_from_price = all_prices.get(token_from_address, 1)
    token_to_price = all_prices.get(token_to_address, 1)

    value_from_usd = amount * float(token_from_price)
    value_to_usd = float(amount_out) * float(token_to_price)

    return TransactionOption(
        dex=dex_name,
        pool=pair,
        price=float(mid_price),
        liquidity=liquidity_usd,
        dex_fee=float(dex_fee),
        gas_cost=float(gas_cost),
        amount_from=amount,
        amount_to=float(amount_out),
        value_from_usd=value_from_usd, 
        value_to_usd=value_to_usd
    )


async def process_dex_pools(dex_name: str,
                            pools: dict, 
                            dex_service, 
                            token_from: str, 
                            token_to: str, 
                            amount: float, 
                            redis_cache_service,
                            all_prices: dict,
                            eth_price: Decimal) -> List[TransactionOption]:
    """Przetwarza pule DEX równolegle z asynchronicznymi wywołaniami blockchain."""

    pool_tasks = []
    for pair, data in pools.items():
        tokens = pair.split('/')
        if set(tokens) == {token_from, token_to}:
            pool_tasks.append(
                process_single_pool(
                    dex_name, pair, data, dex_service, token_from, token_to, amount,
                    redis_cache_service, all_prices, eth_price
                )
            )
    
    results = await asyncio.gather(*pool_tasks, return_exceptions=True)
    
    options = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Błąd przetwarzania puli w {dex_name}: {result}")
        elif result is not None:
            options.append(result)
    
    return options