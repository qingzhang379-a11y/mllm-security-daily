"""
Network utilities: HTTP session, retry, mirror fallback, rate limiting.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

import aiohttp
import requests
from yaml import safe_load

from .logger import get_logger

logger = get_logger(__name__)


class NetworkUtils:
    """Wrapper for HTTP requests with retry and rate limiting."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        net_cfg = config.get("network", {})
        self.timeout = net_cfg.get("default_timeout", 30)
        self.connect_timeout = net_cfg.get("connect_timeout", 15)
        self.max_retries = net_cfg.get("max_retries", 3)
        self.backoff_base = net_cfg.get("backoff_base", 2.0)
        self.user_agent = net_cfg.get(
            "user_agent",
            "MLLM-Security-Daily/1.0 (Academic Research Project)"
        )
        self._last_request_time: dict[str, float] = {}

    def _get_headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    def _respect_interval(self, source_name: str, interval: float):
        """Ensure minimum interval between requests to the same source."""
        now = time.time()
        last = self._last_request_time.get(source_name, 0)
        elapsed = now - last
        if elapsed < interval:
            sleep_time = interval - elapsed
            logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s for {source_name}")
            time.sleep(sleep_time)
        self._last_request_time[source_name] = time.time()

    def requests_get(self, url: str, source_name: str = "default",
                     interval: float = 3.0, **kwargs) -> Optional[requests.Response]:
        """Synchronous GET with retry and rate limiting."""
        self._respect_interval(source_name, interval)

        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(
                    url, headers=headers, timeout=self.timeout, **kwargs
                )
                resp.raise_for_status()
                logger.info(f"GET {url} -> {resp.status_code}")
                return resp
            except requests.RequestException as e:
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed for {url}: {e}"
                )
                if attempt < self.max_retries:
                    sleep_time = self.backoff_base ** attempt
                    time.sleep(sleep_time)
        logger.error(f"All {self.max_retries} attempts failed for {url}")
        return None

    async def aiohttp_get(self, url: str, source_name: str = "default",
                          interval: float = 3.0,
                          **kwargs) -> Optional[str]:
        """Async GET with retry and rate limiting."""
        self._respect_interval(source_name, interval)

        headers = self._get_headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        timeout_obj = aiohttp.ClientTimeout(total=self.timeout)

        for attempt in range(1, self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(headers=headers,
                                                 timeout=timeout_obj) as session:
                    async with session.get(url, **kwargs) as resp:
                        text = await resp.text()
                        logger.info(f"GET {url} -> {resp.status}")
                        return text
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(
                    f"Attempt {attempt}/{self.max_retries} failed for {url}: {e}"
                )
                if attempt < self.max_retries:
                    sleep_time = self.backoff_base ** attempt
                    await asyncio.sleep(sleep_time)
        logger.error(f"All {self.max_retries} attempts failed for {url}")
        return None

    @staticmethod
    def check_robots_txt(robots_url: str) -> bool:
        """Check if scraping is allowed via robots.txt (basic check)."""
        try:
            resp = requests.get(
                robots_url,
                headers={"User-Agent": "*"},
                timeout=10
            )
            if resp.status_code == 200:
                content = resp.text.lower()
                # Check if our UA is disallowed
                disallowed = "disallow: /"
                return disallowed not in content
            return True
        except requests.RequestException:
            logger.warning(f"Could not fetch robots.txt from {robots_url}")
            return True
