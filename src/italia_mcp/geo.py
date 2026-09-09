"""Geocoding: da nome di citta/comune a coordinate. Fonte: Open-Meteo (gratis, senza chiave)."""

import json
import unicodedata
import urllib.parse
import urllib.request

TIMEOUT = 10
_CACHE: dict[str, dict | None] = {}


def normalizza(testo: str) -> str:
    """Minuscolo, senza accenti e senza punteggiatura: per confrontare nomi di comuni."""
    testo = unicodedata.normalize("NFKD", (testo or "").strip().lower())
    testo = "".join(c for c in testo if not unicodedata.combining(c))
    return " ".join(testo.replace("'", " ").replace("-", " ").split())


def scarica_json(url: str, timeout: int = TIMEOUT) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "italia-mcp/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def trova(citta: str) -> dict | None:
    """Coordinate di una localita. A parita di nome preferisce sempre l'Italia."""
    chiave = normalizza(citta)
    if chiave in _CACHE:
        return _CACHE[chiave]

    query = urllib.parse.urlencode(
        {"name": citta, "count": 10, "language": "it", "format": "json"}
    )
    try:
        risultati = scarica_json(
            "https://geocoding-api.open-meteo.com/v1/search?" + query
        ).get("results") or []
    except Exception:
        return None

    scelto = None
    for r in risultati:
        if r.get("country_code") == "IT":
            scelto = r
            break
    if scelto is None and risultati:
        scelto = risultati[0]

    _CACHE[chiave] = scelto
    return scelto
