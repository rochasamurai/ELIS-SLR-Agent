"""check_openclaw_health.py - lightweight OpenClaw health probe for CI.

This check is intentionally non-blocking when OpenClaw is unreachable in CI.
It returns exit code 0 in all expected scenarios and prints diagnostic status.
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    base_url = os.environ.get("OPENCLAW_URL", "http://127.0.0.1:18789")
    health_path = os.environ.get("OPENCLAW_HEALTH_PATH", "/health")
    timeout = float(os.environ.get("OPENCLAW_TIMEOUT", "2"))
    url = f"{base_url.rstrip('/')}{health_path}"

    req = urllib.request.Request(url, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            print(f"OpenClaw health endpoint reachable: {url} (status={code})")
            return 0
    except urllib.error.HTTPError as exc:
        print(
            f"OpenClaw health endpoint responded with HTTP {exc.code}: {url}. "
            "Non-blocking in CI."
        )
        return 0
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"OpenClaw not reachable at {url}: {exc}. Non-blocking in CI.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
