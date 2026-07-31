"""
Demographic context per South African metro.

IMPORTANT LIMITATION: Statistics South Africa did NOT release household
income figures from Census 2022 (data quality/coverage issues), and no
public source publishes reliable median age by metro. So this module
gives:
  - population: real, verified Census 2022 figures where available
  - income_tier: a *relative* qualitative ranking (not Rand values), based
    on well-established provincial income patterns (Western Cape/Gauteng
    highest, Eastern Cape/Limpopo lowest) from the Income & Expenditure
    Survey 2022/23 and General Household Survey reporting
  - median_age: national figure only (28, Census 2022); no verified
    metro-level breakdown is publicly available for free

For real Rand-value income and precise local age data, you'd need a paid
source (Lightstone, GapMaps demographics, StatsSA custom data request) or
StatsSA's per-municipality Census 2022 PDF profiles, which aren't
machine-readable. This table is a coarse city-level signal only - treat it
as directional, not authoritative.
"""

NATIONAL_MEDIAN_AGE = 28  # Census 2022

METROS = {
    "cape town": {
        "province": "Western Cape",
        "population_2022": 4772846,
        "income_tier": "High",
    },
    "johannesburg": {
        "province": "Gauteng",
        "population_2022": 4803262,
        "income_tier": "High",
    },
    "tshwane": {
        "province": "Gauteng",
        "population_2022": 4040315,
        "income_tier": "High",
    },
    "pretoria": {
        "province": "Gauteng",
        "population_2022": 4040315,
        "income_tier": "High",
    },
    "ekurhuleni": {
        "province": "Gauteng",
        "population_2022": 4066691,
        "income_tier": "Medium-High",
    },
    "durban": {
        "province": "KwaZulu-Natal",
        "population_2022": 4239901,
        "income_tier": "Medium",
    },
    "ethekwini": {
        "province": "KwaZulu-Natal",
        "population_2022": 4239901,
        "income_tier": "Medium",
    },
    "nelson mandela bay": {
        "province": "Eastern Cape",
        "population_2022": 1190496,
        "income_tier": "Medium-Low",
    },
    "gqeberha": {
        "province": "Eastern Cape",
        "population_2022": 1190496,
        "income_tier": "Medium-Low",
    },
    "port elizabeth": {
        "province": "Eastern Cape",
        "population_2022": 1190496,
        "income_tier": "Medium-Low",
    },
    "buffalo city": {
        "province": "Eastern Cape",
        "population_2022": 975255,
        "income_tier": "Low",
    },
    "east london": {
        "province": "Eastern Cape",
        "population_2022": 975255,
        "income_tier": "Low",
    },
    "mangaung": {
        "province": "Free State",
        "population_2022": 811431,
        "income_tier": "Medium-Low",
    },
    "bloemfontein": {
        "province": "Free State",
        "population_2022": 811431,
        "income_tier": "Medium-Low",
    },
}

TIER_SCORE = {"High": 4, "Medium-High": 3, "Medium": 2, "Medium-Low": 1, "Low": 0}


def lookup(city):
    """Matches a free-text city name (as scraped from Property24) to a metro record."""
    if not city:
        return None
    key = city.strip().lower()
    for name, record in METROS.items():
        if name in key or key in name:
            return {
                "metro": name,
                "province": record["province"],
                "population_2022": record["population_2022"],
                "income_tier": record["income_tier"],
                "income_tier_score": TIER_SCORE[record["income_tier"]],
                "median_age": NATIONAL_MEDIAN_AGE,
                "median_age_is_national_estimate": True,
            }
    return None


if __name__ == "__main__":
    print(lookup("Cape Town"))
    print(lookup("Some Unknown Town"))
