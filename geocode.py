"""
Geocodes 'suburb, city' text to lat/lon using OpenStreetMap's free Nominatim
API. Nominatim's usage policy caps public requests at 1/sec and requires a
descriptive User-Agent, so results are cached to disk to avoid re-hitting it.
"""
import json
import os
import time
import requests

CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "geocode_cache.json")
HEADERS = {"User-Agent": "commercial-property-finder/1.0 (personal site-selection tool)"}


def _load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


_cache = _load_cache()


def geocode(suburb, city, province="", country="South Africa"):
    query = ", ".join(p for p in [suburb, city, province, country] if p)
    if query in _cache:
        return _cache[query]

    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": 1, "countrycodes": "za"},
        headers=HEADERS,
        timeout=15,
    )
    time.sleep(1.1)  # respect Nominatim's 1 req/sec policy

    result = None
    if resp.status_code == 200 and resp.json():
        hit = resp.json()[0]
        result = {"lat": float(hit["lat"]), "lon": float(hit["lon"])}

    _cache[query] = result
    _save_cache(_cache)
    return result


if __name__ == "__main__":
    print(geocode("Cape Town City Centre", "Cape Town", "Western Cape"))
