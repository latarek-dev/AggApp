import argparse
import itertools
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests


def make_request(endpoint, payload, output_json, file_lock, stats_lock, stats, done_counter, total_requests):
    """
    Wykonuje pojedynczy request i zapisuje wynik do JSON.
    Thread-safe dzięki lockom.
    """
    request_start = time.perf_counter()
    error_msg = ""
    status_code = None
    n_options = None
    ok = False
    response_data = None
    token_from = payload["token_from"]
    token_to = payload["token_to"]
    amount = payload["amount"]

    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        elapsed_ms = (time.perf_counter() - request_start) * 1000
        status_code = resp.status_code
        ok = resp.ok

        if resp.ok:
            try:
                data = resp.json()
                options = data.get("options", [])
                n_options = len(options)
                response_data = data
                with stats_lock:
                    stats["success"] += 1
            except Exception as e:
                error_msg = f"JSON error: {e}"
                with stats_lock:
                    stats["errors"] += 1
        else:
            error_msg = resp.text[:200].replace("\n", " ").strip()
            with stats_lock:
                stats["errors"] += 1

    except requests.exceptions.Timeout:
        elapsed_ms = (time.perf_counter() - request_start) * 1000
        error_msg = "Timeout (30s)"
        with stats_lock:
            stats["errors"] += 1
    except requests.exceptions.ConnectionError:
        elapsed_ms = (time.perf_counter() - request_start) * 1000
        error_msg = "Connection error"
        with stats_lock:
            stats["errors"] += 1
    except Exception as e:
        elapsed_ms = (time.perf_counter() - request_start) * 1000
        error_msg = f"Request error: {type(e).__name__}: {str(e)[:100]}"
        with stats_lock:
            stats["errors"] += 1

    with stats_lock:
        stats["total"] += 1
        stats["total_time_ms"] += elapsed_ms
        done = done_counter[0] + 1
        done_counter[0] = done

    result_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request": {
            "token_from": token_from,
            "token_to": token_to,
            "amount": amount,
        },
        "response": {
            "status_code": status_code,
            "ok": ok,
            "elapsed_ms": round(elapsed_ms, 2),
            "n_options": n_options,
            "data": response_data,
            "error": error_msg,
        },
    }

    with file_lock:
        with open(output_json, "r+", encoding="utf-8") as f:
            test_data = json.load(f)
            test_data["results"].append(result_entry)
            f.seek(0)
            json.dump(test_data, f, indent=2, ensure_ascii=False)
            f.truncate()

    progress = (done / total_requests) * 100
    status_display = str(status_code) if status_code else 'N/A'
    print(
        f"[{done:4d}/{total_requests}] ({progress:5.1f}%) "
        f"{token_from:4s} -> {token_to:4s} | "
        f"status={status_display:>3s} | "
        f"ok={int(ok)} | "
        f"time={elapsed_ms:7.2f}ms | "
        f"options={n_options or 0:2d}"
    )

    return result_entry


