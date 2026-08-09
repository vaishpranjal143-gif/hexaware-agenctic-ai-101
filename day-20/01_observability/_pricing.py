import json, urllib.parse, urllib.request
from pathlib import Path

API = "https://prices.azure.com/api/retail/prices"
CACHE = Path(__file__).resolve().parent / "_prices_cache.json"

METERS = {"in": "{v} inp Gl 1M Tokens",                   # uncached input
          "cached": "{v} cd inp Gl 1M Tokens",            # cached input, ~10x cheaper
          "out": "{v} opt Gl 1M Tokens"}                  # output, the expensive one

FALLBACK = {"in": 2.50, "cached": 0.25, "out": 15.00}     # last known gpt-5.4 Global list price


def _meter_price(meter: str, region: str) -> float | None:
    """Ask the Retail Prices API for one meter, in one region."""
    query = urllib.parse.quote(f"meterName eq '{meter}' and armRegionName eq '{region}'")
    try:
        with urllib.request.urlopen(f"{API}?$filter={query}", timeout=15) as response:
            items = json.loads(response.read()).get("Items", [])
        return float(items[0]["retailPrice"]) if items else None
    except Exception:                                     # offline, rate-limited, schema changed
        return None


def rates(model: str = "gpt-5.4", region: str = "eastus",
          refresh: bool = False) -> tuple[dict[str, float], str]:
    """USD per MILLION tokens for a model, plus a note saying where they came from."""
    key = f"{model}|{region}"
    cache: dict[str, dict[str, float]] = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    if key in cache and not refresh:                      # a classroom should not hammer the API
        return cache[key], f"cached from prices.azure.com ({model}, {region})"

    version = model.replace("gpt-", "")                   # "gpt-5.4" -> "5.4", the meter's prefix
    looked_up = {k: _meter_price(m.format(v=version), region) for k, m in METERS.items()}
    if any(v is None for v in looked_up.values()):        # partial answers are worse than none
        return FALLBACK, (f"FALLBACK constants — no '1M Tokens' meter for '{model}' in {region} "
                          f"(meter naming differs per model family)")

    found: dict[str, float] = {k: float(v) for k, v in looked_up.items() if v is not None}
    cache[key] = found; CACHE.write_text(json.dumps(cache, indent=2))
    return found, f"live from prices.azure.com ({model}, {region}, list price)"


if __name__ == "__main__":                                # `python _pricing.py` to see the numbers
    for m in ("gpt-5.4", "gpt-4.1", "gpt-nonexistent"):
        got, source = rates(m, refresh=True)
        print(f"   {m:18} {got}   <- {source}")
