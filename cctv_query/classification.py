from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from cctv_query.models import CCTVRecord


METALLIC_COLORS: tuple[str, ...] = ("Bronze", "Silver", "Gold")

BRAND_COUNTRIES: dict[str, str] = {
    "Hino": "Japanese",
    "Honda": "Japanese",
    "Isuzu": "Japanese",
    "Mazda": "Japanese",
    "Mitsubishi": "Japanese",
    "Nissan": "Japanese",
    "Subaru": "Japanese",
    "Suzuki": "Japanese",
    "Toyota": "Japanese",
    "Aion": "Chinese",
    "BYD": "Chinese",
    "GWM": "Chinese",
    "Geely": "Chinese",
    "Haval": "Chinese",
    "Jaecoo": "Chinese",
    "MG": "Chinese",
    "Neta": "Chinese",
    "Wuling": "Chinese",
    "BMW": "German",
    "Mercedes-Benz": "German",
    "Volkswagen": "German",
    "Chevrolet": "American",
    "Ford": "American",
    "Tesla": "American",
    "Kia": "South Korean",
    "Peugeot": "French",
    "Proton": "Malaysian",
    "Mini": "British / UK origin",
}

COUNTRY_TO_REGION: dict[str, str] = {
    "Japanese": "Japanese",
    "Chinese": "Chinese",
    "German": "European",
    "South Korean": "Korean",
    "French": "European",
    "British / UK origin": "European",
    "American": "American",
    "Malaysian": "Malaysian",
}

ORIGIN_LABELS: tuple[str, ...] = (
    "Japanese",
    "Chinese",
    "Korean",
    "European",
    "American",
    "German",
    "South Korean",
    "French",
    "Malaysian",
    "British / UK origin",
)


def brand_country(brand: str) -> str | None:
    normalized = brand.casefold()
    for known_brand, country in BRAND_COUNTRIES.items():
        if known_brand.casefold() == normalized:
            return country
    return None


def brand_region(brand: str) -> str | None:
    country = brand_country(brand)
    if country is None:
        return None
    return COUNTRY_TO_REGION.get(country, country)


def brand_matches_origin(brand: str, origin: str) -> bool:
    country = brand_country(brand)
    region = brand_region(brand)
    normalized_origin = origin.casefold()
    return any(value and value.casefold() == normalized_origin for value in (country, region))


def brand_matches_any_origin(brand: str, origins: Iterable[str]) -> bool:
    return any(brand_matches_origin(brand, origin) for origin in origins)


def origin_counts(records: Iterable[CCTVRecord]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        region = brand_region(record.brand)
        if region:
            counts[region] += 1
    return counts
