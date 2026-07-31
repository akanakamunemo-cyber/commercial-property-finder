"""
Free foot-traffic proxy: counts nearby points of interest via OpenStreetMap's
Overpass API. More shops/food/transit around a site correlates with more
pedestrian activity. This is NOT measured visit data (that requires a paid
provider like GapMaps/Placer.ai/BestTime) - it's a relative activity signal
useful for ranking candidate sites against each other.
"""
import requests

OVERPASS_URL = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
HEADERS = {"User-Agent": "commercial-property-finder/1.0"}

# Each category is a list of Overpass statement templates (element type +
# tag filter). {r}/{lat}/{lon} are substituted in at query time.
CATEGORIES = {
    "retail": [
        'node(around:{r},{lat},{lon})["shop"];',
        'way(around:{r},{lat},{lon})["shop"];',
    ],
    "food": [
        'node(around:{r},{lat},{lon})["amenity"~"restaurant|cafe|fast_food|bar|pub"];',
        'way(around:{r},{lat},{lon})["amenity"~"restaurant|cafe|fast_food|bar|pub"];',
    ],
    "transit": [
        'node(around:{r},{lat},{lon})["highway"="bus_stop"];',
        'node(around:{r},{lat},{lon})["railway"~"station|stop|tram_stop"];',
        'way(around:{r},{lat},{lon})["railway"="station"];',
    ],
    "offices": [
        'node(around:{r},{lat},{lon})["office"];',
        'way(around:{r},{lat},{lon})["office"];',
    ],
}


def poi_density(lat, lon, radius_m=500):
    """Returns counts per category plus a weighted composite score."""
    counts = {}
    for key, statements in CATEGORIES.items():
        body = " ".join(s.format(r=radius_m, lat=lat, lon=lon) for s in statements)
        q = f"""
        [out:json][timeout:25];
        (
          {body}
        );
        out count;
        """
        try:
            resp = requests.post(OVERPASS_URL, data={"data": q}, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            counts[key] = int(data["elements"][0]["tags"]["total"])
        except Exception:
            counts[key] = None

    weights = {"retail": 1.0, "food": 1.2, "transit": 1.5, "offices": 0.6}
    score = sum((counts.get(k) or 0) * w for k, w in weights.items())

    return {"counts": counts, "activity_score": round(score, 1), "radius_m": radius_m}


if __name__ == "__main__":
    print(poi_density(-33.9249, 18.4241))  # central Cape Town
