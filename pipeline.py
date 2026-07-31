"""
Orchestrates the full pipeline: scrape Property24 -> geocode -> POI density
(foot-traffic proxy) -> demographic context -> composite score -> save JSON.
"""
import json
import os
import sys

from scraper import scrape_listings
from geocode import geocode
from poi import poi_density
from demographics import lookup as demo_lookup

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "data", "results.json")


def run(path, max_pages=2, city_hint=None, province_hint=None):
    """
    path: Property24 search path, e.g.
        "commercial-property-for-sale/cape-town/western-cape/432"
    city_hint/province_hint: used for geocoding context (Property24 only
        gives suburb text on the listing card, not city/province).
    """
    print(f"Scraping {path} ...")
    listings = scrape_listings(path, max_pages=max_pages)
    print(f"  found {len(listings)} listings")

    enriched = []
    for i, listing in enumerate(listings):
        print(f"[{i + 1}/{len(listings)}] {listing['suburb']}")

        loc = geocode(listing["suburb"], city_hint or "", province_hint or "")
        if not loc:
            listing["geocode_failed"] = True
            enriched.append(listing)
            continue

        listing["lat"] = loc["lat"]
        listing["lon"] = loc["lon"]

        poi = poi_density(loc["lat"], loc["lon"])
        listing["poi"] = poi

        demo = demo_lookup(city_hint or listing["suburb"])
        listing["demographics"] = demo

        income_score = demo["income_tier_score"] if demo else 0
        listing["composite_score"] = round(poi["activity_score"] + income_score * 10, 1)

        enriched.append(listing)

    enriched.sort(key=lambda l: l.get("composite_score", -1), reverse=True)

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print(f"Saved {len(enriched)} results to {RESULTS_PATH}")
    return enriched


if __name__ == "__main__":
    # Example: Cape Town commercial-for-sale listings
    run(
        "commercial-property-for-sale/cape-town/western-cape/432",
        max_pages=1,
        city_hint="Cape Town",
        province_hint="Western Cape",
    )
