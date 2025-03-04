from web3 import Web3
import json
import requests
from decimal import Decimal, getcontext

# Ustawienie precyzji dla obliczeń dziesiętnych
getcontext().prec = 50

# Połączenie z siecią Arbitrum
w3 = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))
if w3.is_connected():
    print("Połączono z siecią Arbitrum!")
else:
    print("Nie udało się połączyć z siecią!")

# Wczytaj ABI Uniswap V3 i SushiSwap (zakładając, że masz odpowiednie ABI)
with open('uniswap_abi.json') as f:
    uniswap_abi = json.load(f)

# Słownik par tokenów z pulami i decymalnymi
UNISWAP_POOLS = {
    "USDC/ETH": {"address": "0xC6962004f452bE9203591991D15f6b388e09E8D0", "decimals": (6, 18)},
    "USDT/ETH": {"address": "0x641C00A822e8b671738d32a431a4Fb6074E5c79d", "decimals": (6, 18)},
    "DAI/ETH":  {"address": "0xA961F0473dA4864C5eD28e00FcC53a3AAb056c1b", "decimals": (18, 18)},
    "USDC/DAI": {"address": "0x7CF803e8d82A50504180f417B8bC7a493C0a0503", "decimals": (18, 6)},
    "USDT/DAI": {"address": "0x7f580f8A02b759C350E6b8340e7c2d4b8162b6a9", "decimals": (6, 18)},
    "ETH/WBTC": {"address": "0x2f5e87C9312fa29aed5c179E456625D79015299c", "decimals": (18, 8)},
}

SUSHISWAP_POOLS = {
    "USDC/ETH": {"address": "0xf3Eb87C1F6020982173C908E7eB31aA66c1f0296", "decimals": (6, 18)},
    "USDT/ETH": {"address": "0x96aDA81328abCe21939A51D971A63077e16db26E", "decimals": (6, 18)},
    "DAI/ETH":  {"address": "0x3370EA4a1640C657bDD94D71325541bA927f5Aef", "decimals": (18, 18)},
    "USDC/DAI": {"address": "0x5DcF1Aa6B3422D8A59dc0e00904E02A1c1ea5a58", "decimals": (18, 6)},
    "USDT/DAI": {"address": "0xCc2B91d28d754DFF160d0924e16e6d213cBD24F8", "decimals": (6, 18)},
    "ETH/WBTC": {"address": "0x6F10667F314498649eb2f80da244e8c6E9f031d5", "decimals": (18, 8)},
}

# Słownik tokenów i ich identyfikatorów na CoinGecko
TOKEN_IDS = {
    "USDC": "usd-coin",          # USDC na CoinGecko to 'usd-coin'
    "USDT": "tether",            # USDT na CoinGecko to 'tether'
    "DAI":  "dai",               # DAI na CoinGecko to 'dai'
    "ETH":  "ethereum",          # ETH na CoinGecko to 'ethereum'
    "WBTC": "wrapped-bitcoin"    # WBTC na CoinGecko to 'wrapped-bitcoin'
}

# Funkcja pobierająca ceny dla wielu tokenów jednocześnie z CoinGecko
def get_prices_from_coingecko(token_ids):
    ids_string = ",".join(token_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print(f"Nie udało się pobrać cen z CoinGecko: {e}")
        return {}

# Pobierz ceny wszystkich interesujących tokenów na raz
coingecko_prices = get_prices_from_coingecko(list(TOKEN_IDS.values()))
print("Ceny z CoinGecko:")
for tid, price_data in coingecko_prices.items():
    print(f" {tid}: {price_data.get('usd')} USD")
print()  # pusty wiersz dla przejrzystości

# Funkcja obliczająca cenę z puli Uniswap lub SushiSwap (na podstawie sqrtPriceX96)
# Funkcja obliczająca cenę z puli Uniswap lub SushiSwap (na podstawie rezerw)
# Funkcja obliczająca cenę z puli Uniswap lub SushiSwap (na podstawie rezerw lub sqrtPriceX96)
def get_pool_price(pool_address, token_decimals, dex_abi):
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


# Przetwarzanie każdej pary z Uniswap
for pair, data in UNISWAP_POOLS.items():
    price_base, price_token = get_pool_price(data["address"], data["decimals"], uniswap_abi)
    if price_base and price_token:
        token_1, token_2 = pair.split('/')
        token_1_id = TOKEN_IDS.get(token_1.upper())
        token_2_id = TOKEN_IDS.get(token_2.upper())

        # Pobieramy ceny z wcześniej pobranych danych z CoinGecko
        token_1_price = coingecko_prices.get(token_1_id, {}).get("usd")
        token_2_price = coingecko_prices.get(token_2_id, {}).get("usd")

        print(f"{pair} (Uniswap):")
        print(f"  Cena 1 {token_2} = {price_base:.6f} {token_1} | Cena 1 {token_1} = {price_token:.18f} {token_2}")
        print(f"  CoinGecko - Cena 1 {token_2} = {token_2_price} USD | Cena 1 {token_1} = {token_1_price} USD\n")

# Przetwarzanie każdej pary z SushiSwap
for pair, data in SUSHISWAP_POOLS.items():
    price_base, price_token = get_pool_price(data["address"], data["decimals"], uniswap_abi)
    if price_base and price_token:
        token_1, token_2 = pair.split('/')
        token_1_id = TOKEN_IDS.get(token_1.upper())
        token_2_id = TOKEN_IDS.get(token_2.upper())

        # Pobieramy ceny z wcześniej pobranych danych z CoinGecko
        token_1_price = coingecko_prices.get(token_1_id, {}).get("usd")
        token_2_price = coingecko_prices.get(token_2_id, {}).get("usd")

        print(f"{pair} (SushiSwap):")
        print(f"  Cena 1 {token_2} = {price_base:.6f} {token_1} | Cena 1 {token_1} = {price_token:.18f} {token_2}")
        print(f"  CoinGecko - Cena 1 {token_2} = {token_2_price} USD | Cena 1 {token_1} = {token_1_price} USD\n")
