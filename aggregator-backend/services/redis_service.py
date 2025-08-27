import redis.asyncio as redis
from typing import Optional, Any
from config import REDIS_URL
import asyncio
from contextlib import asynccontextmanager

class RedisService:
    """
    Singleton serwis Redis zarządzający jednym połączeniem dla całej aplikacji.
    """
    
    _instance = None
    _client: Optional[redis.Redis] = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance
    
    async def _ensure_connection(self) -> redis.Redis:
        """Zapewnia aktywne połączenie z Redis."""
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    self._client = redis.from_url(
                        REDIS_URL, 
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=10,
                        health_check_interval=30,
                        retry_on_timeout=True
                    )
                    try:
                        await self._client.ping()
                        print(f"Utworzono nowe połączenie z Redis: {REDIS_URL}")
                    except Exception as e:
                        print(f"Błąd połączenia z Redis: {e}")
                        self._client = None
                        raise
        else:
            # Sprawdzenie czy połączenie jest aktywne
            try:
                await self._client.ping()
            except Exception:
                # Połączenie zostało utracone, odtwarzamy je
                async with self._lock:
                    try:
                        if self._client:
                            await self._client.close()
                    except Exception:
                        pass
                    
                    self._client = redis.from_url(
                        REDIS_URL, 
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=10,
                        health_check_interval=30,
                        retry_on_timeout=True
                    )
                    await self._client.ping()
                    print(f"Odtworzono połączenie z Redis: {REDIS_URL}")
        
        return self._client
    
    async def connect(self) -> bool:
        """Publiczna metoda do inicjalizacji połączenia."""
        try:
            await self._ensure_connection()
            return True
        except Exception as e:
            print(f"Błąd podczas łączenia z Redis: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Pobiera wartość z Redis."""
        try:
            client = await self._ensure_connection()
            return await client.get(key)
        except Exception as e:
            print(f"Błąd podczas pobierania z Redis: {e}")
            return None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Zapisuje wartość w Redis."""
        try:
            client = await self._ensure_connection()
            result = await client.set(key, value, ex=ex)
            return bool(result)
        except Exception as e:
            print(f"Błąd podczas zapisywania w Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Sprawdza czy klucz istnieje w Redis."""
        try:
            client = await self._ensure_connection()
            result = await client.exists(key)
            return bool(result)
        except Exception as e:
            print(f"Błąd podczas sprawdzania istnienia klucza w Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Usuwa klucz z Redis."""
        try:
            client = await self._ensure_connection()
            result = await client.delete(key)
            return bool(result)
        except Exception as e:
            print(f"Błąd podczas usuwania klucza z Redis: {e}")
            return False
    
    async def close(self):
        """Zamyka połączenie z Redis."""
        if self._client:
            try:
                await self._client.close()
                self._client = None
                print("Zamknięto połączenie z Redis")
            except Exception as e:
                print(f"Błąd podczas zamykania połączenia Redis: {e}")
                self._client = None
    
    @asynccontextmanager
    async def get_client(self):
        """Context manager do bezpośredniego dostępu do klienta Redis."""
        client = await self._ensure_connection()
        try:
            yield client
        except Exception as e:
            print(f"Błąd w kontekście Redis: {e}")
            raise


redis_service = RedisService()
