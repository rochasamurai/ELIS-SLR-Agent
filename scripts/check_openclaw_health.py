"""check_openclaw_health.py - lightweight OpenClaw health probe for CI.

This check is intentionally non-blocking when OpenClaw is unreachable in CI.
It prints diagnostic status and always exits 0.
"""

from __future__ import annotations

import base64
import os
import select
import socket
import ssl
import sys
import urllib.parse


def format_path(default_path: str, override_path: str | None) -> str:
    if override_path:
        path = override_path
    else:
        parsed = urllib.parse.urlparse(default_path)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def websocket_ping(host: str, port: int, path: str, timeout: float, use_ssl: bool) -> bool:
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request_lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}:{port}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {key}",
        "Sec-WebSocket-Version: 13",
        "",
        "",
    ]
    request = "\r\n".join(request_lines).encode("ascii")

    with socket.create_connection((host, port), timeout=timeout) as raw_sock:
        sock = raw_sock
        if use_ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(raw_sock, server_hostname=host)
        sock.sendall(request)
        ready = select.select([sock], [], [], timeout)
        if not ready[0]:
            return False
        response = sock.recv(1024).decode("ascii", "ignore").splitlines()
        if not response:
            return False
        status_line = response[0]
        return status_line.startswith("HTTP/1.1 101") or status_line.startswith("HTTP/1.0 101")


def main() -> int:
    base_url = os.environ.get("OPENCLAW_URL", "ws://127.0.0.1:18789")
    health_path = format_path(base_url, os.environ.get("OPENCLAW_HEALTH_PATH"))
    timeout = float(os.environ.get("OPENCLAW_TIMEOUT", "2"))

    parsed = urllib.parse.urlparse(base_url)
    scheme = parsed.scheme or "ws"
    use_ssl = scheme == "wss"
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if use_ssl else 80)

    print(
        f"Probing OpenClaw WebSocket at {scheme}://{host}:{port}{health_path} "
        f"(timeout={timeout}s)"
    )

    try:
        success = websocket_ping(host, port, health_path, timeout, use_ssl)
        if success:
            print("OpenClaw WebSocket handshake succeeded (status 101).")
        else:
            print(
                "OpenClaw WebSocket handshake failed (no 101 response). "
                "Non-blocking in CI."
            )
    except OSError as exc:
        print(
            f"OpenClaw not reachable at ws://{host}:{port}{health_path}: {exc}. "
            "Non-blocking in CI."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
