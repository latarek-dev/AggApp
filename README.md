# AggApp – Agregator wymiany tokenów (Arbitrum)

Projekt składa się z backendu (FastAPI) i bazy Redis, uruchamianych w kontenerach Dockera.  
Frontend (React + Tailwind) znajduje się w osobnym folderze i może być uruchamiany niezależnie lub również w Compose.

---

## 📦 Technologie

- **Backend**: Python 3.10, FastAPI, Web3.py, Redis (cache), NumPy (TOPSIS)  
- **Frontend**: React, TailwindCSS  
- **Infra**: Docker, Docker Compose  
- **Sieć blockchain**: Arbitrum One (RPC)

---

## 🚀 Uruchamianie (Docker Compose)

### 1. Wymagania
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (z włączonym WSL2 na Windows)  
- Git  

### 2. Klonowanie repozytorium
```bash
git clone https://github.com/twoj-repo/aggapp.git
cd aggapp
```

### 3. Plik `.env`
Skopiuj przykładowy plik środowiskowy:
```bash
cp .env.example .env
```

Domyślna zawartość (możesz zostawić bez zmian):
```env
# Backend
RPC_URL=https://arb1.arbitrum.io/rpc
REDIS_URL=redis://:redispw@redis:6379/0
```

> ⚠️ Prawdziwy `.env` nie jest wersjonowany w Git (jest w `.gitignore`).  

### 4. Budowanie i uruchamianie
```bash
docker compose up -d --build
```

Podgląd logów backendu:
```bash
docker compose logs -f api
```

### 5. Test działania
Otwórz w przeglądarce:
```
http://localhost:8000/
```

Oczekiwany wynik:
```json
{"message": "API działa poprawnie"}
```

---

## 🗂️ Struktura repozytorium

```
AggApp/
│  .env.example         # szablon zmiennych środowiskowych
│  docker-compose.yml   # definicja usług Docker (api + redis)
│
├─ aggregator-backend/  # backend (FastAPI, Redis, Web3.py)
│   ├─ Dockerfile
│   ├─ requirements.txt
│   ├─ config.py
│   ├─ main.py
│   └─ ...
│
├─ aggregator-frontend/ # frontend (React + Tailwind)
│   ├─ package.json
│   ├─ src/
│   └─ ...
```

---

## 🖥️ Frontend (dev lokalny)

Frontend można uruchomić niezależnie od backendu (poza Dockerem):

```bash
cd aggregator-frontend
npm install
npm start
```

Aplikacja frontendowa uruchomi się domyślnie na:  
👉 [http://localhost:3000](http://localhost:3000)

> W trybie deweloperskim frontend łączy się z backendem pod `http://localhost:8000/api`.

---

## 📊 Ranking TOPSIS

Backend po pobraniu ofert z DEX-ów (Uniswap v3, SushiSwap v3, Camelot/Algebra) sortuje je przy pomocy metody **TOPSIS**.  
Brane pod uwagę kryteria:
- `amount_to` – ilość tokenu wyjściowego (benefit),  
- `slippage` – poślizg cenowy (cost),  
- `liquidity` – płynność puli (benefit),  
- `dex_fee` – prowizja DEX-u (cost),  
- `gas_cost` – koszt gazu (cost).  

Wynik → opcje uporządkowane od najlepszego kompromisu do najgorszego.

---

## 📝 Notatki developerskie

- `.env` → lokalny, prywatny (nie commitować do Git).  
- `.env.example` → commitujemy jako szablon dla innych.  
- Backend łączy się z Redisem przez `redis:6379` (nazwa usługi w Compose).  
- Po każdej zmianie w `requirements.txt` → przebuduj kontener:
  ```bash
  docker compose up -d --build
  ```

---
