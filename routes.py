from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from models import ExchangeRequest
from config import UNISWAP_POOLS, SUSHISWAP_POOLS, CAMELOT_POOLS, TOKEN_IDS
from services import CoinGeckoService, UniswapService, SushiswapService, CamelotService, RedisCacheService

exchange_router = APIRouter()

# Dependency injection: Używamy CoinGeckoService oraz serwisów DEX
def get_services(redis_cache_service: RedisCacheService = Depends(),
                 coin_gecko_service: CoinGeckoService = Depends(), 
                 uniswap_service: UniswapService = Depends(),
                 sushiswap_service: SushiswapService = Depends(),
                 camelot_service: CamelotService = Depends()):
    return redis_cache_service, coin_gecko_service, uniswap_service, sushiswap_service, camelot_service

@exchange_router.post("/exchange")
async def exchange(request: ExchangeRequest,
                   services: tuple = Depends(get_services)):
    redis_cache_service, coin_gecko_service, uniswap_service, sushiswap_service, camelot_service = services
    print(f"Otrzymano żądanie z danymi: {request}")
    token_from = request.token_from.upper()
    token_to = request.token_to.upper()
    amount = request.amount
    print(f"Token_from: {token_from}, Token_to: {token_to}, Amount: {amount}")

    token_ids = [TOKEN_IDS[token] for token in [token_from, token_to] if token in TOKEN_IDS]
    print(f"Token IDs do pobrania z CoinGecko: {token_ids}")
    print(type(coin_gecko_service))
    prices = {token_id: coin_gecko_service.get_price(token_id) for token_id in token_ids}
    print(f"Pobrane ceny z CoinGecko: {prices}")

    all_options = []

    for dex, pools, dex_service, price_method in [
        ("Uniswap", UNISWAP_POOLS, uniswap_service, 'get_pair_price'),
        ("SushiSwap", SUSHISWAP_POOLS, sushiswap_service, 'get_pair_price'),
        ("Camelot", CAMELOT_POOLS, camelot_service, 'get_pair_price')
    ]:
        print(f"Przetwarzanie pooli z DEX: {dex}")
        for pair, data in pools.items():
            print(f"Sprawdzanie pary: {pair}")
            tokens = pair.split('/')
            if set(tokens) == {token_from, token_to}:
                print(f"Znaleziono odpowiednią parę: {pair}")
                pool_name = f"{dex.lower()}_{pair}"

                # Sprawdzamy, czy cena jest w cache
                cached_price = await redis_cache_service.get_cached_price(pool_name)
                if cached_price is None:
                    print(f"Cena nie znaleziono w cache dla {pool_name}, pobieramy...")
                    # Jeśli nie ma w cache, pobieramy cenę i cache'ujemy
                    price_base, price_token = getattr(dex_service, price_method)(data["address"], data["decimals"])                    
                    print(f"Obliczone ceny: {price_base}, {price_token}")
                    if price_base and price_token:
                        await redis_cache_service.set_cached_price(pool_name, price_base)
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
                token_from_price = prices.get(TOKEN_IDS.get(token_from), 1)  # Pobierz cenę tokenu
                token_to_price = prices.get(TOKEN_IDS.get(token_to), 1)  # Pobierz cenę tokenu docelowego

                value_from_usd = amount * float(token_from_price)
                value_to_usd = float(exchange_amount) * float(token_to_price)

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
