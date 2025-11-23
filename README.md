# AggApp – Agregator wymiany tokenów

Aplikacja do porównywania kursów wymiany tokenów na różnych DEX-ach w sieci Arbitrum.

Na projekt składa się:
- **backend**,
- **frontend**,
- uruchamiane razem przez **Docker Compose**.  

<img width="1920" height="912" alt="Agregator-Wymiany-Tokenów-11-23-2025_11_59_PM" src="https://github.com/user-attachments/assets/4c0d1574-802d-4395-9ef0-338f5a32ebda" />
<img width="1920" height="912" alt="Agregator-Wymiany-Tokenów-11-23-2025_11_59_PM (1)" src="https://github.com/user-attachments/assets/aec56430-5524-4516-91a7-5f64bf74d313" />

---

## Technologie

- **Backend**: Python 3.10, FastAPI, Web3.py, Redis, NumPy
- **Frontend**: React, TailwindCSS, Nginx  
- **Infra**: Docker
- **Sieć blockchain**: Arbitrum One

---

## Instrukcja

### 1. Wymagania
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) zainstalowany i uruchomiony
- Porty **8000** i **8080** wolne (lub zmień w `docker-compose.yml`)

### 2. Klonowanie repozytorium
```bash
git clone https://github.com/latarek-dev/AggApp.git
cd AggApp
```

### 3. Plik `.env`
Skopiuj przykładowy plik środowiskowy:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Domyślna zawartość (można zostawić bez zmian):
```env
# Backend
RPC_URL=https://arb1.arbitrum.io/rpc
REDIS_URL=redis://:redispw@redis:6379/0
```

**Uwaga**: Jeśli nie masz pliku `.env.example`, możesz utworzyć `.env` ręcznie lub pominąć ten krok - aplikacja użyje domyślnych wartości z `docker-compose.yml`.

### 4. Budowanie i uruchamianie
```bash
docker compose up -d --build
```

Podgląd logów:
```bash
# Logi backend
docker compose logs -f api

# Logi frontend
docker compose logs -f frontend

# Wszystkie logi
docker compose logs -f
```


### 5. Test działania
- Backend API:  
  [http://localhost:8000/](http://localhost:8000/)  
  Oczekiwany wynik:
  ```json
  {"message": "API działa poprawnie"}
  ```

- **Frontend**:  
  [http://localhost:8080/](http://localhost:8080/)  

### 6. Podłączenie portfela
Aby wykonywać wymiany kryptowalut, musisz podłączyć portfel kryptowalutowy do aplikacji. Aplikacja obsługuje przede wszystkim następujące portfele:

- **[MetaMask](https://metamask.io/)**
- **[Rabby](https://rabby.io/)**

**Instrukcja:**
1. Zainstaluj rozszerzenie portfela w przeglądarce (MetaMask lub Rabby)
2. Utwórz lub zaimportuj portfel
3. Przełącz sieć na **Arbitrum One** w portfelu
4. W aplikacji kliknij przycisk **"Połącz Portfel"** w prawym górnym rogu
5. Wybierz swój portfel z listy i zatwierdź połączenie

**Uwaga**: Upewnij się, że masz ETH na Arbitrum One do opłat za transakcje (gas fees).

### 7. Zatrzymywanie aplikacji
```bash
docker compose down
```

---
