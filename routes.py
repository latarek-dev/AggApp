from decimal import Decimal
from fastapi import APIRouter, HTTPException
from models import ExchangeRequest
from config import UNISWAP_POOLS, SUSHISWAP_POOLS, CAMELOT_POOLS, TOKEN_IDS, uniswap_abi, camelot_abi
from utils import get_prices_from_coingecko, get_uniswap_price, get_camelot_price, get_cached_price, set_cached_price

exchange_router = APIRouter()

@exchange_router.post("/exchange")
async def exchange(request: ExchangeRequest):
    print(f"Otrzymano żądanie z danymi: {request}")
    token_from = request.token_from.upper()
    token_to = request.token_to.upper()
    amount = request.amount
    print(f"Token_from: {token_from}, Token_to: {token_to}, Amount: {amount}")

    token_ids = [TOKEN_IDS[token] for token in [token_from, token_to] if token in TOKEN_IDS]
    print(f"Token IDs do pobrania z CoinGecko: {token_ids}")
    prices = get_prices_from_coingecko(token_ids)
    print(f"Pobrane ceny z CoinGecko: {prices}")

    all_options = []

    for dex, pools, dex_abi, price_func in [
        ("Uniswap", UNISWAP_POOLS, uniswap_abi, get_uniswap_price),
        ("SushiSwap", SUSHISWAP_POOLS, uniswap_abi, get_uniswap_price),
        ("Camelot", CAMELOT_POOLS, camelot_abi, get_camelot_price)
    ]:
        print(f"Przetwarzanie pooli z DEX: {dex}")
        for pair, data in pools.items():
            print(f"Sprawdzanie pary: {pair}")
            tokens = pair.split('/')
            if set(tokens) == {token_from, token_to}:
                print(f"Znaleziono odpowiednią parę: {pair}")
                pool_name = f"{dex.lower()}_{pair}"

                # Sprawdzamy, czy cena jest w cache
                cached_price = await get_cached_price(pool_name)
                if cached_price is None:
                    print(f"Cena nie znaleziono w cache dla {pool_name}, pobieramy...")
                    # Jeśli nie ma w cache, pobieramy cenę i cache'ujemy
                    price_base, price_token = price_func(data["address"], data["decimals"], dex_abi)
                    print(f"Obliczone ceny: {price_base}, {price_token}")
                    if price_base and price_token:
                        await set_cached_price(pool_name, price_base)
                        cached_price = price_base
                    else:
                        price_base = Decimal(0)  # Default value to avoid uninitialized reference
                        price_token = Decimal(0)  # Default value to avoid uninitialized reference
                else:
                    price_base = cached_price
                    price_token = Decimal(1) / Decimal(price_base) if price_base > 0 else Decimal(0)
                    print(f"Znaleziona cena w cache: {cached_price}")

                # Obliczanie kwoty wymiany
                exchange_amount = Decimal(amount) * Decimal(price_token) if token_from == tokens[0] else Decimal(amount) * Decimal(price_base)
                print(f"Obliczona kwota wymiany: {exchange_amount}")
                token_from_price = prices.get(TOKEN_IDS.get(token_from), {}).get("usd", 1)
                token_to_price = prices.get(TOKEN_IDS.get(token_to), {}).get("usd", 1)

                value_from_usd = amount * token_from_price
                value_to_usd = float(exchange_amount) * token_to_price

                all_options.append((dex, pair, exchange_amount, value_from_usd, value_to_usd))

    all_options.sort(key=lambda x: x[2], reverse=True)
    print(f"Opcje wymiany po sortowaniu: {all_options}")

    if all_options:
        best_pool = all_options[0]
        print(f"Najlepsza opcja: {best_pool}")
        return {
            "best_option": {
                "dex": best_pool[0],
                "pair": best_pool[1],
                "amount_from": amount,
                "amount_to": float(best_pool[2]),
                "value_from_usd": best_pool[3],
                "value_to_usd": best_pool[4]
            },
            "options": [
                {
                    "dex": dex,
                    "pair": pair,
                    "amount_from": amount,
                    "amount_to": float(exchange_amount),
                    "value_from_usd": value_from_usd,
                    "value_to_usd": value_to_usd
                } for dex, pair, exchange_amount, value_from_usd, value_to_usd in all_options[1:]
            ]
        }
    else:
        print("Brak dostępnych opcji wymiany.")
        raise HTTPException(status_code=404, detail="No exchange options available.")
