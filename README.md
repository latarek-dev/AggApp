# AggApp – Agregator wymiany tokenów

Projekt składa się z:
- **backendu** (FastAPI + Redis cache),
- **frontendu** (React + Tailwind, serwowany przez Nginx),
- uruchamianych razem przez **Docker Compose**.  

---

## Technologie

- **Backend**: Python 3.10, FastAPI, Web3.py, Redis, NumPy
- **Frontend**: React, TailwindCSS, Nginx  
- **Infra**: Docker
- **Sieć blockchain**: Arbitrum One

---

## Uruchamianie (Docker Compose)

### 1. Wymagania
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
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

Domyślna zawartość (można zostawić bez zmian):
```env
# Backend
RPC_URL=https://arb1.arbitrum.io/rpc
REDIS_URL=redis://:redispw@redis:6379/0
```

### 4. Budowanie i uruchamianie
```bash
docker compose up -d --build
```

Podgląd logów backendu:
```bash
docker compose logs -f api
```

Podgląd logów frontendu:
```bash
docker compose logs -f frontend
```

### 5. Test działania
- Backend API:  
  [http://localhost:8000/](http://localhost:8000/)  
  Oczekiwany wynik:
  ```json
  {"message": "API działa poprawnie"}
  ```

- Frontend (React przez Nginx):  
  [http://localhost:8080/](http://localhost:8080/)  

---

## Struktura repozytorium

```
AggApp/
│  .env.example         # szablon zmiennych środowiskowych
│  docker-compose.yml   # definicja usług Docker
│
├─ aggregator-backend/
│   ├─ Dockerfile
│   ├─ requirements.txt
│   ├─ config.py
│   ├─ main.py
│   └─ ...
│
├─ aggregator-frontend/
│   ├─ Dockerfile
│   ├─ nginx.conf
│   ├─ package.json
│   ├─ src/
│   └─ ...
```
