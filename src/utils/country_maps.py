"""
src/utils/country_maps.py
=========================
Country-name normalisation utilities for the Carbon Footprint pipeline.

Provides:
- _COUNTRY_ALIASES   – lower-case variant → canonical name lookup
- REGION_MAP         – canonical name → world-region string
- _strip_accents()   – unicode accent removal helper
- normalise_country_name()   – single string → canonical name
- normalise_country_series() – pd.Series → pd.Series of canonical names
- add_region_column()        – attach a 'region' column to a DataFrame
"""

import unicodedata
from typing import Optional

import pandas as pd

from src.utils.logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Alias table  (lower-case variant → canonical country name)
# ---------------------------------------------------------------------------
_COUNTRY_ALIASES: dict[str, str] = {
    # ── United States ──────────────────────────────────────────────────────
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "united states of america": "United States",
    "america": "United States",
    "the united states": "United States",
    # ── United Kingdom ─────────────────────────────────────────────────────
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "northern ireland": "United Kingdom",
    "the united kingdom": "United Kingdom",
    # ── China ──────────────────────────────────────────────────────────────
    "china": "China",
    "prc": "China",
    "p.r.c.": "China",
    "people's republic of china": "China",
    "peoples republic of china": "China",
    "mainland china": "China",
    "zhongguo": "China",
    # ── India ──────────────────────────────────────────────────────────────
    "india": "India",
    "republic of india": "India",
    "bharat": "India",
    "hindustan": "India",
    # ── Russia ─────────────────────────────────────────────────────────────
    "russia": "Russia",
    "russian federation": "Russia",
    "rf": "Russia",
    "ussr": "Russia",
    "soviet union": "Russia",
    # ── South Korea ────────────────────────────────────────────────────────
    "south korea": "South Korea",
    "korea": "South Korea",
    "republic of korea": "South Korea",
    "rok": "South Korea",
    "한국": "South Korea",
    # ── North Korea ────────────────────────────────────────────────────────
    "north korea": "North Korea",
    "dprk": "North Korea",
    "democratic people's republic of korea": "North Korea",
    "democratic peoples republic of korea": "North Korea",
    # ── Germany ────────────────────────────────────────────────────────────
    "germany": "Germany",
    "deutschland": "Germany",
    "federal republic of germany": "Germany",
    "west germany": "Germany",
    # ── France ─────────────────────────────────────────────────────────────
    "france": "France",
    "french republic": "France",
    "republique francaise": "France",
    # ── Japan ──────────────────────────────────────────────────────────────
    "japan": "Japan",
    "nippon": "Japan",
    "nihon": "Japan",
    # ── Canada ─────────────────────────────────────────────────────────────
    "canada": "Canada",
    # ── Australia ──────────────────────────────────────────────────────────
    "australia": "Australia",
    "oz": "Australia",
    # ── Brazil ─────────────────────────────────────────────────────────────
    "brazil": "Brazil",
    "brasil": "Brazil",
    "federative republic of brazil": "Brazil",
    # ── Italy ──────────────────────────────────────────────────────────────
    "italy": "Italy",
    "italia": "Italy",
    "italian republic": "Italy",
    # ── Spain ──────────────────────────────────────────────────────────────
    "spain": "Spain",
    "españa": "Spain",
    "espana": "Spain",
    "kingdom of spain": "Spain",
    # ── Mexico ─────────────────────────────────────────────────────────────
    "mexico": "Mexico",
    "méxico": "Mexico",
    "united mexican states": "Mexico",
    # ── Indonesia ──────────────────────────────────────────────────────────
    "indonesia": "Indonesia",
    "republic of indonesia": "Indonesia",
    # ── Saudi Arabia ───────────────────────────────────────────────────────
    "saudi arabia": "Saudi Arabia",
    "ksa": "Saudi Arabia",
    "kingdom of saudi arabia": "Saudi Arabia",
    # ── South Africa ───────────────────────────────────────────────────────
    "south africa": "South Africa",
    "rsa": "South Africa",
    "republic of south africa": "South Africa",
    # ── Turkey ─────────────────────────────────────────────────────────────
    "turkey": "Turkey",
    "türkiye": "Turkey",
    "turkiye": "Turkey",
    "republic of turkey": "Turkey",
    # ── Iran ───────────────────────────────────────────────────────────────
    "iran": "Iran",
    "islamic republic of iran": "Iran",
    "persia": "Iran",
    # ── Argentina ──────────────────────────────────────────────────────────
    "argentina": "Argentina",
    "argentine republic": "Argentina",
    # ── Poland ─────────────────────────────────────────────────────────────
    "poland": "Poland",
    "polska": "Poland",
    "republic of poland": "Poland",
    # ── Netherlands ────────────────────────────────────────────────────────
    "netherlands": "Netherlands",
    "the netherlands": "Netherlands",
    "holland": "Netherlands",
    # ── Sweden ─────────────────────────────────────────────────────────────
    "sweden": "Sweden",
    "sverige": "Sweden",
    # ── Norway ─────────────────────────────────────────────────────────────
    "norway": "Norway",
    "norge": "Norway",
    # ── Switzerland ────────────────────────────────────────────────────────
    "switzerland": "Switzerland",
    "schweiz": "Switzerland",
    "suisse": "Switzerland",
    # ── Belgium ────────────────────────────────────────────────────────────
    "belgium": "Belgium",
    "belgique": "Belgium",
    "belgie": "Belgium",
    # ── Pakistan ───────────────────────────────────────────────────────────
    "pakistan": "Pakistan",
    "islamic republic of pakistan": "Pakistan",
    # ── Bangladesh ─────────────────────────────────────────────────────────
    "bangladesh": "Bangladesh",
    "people's republic of bangladesh": "Bangladesh",
    # ── Vietnam ────────────────────────────────────────────────────────────
    "vietnam": "Vietnam",
    "viet nam": "Vietnam",
    "socialist republic of vietnam": "Vietnam",
    # ── Egypt ──────────────────────────────────────────────────────────────
    "egypt": "Egypt",
    "arab republic of egypt": "Egypt",
    # ── Nigeria ────────────────────────────────────────────────────────────
    "nigeria": "Nigeria",
    "federal republic of nigeria": "Nigeria",
    # ── Ethiopia ───────────────────────────────────────────────────────────
    "ethiopia": "Ethiopia",
    "federal democratic republic of ethiopia": "Ethiopia",
    # ── Kenya ──────────────────────────────────────────────────────────────
    "kenya": "Kenya",
    "republic of kenya": "Kenya",
    # ── Tanzania ───────────────────────────────────────────────────────────
    "tanzania": "Tanzania",
    "united republic of tanzania": "Tanzania",
    # ── Ghana ──────────────────────────────────────────────────────────────
    "ghana": "Ghana",
    "republic of ghana": "Ghana",
    # ── Ukraine ────────────────────────────────────────────────────────────
    "ukraine": "Ukraine",
    # ── Czech Republic ─────────────────────────────────────────────────────
    "czech republic": "Czech Republic",
    "czechia": "Czech Republic",
    "czech": "Czech Republic",
    # ── Romania ────────────────────────────────────────────────────────────
    "romania": "Romania",
    "românia": "Romania",
    # ── Greece ─────────────────────────────────────────────────────────────
    "greece": "Greece",
    "hellas": "Greece",
    "hellenic republic": "Greece",
    # ── Portugal ───────────────────────────────────────────────────────────
    "portugal": "Portugal",
    "portuguese republic": "Portugal",
    # ── New Zealand ────────────────────────────────────────────────────────
    "new zealand": "New Zealand",
    "nz": "New Zealand",
    # ── Taiwan ─────────────────────────────────────────────────────────────
    "taiwan": "Taiwan",
    "chinese taipei": "Taiwan",
    "republic of china": "Taiwan",
    "roc": "Taiwan",
    # ── Hong Kong ──────────────────────────────────────────────────────────
    "hong kong": "Hong Kong",
    "hk": "Hong Kong",
    # ── Singapore ──────────────────────────────────────────────────────────
    "singapore": "Singapore",
    "republic of singapore": "Singapore",
    # ── Malaysia ───────────────────────────────────────────────────────────
    "malaysia": "Malaysia",
    # ── Thailand ───────────────────────────────────────────────────────────
    "thailand": "Thailand",
    "kingdom of thailand": "Thailand",
    # ── Philippines ────────────────────────────────────────────────────────
    "philippines": "Philippines",
    "the philippines": "Philippines",
    "republic of the philippines": "Philippines",
    # ── Chile ──────────────────────────────────────────────────────────────
    "chile": "Chile",
    "republic of chile": "Chile",
    # ── Colombia ───────────────────────────────────────────────────────────
    "colombia": "Colombia",
    "republic of colombia": "Colombia",
    # ── Peru ───────────────────────────────────────────────────────────────
    "peru": "Peru",
    "perú": "Peru",
    "republic of peru": "Peru",
    # ── Venezuela ──────────────────────────────────────────────────────────
    "venezuela": "Venezuela",
    "bolivarian republic of venezuela": "Venezuela",
    # ── Israel ─────────────────────────────────────────────────────────────
    "israel": "Israel",
    "state of israel": "Israel",
    # ── Iraq ───────────────────────────────────────────────────────────────
    "iraq": "Iraq",
    "republic of iraq": "Iraq",
    # ── Algeria ────────────────────────────────────────────────────────────
    "algeria": "Algeria",
    "people's democratic republic of algeria": "Algeria",
    # ── Morocco ────────────────────────────────────────────────────────────
    "morocco": "Morocco",
    "kingdom of morocco": "Morocco",
    # ── Kazakhstan ─────────────────────────────────────────────────────────
    "kazakhstan": "Kazakhstan",
    "republic of kazakhstan": "Kazakhstan",
    # ── Austria ────────────────────────────────────────────────────────────
    "austria": "Austria",
    "republic of austria": "Austria",
    "osterreich": "Austria",
    "österreich": "Austria",
    # ── Denmark ────────────────────────────────────────────────────────────
    "denmark": "Denmark",
    "kingdom of denmark": "Denmark",
    "danmark": "Denmark",
    # ── Finland ────────────────────────────────────────────────────────────
    "finland": "Finland",
    "suomi": "Finland",
    "republic of finland": "Finland",
}

