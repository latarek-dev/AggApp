import requests
import time
from decimal import Decimal
from config import w3, get_redis

async def get_cached_price(pool_name):
    """Pobiera cenę z cache Redis, jeśli jest dostępna."""
    redis = await get_redis()
    print(f"Połączenie z Redis: {redis}")  # Debugowanie
    price = await redis.get(pool_name)
    if price:
        print(f"Znaleziono cenę w Redis: {price}")
    else:
        print(f"Nie znaleziono ceny w Redis")
    return float(price) if price else None

async def set_cached_price(pool_name, price, ttl=60):
    """Ustawia cenę w cache Redis na określony czas (domyślnie 60 sek.)."""
    redis = await get_redis()
    print(f"Połączenie z Redis: {redis}")  # Debugowanie
    # Konwersja ceny na float, jeśli jest to obiekt Decimal
    if isinstance(price, Decimal):
        price = float(price)
    await redis.set(pool_name, price, ex=ttl)
    print(f"Zapisano cenę {price} w Redis dla {pool_name}")  # Debugowanie

def get_prices_from_coingecko(token_ids):
    ids_string = ",".join(token_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"

    for _ in range(3):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Błąd CoinGecko: {e}, ponawiam próbę...")
            time.sleep(1)

    return {}

# Funkcja obliczająca cenę z puli Uniswap lub SushiSwap (na podstawie sqrtPriceX96)
def get_uniswap_price(pool_address, token_decimals, dex_abi):
    try:
        pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
    
        # Uniswap V3 - użycie slot0() do uzyskania sqrtPriceX96
        slot0_data = pool_contract.functions.slot0().call()
        sqrt_price_x96 = slot0_data[0]
        sqrt_price = Decimal(sqrt_price_x96) / Decimal(2 ** 96)
        price_in_base = sqrt_price ** 2

        decimals_token, decimals_base = token_decimals
        if decimals_token > decimals_base:
            adjusted_price = price_in_base / Decimal(10 ** (decimals_token - decimals_base))
        else:
            adjusted_price = price_in_base * Decimal(10 ** (decimals_base - decimals_token))
        inverse_price = Decimal(1) / adjusted_price if adjusted_price != 0 else Decimal(0)
        return adjusted_price, inverse_price
    except Exception as e:
        print(f"Błąd podczas pobierania stanu puli {pool_address}: {e}")
        return None, None

def get_camelot_price(pool_address, token_decimals, dex_abi):
    try:
        pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
        global_state = pool_contract.functions.globalState().call()

        # Debugowanie: Sprawdzamy wartość global_state przed przeliczeniem
        print(f"global_state: {global_state}")

        decimals_token, decimals_base = token_decimals  # Rozdzielamy krotkę
        sqrt_price = Decimal(global_state[0]) / Decimal(2 ** 96)  # Podziel przez 10^18 bez dodatkowych kroków
        price = sqrt_price ** 2

        # Debugowanie: Sprawdzamy wynik ceny po przekształceniu
        print(f"Price after transforming sqrtPrice: {price}")

            # Dostosowanie ceny względem różnicy decymalnych
        if decimals_token > decimals_base:
            price = price / Decimal(10 ** (decimals_token - decimals_base))
        else:
            price = price * Decimal(10 ** (decimals_base - decimals_token))

            # Debugowanie: Sprawdzamy wartość ceny po dostosowaniu
        print(f"Adjusted price: {price}")
        
        inverse_price = Decimal(1) / price if price > 0 else Decimal(0)
        
        return price, inverse_price
    except Exception as e:
        print(f"Błąd Camelot {pool_address}: {e}")
        return None, None