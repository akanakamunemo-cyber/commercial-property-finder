"""
Scrapes commercial property listings from Property24's public search pages.

Property24 server-renders listing tiles as schema.org Product markup, so this
uses plain requests + BeautifulSoup rather than a browser. Be a polite scraper:
one request per page, a real user agent, and a delay between pages.
"""
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.property24.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def scrape_listings(path, max_pages=3, delay=1.5):
    """
    path: a Property24 search path, e.g.
        "commercial-property-for-sale/cape-town/western-cape/432"
        "commercial-property-to-rent/johannesburg/gauteng/9"
    Returns a list of dicts: listing_number, title, price_zar, suburb,
    size_sqm, url, image_url, for_rent (bool).
    """
    results = []
    seen = set()

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/{path.strip('/')}/p{page}"
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        tiles = soup.select('div[itemtype="http://schema.org/Product"][data-listing-number]')
        if not tiles:
            break

        for tile in tiles:
            listing_number = tile.get("data-listing-number")
            if not listing_number or listing_number in seen:
                continue
            seen.add(listing_number)

            link = tile.select_one("a.p24_content")
            detail_path = link.get("href") if link else None
            if not detail_path:
                continue

            price_el = tile.select_one(".p24_price")
            price_raw = price_el.get("content") if price_el else None
            price_zar = int(price_raw) if price_raw and price_raw.isdigit() else None

            location_el = tile.select_one(".p24_location")
            suburb = location_el.get_text(strip=True) if location_el else None

            size_el = tile.select_one(".p24_size span")
            size_sqm = None
            if size_el:
                m = re.search(r"([\d\s]+)", size_el.get_text())
                if m:
                    size_sqm = int(m.group(1).replace(" ", "").replace("\xa0", ""))

            img_el = tile.select_one("img.js_P24_listingImage")
            image_url = img_el.get("src") if img_el else None

            results.append({
                "listing_number": listing_number,
                "url": BASE_URL + detail_path,
                "suburb": suburb,
                "price_zar": price_zar,
                "size_sqm": size_sqm,
                "image_url": image_url,
                "for_rent": "to-rent" in path,
            })

        time.sleep(delay)

    return results


if __name__ == "__main__":
    listings = scrape_listings("commercial-property-for-sale/cape-town/western-cape/432", max_pages=1)
    for l in listings[:5]:
        print(l)
