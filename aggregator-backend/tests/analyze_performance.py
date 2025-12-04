"""
Analiza wydajności backendu AggApp

Analiza wyników testów wydajnościowych dla różnych scenariuszy:
1. Systematyczny - sekwencyjne requesty dla wszystkich par
2. Losowy - losowe pary, sekwencyjnie
3. Losowy 10 klientów - losowe pary, 10 równoczesnych workerów
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator, SecondLocator
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Wczytanie danych
files = {
    'Systematyczny': 'exchange_performance_systematic.json',
    'Losowy': 'exchange_performance_random.json',
    'Losowy 10 klientów': 'exchange_performance_random_10_clients.json'
}

print("Wczytuję dane...")
data = {}
for name, filename in files.items():
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data[name] = json.load(f)
        print(f"✓ Wczytano {name}: {len(data[name]['results'])} requestów")
    except FileNotFoundError:
        print(f"✗ Nie znaleziono pliku: {filename}")

if not data:
    print("Brak danych do analizy!")
    exit(1)


print("\nPrzygotowuję dane...")
dfs = {}

for name, json_data in data.items():
    results = json_data['results']
    metadata = json_data['metadata']
    
    rows = []
    for result in results:
        req = result['request']
        resp = result['response']
        
        rows.append({
            'timestamp': result['timestamp'],
            'token_from': req['token_from'],
            'token_to': req['token_to'],
            'pair': f"{req['token_from']}->{req['token_to']}",
            'amount': req['amount'],
            'status_code': resp['status_code'],
            'ok': resp['ok'],
            'elapsed_ms': resp['elapsed_ms'],
            'elapsed_s': resp['elapsed_ms'] / 1000,
            'n_options': resp['n_options'] if resp['n_options'] is not None else 0,
            'error': resp.get('error', ''),
            'mode': metadata.get('mode', name),
            'concurrent_workers': metadata.get('concurrent_workers', 1)
        })
    
    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    dfs[name] = df
    print(f"\n{name}:")
    print(f"  Liczba requestów: {len(df)}")
    print(f"  Sukces: {df['ok'].sum()} ({df['ok'].mean()*100:.1f}%)")
    print(f"  Błędy: {(~df['ok']).sum()} ({(~df['ok']).mean()*100:.1f}%)")

# Statystyki podstawowe
print("\n" + "="*100)
print("STATYSTYKI PODSTAWOWE")
print("="*100)

stats_summary = []

for name, df in dfs.items():
    successful = df[df['ok'] == True]
    
    stats_summary.append({
        'Scenariusz': name,
        'Liczba requestów': len(df),
        'Sukces': df['ok'].sum(),
        'Błędy': (~df['ok']).sum(),
        'Sukces [%]': f"{df['ok'].mean()*100:.1f}",
        'Średni czas [ms]': f"{successful['elapsed_ms'].mean():.2f}",
        'Mediana [ms]': f"{successful['elapsed_ms'].median():.2f}",
        'Min [ms]': f"{successful['elapsed_ms'].min():.2f}",
        'Max [ms]': f"{successful['elapsed_ms'].max():.2f}",
        'Q25 [ms]': f"{successful['elapsed_ms'].quantile(0.25):.2f}",
        'Q75 [ms]': f"{successful['elapsed_ms'].quantile(0.75):.2f}",
        'Odch. std [ms]': f"{successful['elapsed_ms'].std():.2f}",
        'Średnia opcji': f"{successful['n_options'].mean():.2f}",
        'Czas całkowity [s]': data[name]['metadata'].get('total_elapsed_seconds', 0)
    })

stats_df = pd.DataFrame(stats_summary)
print(stats_df.to_string(index=False))

print("\n" + "="*100)
print("EKSPORT DO EXCELA")
print("="*100)

excel_filename = 'analiza_wydajnosci.xlsx'

try:
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        # Arkusz 1: Statystyki podsumowujące
        stats_df.to_excel(writer, sheet_name='Statystyki', index=False)
        
        # Arkusz 2-4: Szczegółowe dane dla każdego scenariusza
        for name, df in dfs.items():
            sheet_name = name[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Arkusz 5: Porównanie czasów odpowiedzi
        comparison_data = []
        for name, df in dfs.items():
            successful = df[df['ok'] == True]
            comparison_data.append({
                'Scenariusz': name,
                'Średnia [ms]': successful['elapsed_ms'].mean(),
                'Mediana [ms]': successful['elapsed_ms'].median(),
                'Min [ms]': successful['elapsed_ms'].min(),
                'Max [ms]': successful['elapsed_ms'].max(),
                'Q25 [ms]': successful['elapsed_ms'].quantile(0.25),
                'Q75 [ms]': successful['elapsed_ms'].quantile(0.75),
                'Std [ms]': successful['elapsed_ms'].std(),
                'P95 [ms]': successful['elapsed_ms'].quantile(0.95),
                'P99 [ms]': successful['elapsed_ms'].quantile(0.99)
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(writer, sheet_name='Porównanie', index=False)
    
    print(f"✓ Dane wyeksportowane do: {excel_filename}")
except Exception as e:
    print(f"✗ Błąd podczas eksportu do Excela: {e}")

# Wykresy
print("\n" + "="*100)
print("GENEROWANIE WYKRESÓW")
print("="*100)

# 1. Histogramy czasów odpowiedzi
print("1. Histogramy czasów odpowiedzi...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, (name, df) in enumerate(dfs.items()):
    successful = df[df['ok'] == True]
    
    axes[idx].hist(successful['elapsed_ms'], bins=50, alpha=0.7, edgecolor='black')
    axes[idx].axvline(successful['elapsed_ms'].mean(), color='red', linestyle='--', 
                      label=f'Średnia: {successful["elapsed_ms"].mean():.0f} ms')
    axes[idx].axvline(successful['elapsed_ms'].median(), color='green', linestyle='--', 
                      label=f'Mediana: {successful["elapsed_ms"].median():.0f} ms')
    axes[idx].set_xlabel('Czas odpowiedzi [ms]')
    axes[idx].set_ylabel('Liczba requestów')
    axes[idx].set_title(f'{name}\n(n={len(successful)})')
    axes[idx].legend()
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('histogramy_czasow.png', dpi=300, bbox_inches='tight')
print("  ✓ Zapisano: histogramy_czasow.png")
plt.close()

# 2. Wykresy czasowe
print("2. Wykresy czasowe...")
fig, axes = plt.subplots(3, 1, figsize=(16, 12))

for idx, (name, df) in enumerate(dfs.items()):
    successful = df[df['ok'] == True].copy()
    successful = successful.sort_values('timestamp')
    
    axes[idx].plot(successful['timestamp'], successful['elapsed_ms'], 
                  marker='o', markersize=4, alpha=0.7, linewidth=1.5, 
                  color='#2E86AB', markeredgecolor='white', markeredgewidth=0.5)
    axes[idx].axhline(successful['elapsed_ms'].mean(), color='red', 
                     linestyle='--', linewidth=2, label=f'Średnia: {successful["elapsed_ms"].mean():.0f} ms')
    axes[idx].axhline(successful['elapsed_ms'].median(), color='green', 
                     linestyle='--', linewidth=2, label=f'Mediana: {successful["elapsed_ms"].median():.0f} ms')
    axes[idx].set_xlabel('Czas', fontsize=11, fontweight='bold')
    axes[idx].set_ylabel('Czas odpowiedzi [ms]', fontsize=11, fontweight='bold')
    axes[idx].set_title(f'{name} - Czas odpowiedzi w czasie', fontsize=13, fontweight='bold', pad=10)
    axes[idx].legend(loc='upper right', fontsize=10)
    axes[idx].grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    time_span = (successful['timestamp'].max() - successful['timestamp'].min()).total_seconds()
    
    date_format = DateFormatter('%H:%M:%S')
    axes[idx].xaxis.set_major_formatter(date_format)
    
    if time_span < 60:
        axes[idx].xaxis.set_major_locator(SecondLocator(interval=max(5, int(time_span / 10))))
    elif time_span < 3600:
        axes[idx].xaxis.set_major_locator(MinuteLocator(interval=max(1, int(time_span / 600))))
    else:
        axes[idx].xaxis.set_major_locator(MinuteLocator(interval=max(5, int(time_span / 3600))))
    
    axes[idx].tick_params(axis='x', rotation=45)
    plt.setp(axes[idx].xaxis.get_majorticklabels(), ha='right')
    
    axes[idx].margins(x=0.02)

plt.tight_layout(rect=[0, 0.02, 1, 0.98])
plt.savefig('wykresy_czasowe.png', dpi=300, bbox_inches='tight', pad_inches=0.2)
print("  ✓ Zapisano: wykresy_czasowe.png")
plt.close()

# Szczegółowa tabela porównawcza
print("\n" + "="*100)
print("SZCZEGÓŁOWE PORÓWNANIE")
print("="*100)

detailed_comparison = []

for name, df in dfs.items():
    successful = df[df['ok'] == True]
    metadata = data[name]['metadata']
    
    detailed_comparison.append({
        'Scenariusz': name,
        'Tryb': metadata.get('mode', 'N/A'),
        'Workers': metadata.get('concurrent_workers', 1),
        'Requestów': len(df),
        'Sukces': df['ok'].sum(),
        'Błędy': (~df['ok']).sum(),
        'Sukces [%]': f"{df['ok'].mean()*100:.1f}",
        'Średnia [ms]': f"{successful['elapsed_ms'].mean():.2f}",
        'Mediana [ms]': f"{successful['elapsed_ms'].median():.2f}",
        'Min [ms]': f"{successful['elapsed_ms'].min():.2f}",
        'Max [ms]': f"{successful['elapsed_ms'].max():.2f}",
        'P25 [ms]': f"{successful['elapsed_ms'].quantile(0.25):.2f}",
        'P75 [ms]': f"{successful['elapsed_ms'].quantile(0.75):.2f}",
        'P95 [ms]': f"{successful['elapsed_ms'].quantile(0.95):.2f}",
        'P99 [ms]': f"{successful['elapsed_ms'].quantile(0.99):.2f}",
        'Std [ms]': f"{successful['elapsed_ms'].std():.2f}",
        'Czas całkowity [s]': f"{metadata.get('total_elapsed_seconds', 0):.2f}",
        'Requestów/s': f"{len(df) / metadata.get('total_elapsed_seconds', 1):.2f}",
        'Średnia opcji': f"{successful['n_options'].mean():.2f}"
    })

detailed_df = pd.DataFrame(detailed_comparison)
print(detailed_df.to_string(index=False))

# Eksport szczegółowej tabeli
try:
    detailed_df.to_excel('szczegolowe_porownanie.xlsx', index=False)
    print("\n✓ Szczegółowe porównanie wyeksportowane do: szczegolowe_porownanie.xlsx")
except Exception as e:
    print(f"\n✗ Błąd podczas eksportu: {e}")

# Statystyki per para tokenów
print("\n" + "="*100)
print("STATYSTYKI PER PARA TOKENÓW")
print("="*100)

for name, df in dfs.items():
    successful = df[df['ok'] == True]
    
    pair_stats = successful.groupby('pair')['elapsed_ms'].agg([
        'count', 'mean', 'median', 'min', 'max', 'std'
    ]).round(2)
    pair_stats.columns = ['Liczba', 'Średnia [ms]', 'Mediana [ms]', 'Min [ms]', 'Max [ms]', 'Std [ms]']
    pair_stats = pair_stats.sort_values('Średnia [ms]', ascending=False)
    
    print(f"\n{name}:")
    print(pair_stats.to_string())

# Wnioski i podsumowanie
print("\n" + "="*100)
print("WNIOSKI I PODSUMOWANIE")
print("="*100)

for name, df in dfs.items():
    successful = df[df['ok'] == True]
    metadata = data[name]['metadata']
    
    print(f"\n{name}:")
    print(f"  • Średni czas odpowiedzi: {successful['elapsed_ms'].mean():.0f} ms")
    print(f"  • Mediana: {successful['elapsed_ms'].median():.0f} ms")
    print(f"  • P95: {successful['elapsed_ms'].quantile(0.95):.0f} ms")
    print(f"  • Współczynnik sukcesu: {df['ok'].mean()*100:.1f}%")
    print(f"  • Throughput: {len(df) / metadata.get('total_elapsed_seconds', 1):.2f} requestów/s")
    
    # Analiza cache
    successful_copy = successful.copy()
    successful_copy['occurrence'] = successful_copy.groupby('pair').cumcount() + 1
    first = successful_copy[successful_copy['occurrence'] == 1]['elapsed_ms']
    subsequent = successful_copy[successful_copy['occurrence'] > 1]['elapsed_ms']
    
    if len(first) > 0 and len(subsequent) > 0:
        cache_improvement = ((first.mean() - subsequent.mean()) / first.mean()) * 100
        print(f"  • Poprawa dzięki cache: {cache_improvement:.1f}% (pierwsze: {first.mean():.0f}ms, kolejne: {subsequent.mean():.0f}ms)")

print("\n" + "="*100)
print("ANALIZA ZAKOŃCZONA")
print("="*100)
print("\nWygenerowane pliki:")
print("  • analiza_wydajnosci.xlsx - główny plik Excel z wszystkimi danymi")
print("  • szczegolowe_porownanie.xlsx - szczegółowe porównanie scenariuszy")
print("  • histogramy_czasow.png - histogramy rozkładów czasów")
print("  • wykresy_czasowe.png - wykresy czasowe")

