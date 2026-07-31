# SA Commercial Property Finder

A local tool that scrapes commercial property listings for sale in South Africa
(via Property24), enriches each one with free foot-traffic-proxy and
demographic signals, scores them, and shows the results on a map + table
dashboard.

## Pipeline

1. **`scraper.py`** — scrapes Property24's commercial-for-sale search pages
   (price, size, suburb, listing URL). Server-rendered HTML, no JS engine
   needed.
2. **`geocode.py`** — geocodes each suburb to lat/lon via OpenStreetMap
   Nominatim (free, rate-limited to 1 req/sec, cached to `data/geocode_cache.json`).
3. **`poi.py`** — free foot-traffic *proxy*: counts nearby shops, food/drink
   venues, transit stops, and offices within 500m via the OpenStreetMap
   Overpass API, weighted into an "activity score."
4. **`demographics.py`** — static per-metro lookup: verified Census 2022
   population + a *relative* income tier (High/Medium/Low). See limitations
   below.
5. **`pipeline.py`** — orchestrates the above and writes `data/results.json`.
6. **`app.py`** + **`templates/index.html`** — Flask dashboard: pick a region,
   click "Scrape & Score," see results on a Leaflet map and sortable table.

## Running it

```
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5050 in a browser, pick a region, and click
"Scrape & Score." First runs take a few minutes (geocoding is rate-limited to
~1 request/sec, and each listing needs 4 Overpass queries).

You can also run the pipeline directly from the CLI:
```
python pipeline.py
```

## Important data limitations (read before trusting the numbers)

**Foot traffic is a proxy, not measured data.** The "activity score" counts
nearby OpenStreetMap points of interest (shops, restaurants, transit stops,
offices) as a stand-in for pedestrian activity. It's useful for *ranking*
candidate sites relatively, but it is **not** actual visit-count data. For
real foot traffic (device-location-based visit counts), you'd need a paid
provider — **GapMaps** (confirmed South Africa coverage, REST API) or
**BestTime.app** / **Placer.ai** are the ones with demonstrated SA usage.
Swapping in a paid provider means writing a new module with the same
interface as `poi_density()` in `poi.py`.

**Income data is a rough relative tier, not Rand figures.** Statistics South
Africa did **not** release household income data from Census 2022 (data
quality/coverage issues per their own release notes). There is no free,
reliable, machine-readable source of income-by-suburb for South Africa today.
`demographics.py` uses a qualitative High→Low tier per metro based on general,
well-documented provincial income patterns (Western Cape/Gauteng highest,
Eastern Cape/Free State lower) — treat it as directional only.

**Age data is national-only.** The only broadly-cited figure is the national
median age (28, Census 2022). No free source publishes verified median age by
suburb or metro. `demographics.py` returns the national figure for every
location, flagged with `median_age_is_national_estimate: true`.

**Population figures are real** — Census 2022 metro totals, cross-checked
against Wikipedia's cited StatsSA figures.

## Upgrading data quality later

If this proves useful and you want sharper numbers:
- **Foot traffic**: integrate GapMaps or BestTime.app's API (both have paid
  tiers) — replace `poi.py`'s `poi_density()` with a call to their API,
  keeping the same return shape so `pipeline.py` doesn't need to change.
- **Income/age**: request custom-area Census 2022 data directly from StatsSA,
  or license Lightstone Property's South African demographic/spending data
  (used by SA banks and retailers for site selection).
- **More property sources**: Property24 is the largest SA listings portal,
  but Gumtree Property and PropertyFox commercial listings could be added
  as extra scraper modules feeding the same pipeline.

## Etiquette / ToS note

The Property24 scraper is deliberately polite — sequential requests, a
delay between pages, and modest page counts by default. This is for
personal research/analysis. If you plan to scrape at scale or commercially,
check Property24's terms of service or use their listing data via a
licensed data partner instead.
