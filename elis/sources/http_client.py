"""Shared HTTP client for the ELIS adapter layer.

Provides retry on 429/5xx with exponential backoff and jitter,
per-source rate-limit delays, and secret-safe logging.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

# Keys whose values must never appear in log output.
_SENSITIVE_PARAMS = frozenset(
    {
        "apikey",
        "api_key",
        "apiKey",
        "access_token",
        "token",
        "insttoken",
    }
)


def _sanitise_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Return a copy of *params* with sensitive values masked."""
    if not params:
        return {}
    sanitised: dict[str, Any] = {}
    for key, value in params.items():
        if key.lower().replace("-", "_") in {s.lower() for s in _SENSITIVE_PARAMS}:
            sanitised[key] = "***"
        else:
            sanitised[key] = value
    return sanitised


class ELISHttpClient:
    """Resilient HTTP client with retry, backoff, and rate-limit support.

    Parameters
    ----------
    source_name:
        Human-readable label used in log messages.
    delay_seconds:
        Polite delay between successive requests (rate-limit compliance).
    max_retries:
        Maximum retry attempts on 429 / 5xx responses.
    backoff_base:
        Base wait in seconds for exponential backoff.
    backoff_max:
        Cap for backoff wait in seconds.
    timeout:
        Per-request timeout in seconds.
    """

    def __init__(
        self,
        source_name: str,
        *,
        delay_seconds: float = 0.5,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        backoff_max: float = 60.0,
        timeout: int = 30,
    ) -> None:
        self.source_name = source_name
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.timeout = timeout
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Single request with retry
    # ------------------------------------------------------------------

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Issue a GET request with retry on 429 / 5xx.

        Raises ``requests.exceptions.RequestException`` on unrecoverable
        failure or after exhausting retries.
        """
        attempt = 0
        while True:
            try:
                resp = self._session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            except requests.exceptions.RequestException:
                logger.warning(
                    "[%s] Request failed for %s (params=%s)",
                    self.source_name,
                    url,
                    _sanitise_params(params),
                )
                raise

            if resp.status_code == 429 or resp.status_code >= 500:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error(
                        "[%s] Max retries (%d) exceeded — last status %d",
                        self.source_name,
                        self.max_retries,
                        resp.status_code,
                    )
                    resp.raise_for_status()

                wait = min(
                    self.backoff_base * (2 ** (attempt - 1))
                    + random.uniform(0, 0.5),  # noqa: S311
                    self.backoff_max,
                )
                logger.warning(
                    "[%s] %d response — retrying in %.1fs (attempt %d/%d)",
                    self.source_name,
                    resp.status_code,
                    wait,
                    attempt,
                    self.max_retries,
                )
                time.sleep(wait)
                continue

            # Non-retryable client errors bubble up immediately.
            if resp.status_code >= 400:
                resp.raise_for_status()

            return resp

    # ------------------------------------------------------------------
    # Polite delay between calls
    # ------------------------------------------------------------------

    def polite_wait(self) -> None:
        """Sleep for the configured inter-request delay."""
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
