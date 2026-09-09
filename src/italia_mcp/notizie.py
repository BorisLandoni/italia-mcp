"""Titoli di notizie italiane dai feed RSS dell'ANSA."""

import time
import urllib.request
import xml.etree.ElementTree as ET

FEED = {
    "principali": "https://www.ansa.it/sito/notizie/topnews/topnews_rss.xml",
    "cronaca": "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml",
    "politica": "https://www.ansa.it/sito/notizie/politica/politica_rss.xml",
    "economia": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
    "mondo": "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
    "tecnologia": "https://www.ansa.it/sito/notizie/tecnologia/tecnologia_rss.xml",
    "sport": "https://www.ansa.it/sito/notizie/sport/sport_rss.xml",
}

TTL = 600
_CACHE: dict[str, tuple[float, list[str]]] = {}


def _titoli(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "italia-mcp/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        albero = ET.fromstring(r.read())
    titoli = []
    for elemento in albero.iterfind(".//item/title"):
        testo = (elemento.text or "").strip()
        if testo:
            titoli.append(testo)
    return titoli


def notizie(argomento: str = "principali", quante: int = 5) -> dict:
    argomento = (argomento or "principali").strip().lower()
    if argomento not in FEED:
        return {"ok": False,
                "errore": f"Argomento non valido. Scegli tra: {', '.join(FEED)}"}

    quante = max(1, min(int(quante), 6))
    adesso = time.time()

    if argomento in _CACHE and adesso - _CACHE[argomento][0] < TTL:
        titoli = _CACHE[argomento][1]
    else:
        try:
            titoli = _titoli(FEED[argomento])
        except Exception:
            return {"ok": False, "errore": "Non riesco a leggere le notizie adesso"}
        _CACHE[argomento] = (adesso, titoli)

    # i titoli lunghi vengono accorciati: la risposta deve restare piccola
    scelti = [t[:110] for t in titoli[:quante]]
    return {"ok": True, "argomento": argomento, "titoli": scelti, "fonte": "ANSA"}