def run_tests(
    base_url: str,
    tokens: list[str],
    amount: float,
    repeats: int,
    output_json: str,
    delay: float = 0.0,
    randomize: bool = False,
    concurrent: int = 1,
):
    """
    Wykonuje serię zapytań POST /api/exchange dla kombinacji par tokenów
    i zapisuje wyniki do pliku JSON (na bieżąco, po każdym requeście).
    
    Args:
        concurrent: Liczba równoczesnych requestów (workers). Domyślnie 1 (sekwencyjnie).
    """
    endpoint = base_url.rstrip("/") + "/exchange"

    all_pairs = [(t_from, t_to) for t_from, t_to in itertools.product(tokens, tokens) if t_from != t_to]

    if randomize:
        pairs_to_test = random.choices(all_pairs, k=repeats)
        mode = "LOSOWY"
    else:
        pairs_to_test = []
        for _ in range(repeats):
            pairs_to_test.extend(all_pairs)
        mode = "SYSTEMATYCZNY"

    print("=" * 70)
    print("Test wydajnościowy backendu AggApp")
    print("=" * 70)
    print(f"Base URL:     {base_url}")
    print(f"Endpoint:     {endpoint}")
    print(f"Tokens:       {tokens}")
    print(f"Możliwych par: {len(all_pairs)}")
    print(f"Tryb:         {mode}")
    print(f"Requestów:    {len(pairs_to_test)}")
    print(f"Równoczesne:  {concurrent} worker(s)")
    print(f"Delay:        {delay}s między requestami")
    print(f"Wyjście JSON: {output_json}")
    print("=" * 70)
    print()

    total_requests = len(pairs_to_test)
    stats = {
        "total": 0,
        "success": 0,
        "errors": 0,
        "total_time_ms": 0.0,
    }

    test_data = {
        "metadata": {
            "timestamp_start": datetime.utcnow().isoformat(),
            "base_url": base_url,
            "tokens": tokens,
            "amount": amount,
            "mode": mode,
            "total_pairs": len(all_pairs),
            "total_requests": total_requests,
            "randomize": randomize,
            "concurrent_workers": concurrent,
        },
        "results": []
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    file_lock = threading.Lock()
    stats_lock = threading.Lock()
    done_counter = [0]

    start_time = time.time()

    payloads = [
        {
            "token_from": token_from,
            "token_to": token_to,
            "amount": amount,
        }
        for token_from, token_to in pairs_to_test
    ]

    if concurrent == 1:
        for payload in payloads:
            make_request(endpoint, payload, output_json, file_lock, stats_lock, stats, done_counter, total_requests)
            if delay > 0:
                time.sleep(delay)
    else:
        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            futures = {
                executor.submit(make_request, endpoint, payload, output_json, file_lock, stats_lock, stats, done_counter, total_requests): payload
                for payload in payloads
            }
            
            for future in as_completed(futures):
                future.result()
                if delay > 0:
                    time.sleep(delay)


    total_elapsed = time.time() - start_time
    avg_time_ms = stats["total_time_ms"] / stats["total"] if stats["total"] > 0 else 0

    with open(output_json, "r+", encoding="utf-8") as f:
        test_data = json.load(f)
        test_data["metadata"]["timestamp_end"] = datetime.utcnow().isoformat()
        test_data["metadata"]["total_elapsed_seconds"] = round(total_elapsed, 2)
        test_data["statistics"] = {
            "total": stats["total"],
            "success": stats["success"],
            "errors": stats["errors"],
            "success_rate": round(stats["success"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0,
            "avg_time_ms": round(avg_time_ms, 2),
            "requests_per_second": round(stats["total"] / total_elapsed, 2) if total_elapsed > 0 else 0,
        }
        f.seek(0)
        json.dump(test_data, f, indent=2, ensure_ascii=False)
        f.truncate()

    print()
    print("=" * 70)
    print("Podsumowanie")
    print("=" * 70)
    print(f"Łącznie requestów:  {stats['total']}")
    print(f"Sukces:             {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Błędy:              {stats['errors']} ({stats['errors']/stats['total']*100:.1f}%)")
    print(f"Średni czas:        {avg_time_ms:.2f} ms")
    print(f"Całkowity czas:     {total_elapsed:.1f} s")
    print(f"Requestów/s:        {stats['total'] / total_elapsed:.2f}" if total_elapsed > 0 else "N/A")
    print(f"Wyniki zapisane:    {output_json}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Test wydajności backendu AggApp (POST /exchange).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  # Systematyczny test (każda para 5x)
  python performance_test.py
  
  # Losowy test (100 losowych requestów)
  python performance_test.py --random --repeats 100
  
  # Równoczesne requesty (10 równoczesnych użytkowników)
  python performance_test.py --concurrent 10 --repeats 20
  
  # Więcej powtórzeń z opóźnieniem
  python performance_test.py --repeats 10 --delay 0.2
  
  # Wybrane tokeny z równoczesnością
  python performance_test.py --tokens ETH USDC USDT --amount 5.0 --concurrent 5
        """,
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Bazowy URL backendu (bez /exchange). Domyślnie: http://localhost:8000",
    )
    parser.add_argument(
        "--tokens",
        nargs="+",
        default=["ETH", "USDC", "USDT", "DAI", "WBTC"],
        help="Lista symboli tokenów (spacje jako separator). Domyślnie: ETH USDC USDT DAI WBTC (wszystkie tokeny)",
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=1.0,
        help="Kwota wejściowa dla wszystkich zapytań. Domyślnie: 1.0",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="Liczba powtórzeń. Systematyczny: każda para N razy. Losowy: N losowych requestów. Domyślnie: 5",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Opóźnienie w sekundach między requestami. Domyślnie: 0.0 (brak opóźnienia). UWAGA: Przy --concurrent > 1 delay jest stosowany po każdym zakończonym requeście.",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Tryb losowy: losuj pary tokenów (imitacja naturalnego ruchu). Bez flagi: systematyczny test wszystkich par.",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Liczba równoczesnych requestów (workers). Domyślnie: 1 (sekwencyjnie). Użyj większej wartości (np. 10, 20) do testowania równoczesnych użytkowników i zalet cache.",
    )
    parser.add_argument(
        "--output",
        default="exchange_performance.json",
        help="Ścieżka do pliku JSON (pełne wyniki, zapisywane na bieżąco). Domyślnie: exchange_performance.json",
    )

    args = parser.parse_args()

    run_tests(
        base_url=args.base_url,
        tokens=args.tokens,
        amount=args.amount,
        repeats=args.repeats,
        output_json=args.output,
        delay=args.delay,
        randomize=args.random,
        concurrent=args.concurrent,
    )


if __name__ == "__main__":
    main()
