"""Limitação de tentativas em memória (janela fixa por chave).

O estado vive no processo: com vários workers/réplicas cada um conta separadamente, então
o limite efetivo é multiplicado. Nesse cenário, complemente com limites no proxy reverso
ou troque o armazenamento por um compartilhado (ex.: Redis).
"""

import math
import time
from collections.abc import Callable
from threading import Lock

from starlette.requests import Request

from app.core.config import settings
from app.core.exceptions import TooManyRequestsError


class RateLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: float,
        *,
        max_keys: int = 10_000,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self._clock = clock
        self._lock = Lock()
        # chave -> (início da janela, tentativas na janela)
        self._windows: dict[str, tuple[float, int]] = {}

    def check(self, key: str) -> None:
        """Lança TooManyRequestsError se a chave já esgotou a janela atual (sem contar)."""
        with self._lock:
            self._ensure_allowed(key, self._clock())

    def add(self, key: str) -> None:
        """Conta uma tentativa para a chave."""
        with self._lock:
            self._add(key, self._clock())

    def hit(self, key: str) -> None:
        """Verifica e conta a tentativa em uma única operação."""
        with self._lock:
            now = self._clock()
            self._ensure_allowed(key, now)
            self._add(key, now)

    def clear(self, key: str) -> None:
        with self._lock:
            self._windows.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()

    def _current(self, key: str, now: float) -> tuple[float, int]:
        window = self._windows.get(key)
        if window is None or now - window[0] >= self.window_seconds:
            self._windows.pop(key, None)
            return now, 0
        return window

    def _add(self, key: str, now: float) -> None:
        start, count = self._current(key, now)
        if key not in self._windows:
            self._make_room(now)
        self._windows[key] = (start, count + 1)

    def _ensure_allowed(self, key: str, now: float) -> None:
        start, count = self._current(key, now)
        if count >= self.limit:
            retry_after = max(1, math.ceil(start + self.window_seconds - now))
            raise TooManyRequestsError(retry_after=retry_after)

    def _make_room(self, now: float) -> None:
        """Mantém a memória limitada: descarta janelas expiradas e, se preciso, as mais antigas."""
        if len(self._windows) < self.max_keys:
            return
        expired = [
            key for key, (start, _) in self._windows.items() if now - start >= self.window_seconds
        ]
        for key in expired:
            del self._windows[key]
        while len(self._windows) >= self.max_keys:
            del self._windows[next(iter(self._windows))]


def client_ip(request: Request) -> str:
    """IP do cliente. Atrás de um proxy reverso, rode o uvicorn com
    `--proxy-headers --forwarded-allow-ips=<ip do proxy>` para que este seja o IP real."""
    return request.client.host if request.client else "desconhecido"


def login_failure_key(email: str, ip: str) -> str:
    return f"{email}|{ip}"


# Tentativas de login por IP (protege contra força bruta e contra abuso do hash Argon2).
login_ip_limiter = RateLimiter(settings.login_rate_limit_per_minute, window_seconds=60)
# Falhas de login por e-mail + IP: barra a força bruta de um IP contra uma conta sem bloquear
# o dono da conta, que entra de outro IP.
login_failure_limiter = RateLimiter(settings.login_failure_limit, window_seconds=15 * 60)
# Falhas de login por e-mail somando todos os IPs (força bruta distribuída). O limite é alto
# para que trancar a conta exija vários IPs.
login_account_limiter = RateLimiter(settings.login_account_failure_limit, window_seconds=60 * 60)
# Cadastros por IP (limita a criação em massa de contas e a enumeração de e-mails).
register_ip_limiter = RateLimiter(settings.register_rate_limit_per_hour, window_seconds=60 * 60)

ALL_LIMITERS = (login_ip_limiter, login_failure_limiter, login_account_limiter, register_ip_limiter)