# ---------------------------------------------------------------------------
# Region map  (canonical country name → broad world region)
# ---------------------------------------------------------------------------
REGION_MAP: dict[str, str] = {
    # North America
    "United States": "North America",
    "Canada": "North America",
    "Mexico": "North America",
    # Europe
    "United Kingdom": "Europe",
    "Germany": "Europe",
    "France": "Europe",
    "Italy": "Europe",
    "Spain": "Europe",
    "Netherlands": "Europe",
    "Sweden": "Europe",
    "Norway": "Europe",
    "Switzerland": "Europe",
    "Belgium": "Europe",
    "Poland": "Europe",
    "Czech Republic": "Europe",
    "Romania": "Europe",
    "Greece": "Europe",
    "Portugal": "Europe",
    "Austria": "Europe",
    "Denmark": "Europe",
    "Finland": "Europe",
    "Ukraine": "Europe",
    # East Asia & Pacific
    "China": "East Asia & Pacific",
    "Japan": "East Asia & Pacific",
    "South Korea": "East Asia & Pacific",
    "North Korea": "East Asia & Pacific",
    "Taiwan": "East Asia & Pacific",
    "Hong Kong": "East Asia & Pacific",
    "Singapore": "East Asia & Pacific",
    "Malaysia": "East Asia & Pacific",
    "Thailand": "East Asia & Pacific",
    "Vietnam": "East Asia & Pacific",
    "Indonesia": "East Asia & Pacific",
    "Philippines": "East Asia & Pacific",
    "Australia": "East Asia & Pacific",
    "New Zealand": "East Asia & Pacific",
    # South Asia
    "India": "South Asia",
    "Pakistan": "South Asia",
    "Bangladesh": "South Asia",
    # Eastern Europe & Central Asia
    "Russia": "Eastern Europe & Central Asia",
    "Kazakhstan": "Eastern Europe & Central Asia",
    # Middle East & North Africa
    "Saudi Arabia": "Middle East & North Africa",
    "Iran": "Middle East & North Africa",
    "Turkey": "Middle East & North Africa",
    "Iraq": "Middle East & North Africa",
    "Israel": "Middle East & North Africa",
    "Egypt": "Middle East & North Africa",
    "Algeria": "Middle East & North Africa",
    "Morocco": "Middle East & North Africa",
    # Sub-Saharan Africa
    "Nigeria": "Sub-Saharan Africa",
    "South Africa": "Sub-Saharan Africa",
    "Ethiopia": "Sub-Saharan Africa",
    "Kenya": "Sub-Saharan Africa",
    "Tanzania": "Sub-Saharan Africa",
    "Ghana": "Sub-Saharan Africa",
    # Latin America & Caribbean
    "Brazil": "Latin America & Caribbean",
    "Argentina": "Latin America & Caribbean",
    "Chile": "Latin America & Caribbean",
    "Colombia": "Latin America & Caribbean",
    "Peru": "Latin America & Caribbean",
    "Venezuela": "Latin America & Caribbean",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_accents(text: str) -> str:
    """
    Remove diacritical marks (accents) from *text* via Unicode decomposition.

    Parameters
    ----------
    text : str
        Input string, possibly containing accented characters.

    Returns
    -------
    str
        ASCII-safe string with combining characters removed.

    Examples
    --------
    >>> _strip_accents("Türkiye")
    'Turkiye'
    >>> _strip_accents("España")
    'Espana'
    """
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalise_country_name(name: Optional[str]) -> Optional[str]:
    """
    Map a raw country name string to its canonical form.

    The function applies the following resolution steps in order:

    1. Return ``None`` for missing / empty input.
    2. Strip leading/trailing whitespace and collapse internal whitespace.
    3. Look up the lower-cased, accent-stripped variant in ``_COUNTRY_ALIASES``.
    4. If a match is found, return the canonical name.
    5. Otherwise return the original (whitespace-normalised) input unchanged,
       so that callers can detect unresolved names.

    Parameters
    ----------
    name : str | None
        Raw country string as it appears in a dataset.

    Returns
    -------
    str | None
        Canonical country name, or ``None`` if *name* is null/empty.

    Examples
    --------
    >>> normalise_country_name("u.s.a.")
    'United States'
    >>> normalise_country_name("great britain")
    'United Kingdom'
    >>> normalise_country_name("Deutschland")
    'Germany'
    >>> normalise_country_name(None)
    # returns None
    """
    if name is None:
        return None

    # Coerce to string and normalise whitespace
    cleaned = " ".join(str(name).split())

    if not cleaned:
        return None

    # Build lookup key: lower-case + accent-stripped
    key = _strip_accents(cleaned).lower()

    canonical = _COUNTRY_ALIASES.get(key)
    if canonical is not None:
        return canonical

    # Secondary attempt: strip accents from aliases as well (handles stored
    # accented keys when the input is already ASCII)
    for alias, canon in _COUNTRY_ALIASES.items():
        if _strip_accents(alias) == key:
            return canon

    # Unresolved – return normalised original
    log.debug("Country name not resolved: %r", cleaned)
    return cleaned


def normalise_country_series(series: pd.Series) -> pd.Series:
    """
    Vectorised wrapper around :func:`normalise_country_name` for a pandas Series.

    Parameters
    ----------
    series : pd.Series
        Series of raw country name strings (may contain ``NaN``).

    Returns
    -------
    pd.Series
        Series of canonical country names with the same index.

    Examples
    --------
    >>> import pandas as pd
    >>> raw = pd.Series(["usa", "great britain", "Deutschland", None])
    >>> normalise_country_series(raw)
    0    United States
    1   United Kingdom
    2          Germany
    3             None
    dtype: object
    """
    return series.map(normalise_country_name)


def add_region_column(
    df: pd.DataFrame,
    country_col: str = "country",
) -> pd.DataFrame:
    """
    Attach a ``region`` column to *df* based on the canonical country column.

    The function:

    1. Normalises the values in *country_col* using
       :func:`normalise_country_series`.
    2. Maps the resulting canonical names to world regions via
       :data:`REGION_MAP`.
    3. Writes the result into a new ``"region"`` column (overwriting if it
       already exists).

    Countries that cannot be resolved to a region are labelled
    ``"Unknown Region"``.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must contain a column named *country_col*.
    country_col : str
        Name of the column holding raw country name strings.
        Defaults to ``"country"``.

    Returns
    -------
    pd.DataFrame
        The *same* DataFrame with a ``"region"`` column added/updated
        **in-place** (the original object is mutated for efficiency).

    Raises
    ------
    KeyError
        If *country_col* is not present in *df*.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"country": ["usa", "great britain", "Deutschland"]})
    >>> add_region_column(df)
       country          region
    0      usa   North America
    1  great britain      Europe
    2  Deutschland      Europe
    """
    if country_col not in df.columns:
        raise KeyError(
            f"Column {country_col!r} not found in DataFrame. "
            f"Available columns: {list(df.columns)}"
        )

    canonical = normalise_country_series(df[country_col])
    df["region"] = canonical.map(REGION_MAP).fillna("Unknown Region")

    resolved = (df["region"] != "Unknown Region").sum()
    log.info(
        "add_region_column: %d/%d rows mapped to a known region.",
        resolved,
        len(df),
    )
    return df
