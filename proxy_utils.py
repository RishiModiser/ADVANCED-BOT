"""Proxy parsing helpers shared by the desktop application and tests."""

import logging
from typing import Dict


def parse_proxy(proxy_string: str) -> Dict[str, str]:
    """Parse an authenticated proxy into a Playwright proxy configuration.

    Supported formats are ``username:password@host:port`` and
    ``host:port:username:password``.
    """
    proxy_string = proxy_string.strip()
    if not proxy_string:
        raise ValueError("Empty proxy string")

    try:
        if "@" in proxy_string:
            auth, address = proxy_string.split("@", 1)
            username, password = auth.split(":", 1)
            host, port = address.rsplit(":", 1)
        else:
            host, port, username, password = proxy_string.split(":", 3)
    except ValueError as exc:
        raise ValueError(f"Unable to parse proxy: {proxy_string!r}") from exc

    if not host or not port or not username:
        raise ValueError(f"Unable to parse proxy: {proxy_string!r}")

    proxy_config = {
        "server": f"http://{host}:{port}",
        "username": username,
        "password": password,
    }
    logging.info("Proxy parsed successfully: %s:%s", host, port)
    return proxy_config
