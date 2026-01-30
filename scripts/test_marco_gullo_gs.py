"""
Apify Actor access smoke-test (Google Scholar Scraper)

Purpose:
- Validate that you can run the Actor via Apify API and retrieve dataset items.
- Enable Apify Proxy *inside the Actor run* to reduce 429 rate-limiting from Google Scholar.

What this script is NOT:
- Not an external HTTP proxy client (no proxy.apify.com URL usage).
- Not a production scraper orchestration (keeps logic minimal and observable).

Required env vars:
- APIFY_TOKEN (preferred) or APIFY_API_TOKEN (legacy)

Optional env vars:
- GS_KEYWORD            default: "agile"
- GS_MAX_ITEMS          default: "20"
- GS_ATTEMPTS           default: "4"
- APIFY_PROXY_GROUPS    comma-separated, e.g. "RESIDENTIAL" (if your plan supports it)
"""

from apify_client import ApifyClient
import os
import time
import random
from typing import Any, Dict, List, Optional

ACTOR_ID = "marco.gullo/google-scholar-scraper"


# ----------------------------
# Helpers
# ----------------------------

def get_env(*names: str, required: bool = False) -> Optional[str]:
    """
    Return the first matching environment variable value from `names`.
    If required=True and none are set, raise a clear error.
    """
    for name in names:
        val = os.getenv(name)
        if val:
            return val
    if required:
        raise RuntimeError(f"Missing required environment variable: one of {names}")
    return None


def poll_run_until_terminal(client: ApifyClient, run_id: str, poll_secs: float = 3.0) -> Dict[str, Any]:
    """
    Poll the run status until it reaches a terminal state.
    Terminal states: SUCCEEDED, FAILED, ABORTED, TIMED-OUT
    """
    while True:
        run = client.run(run_id).get()
        status = run.get("status")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return run
        time.sleep(poll_secs)


def fetch_dataset_items(client: ApifyClient, dataset_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Iterate dataset items and return them as a list.
    limit=None means "fetch all items".
    """
    items: List[Dict[str, Any]] = []
    for i, item in enumerate(client.dataset(dataset_id).iterate_items()):
        items.append(item)
        if limit is not None and i + 1 >= limit:
            break
    return items


def build_actor_input(keyword: str, max_items: int, proxy_groups: Optional[List[str]]) -> Dict[str, Any]:
    """
    Build the Actor input payload.

    Notes:
    - We enable Apify Proxy *inside* the Actor run.
    - Two common field names exist across actors:
        1) proxyConfiguration (Apify SDK standard)
        2) proxyOptions (used by some community actors)
      We set BOTH for compatibility, but still "proxy config only" (no external proxy URL).
    """
    run_input: Dict[str, Any] = {
        "keyword": keyword,
        "maxItems": max_items,
        "filter": "all",
        "sortBy": "relevance",
        "articleType": "any",
        "enableDebugDumps": False,

        # Apify SDK standard field used by many actors
        "proxyConfiguration": {
            "useApifyProxy": True,
        },

        # Some actors use this alternative field name
        "proxyOptions": {
            "useApifyProxy": True,
        },
    }

    # Optional proxy groups (depends on your plan / proxy access)
    # Example env: APIFY_PROXY_GROUPS=RESIDENTIAL
    if proxy_groups:
        run_input["proxyConfiguration"]["apifyProxyGroups"] = proxy_groups
        run_input["proxyOptions"]["apifyProxyGroups"] = proxy_groups

    return run_input


# ----------------------------
# Main test routine
# ----------------------------

def run_actor_smoketest(client: ApifyClient, keyword: str, max_items: int, proxy_groups: Optional[List[str]]) -> List[Dict[str, Any]]:
    """
    Run the Actor and return dataset items.
    Includes a small retry/backoff loop to avoid failing the test due to transient 429 blocks.
    """
    attempts = int(get_env("GS_ATTEMPTS") or "4")
    last_error: Optional[Exception] = None

    for attempt in range(1, attempts + 1):
        # Keep each attempt explicit and observable (test script behavior).
        run_input = build_actor_input(keyword, max_items, proxy_groups)

        print("\n" + "-" * 80)
        print(f"Attempt {attempt}/{attempts}")
        print(f"Actor: {ACTOR_ID}")
        print(f"Keyword: {keyword!r} | maxItems: {max_items}")
        print(f"Proxy: useApifyProxy=True | Groups: {proxy_groups or 'default'}")

        try:
            # Start the Actor run
            run = client.actor(ACTOR_ID).call(run_input=run_input)
            run_id = run["id"]
            print(f"Run started: {run_id}")

            # Wait until completion
            final_run = poll_run_until_terminal(client, run_id)
            status = final_run.get("status")
            print(f"Run finished: {run_id} | status={status}")

            # Fetch results from the default dataset
            dataset_id = final_run.get("defaultDatasetId")
            if not dataset_id:
                raise RuntimeError("No defaultDatasetId returned by the Actor run.")

            items = fetch_dataset_items(client, dataset_id)
            print(f"Dataset items: {len(items)}")

            # Success criteria for smoke test: SUCCEEDED and non-empty results
            if status == "SUCCEEDED" and items:
                return items

            # If we got a soft-failure (empty results or non-success status),
            # reduce pressure and retry to validate the access path.
            # This keeps the script useful even under intermittent rate limiting.
            max_items = max(5, max_items // 2)
            print(f"Retrying with reduced maxItems={max_items} to lower request pressure...")

        except Exception as e:
            last_error = e
            print(f"ERROR: {type(e).__name__}: {e}")

        # Exponential backoff + small jitter to avoid immediate re-blocking
        sleep_seconds = min(90, 10 * (2 ** (attempt - 1)) + random.uniform(0, 3))
        print(f"Backoff: sleeping {sleep_seconds:.1f}s before next attempt...")
        time.sleep(sleep_seconds)

    # If all attempts fail, raise a clear error for diagnostics
    raise RuntimeError(f"Smoke test failed after {attempts} attempts. Last error: {last_error!r}")


def main() -> None:
    # Apify token (API key) used to authenticate to Apify API
    token = get_env("APIFY_TOKEN", "APIFY_API_TOKEN", required=True)
    client = ApifyClient(token)

    # Test parameters
    keyword = get_env("GS_KEYWORD") or "agile"
    max_items = int(get_env("GS_MAX_ITEMS") or "20")

    # Proxy group selection (optional; only if your plan supports groups like RESIDENTIAL)
    proxy_groups_env = (get_env("APIFY_PROXY_GROUPS") or "").strip()
    proxy_groups = [g.strip() for g in proxy_groups_env.split(",") if g.strip()] or None

    items = run_actor_smoketest(client, keyword, max_items, proxy_groups)

    print("\n" + "=" * 80)
    print("✅ SMOKE TEST PASSED")
    print(f"Retrieved {len(items)} items.")
    print("=" * 80)

    # Print a minimal sample to confirm shape (kept short; this is a validation script)
    first = items[0]
    print("First item sample fields:")
    print("  title  :", str(first.get("title", "N/A"))[:120])
    print("  authors:", str(first.get("authors", "N/A"))[:120])
    print("  year   :", first.get("year", "N/A"))


if __name__ == "__main__":
    main()
