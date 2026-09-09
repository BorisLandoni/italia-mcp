"""Ultime pubblicazioni dei siti Futura Group (Elettronica In, EI PRO, FuturaShop).

Un solo strumento con un parametro, invece di tre strumenti separati: l'elenco
degli strumenti viaggia in ogni richiesta al modello, quindi ogni voce in meno
e' contesto guadagnato.

Le fonti si possono ridefinire con la variabile d'ambiente ITALIA_MCP_FONTI,
nel formato  chiave=URL|Etichetta;chiave2=URL2|Etichetta2
"""

import html
import os
import time
import urllib.request
import xml.etree.ElementTree as ET

FONTI_PREDEFINITE = {
    "elettronica-in": (
        "https://ei.futuranet.it/feed/",
        "Elettronica In",
    ),
    "elettronica-in-pro": (
        "https://eipro.futuranet.it/feed/",
        "Elettronica In PRO",
    ),
    "prodotti": (
        "https://futuranet.it/?post_type=product&feed=rss2",
        "FuturaShop",
    ),
}

# come l'utente puo' nominare le sezioni a voce
SINONIMI = {
    "ei": "elettronica-in",
    "elettronica": "elettronica-in",
    "elettronicain": "elettronica-in",
    "articoli": "elettronica-in",
    "rivista": "elettronica-in",
    "eipro": "elettronica-in-pro",
    "pro": "elettronica-in-pro",
    "elettronica-in-professional": "elettronica-in-pro",
    "shop": "prodotti",
    "futurashop": "prodotti",
    "negozio": "prodotti",
    "prodotto": "prodotti",
    "novita": "prodotti",
}

TTL = 900
_CACHE: dict[str, tuple[float, list[str]]] = {}


def _fonti() -> dict[str, tuple[str, str]]:
    grezzo = os.environ.get("ITALIA_MCP_FONTI", "").strip()
    if not grezzo:
        return FONTI_PREDEFINITE

    fonti = {}
    for pezzo in grezzo.split(";"):
        if "=" not in pezzo:
            continue
        chiave, resto = pezzo.split("=", 1)
        url, _, etichetta = resto.partition("|")
        fonti[chiave.strip().lower()] = (url.strip(), (etichetta or chiave).strip())
    return fonti or FONTI_PREDEFINITE


def _titoli(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "italia-mcp/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        albero = ET.fromstring(r.read())

    titoli = []
    for elemento in albero.iterfind(".//item/title"):
        testo = html.unescape((elemento.text or "").strip())
        if testo:
            titoli.append(" ".join(testo.split()))
    return titoli


def novita(sezione: str = "elettronica-in", quante: int = 5) -> dict:
    fonti = _fonti()

    chiave = (sezione or "elettronica-in").strip().lower().replace(" ", "-")
    chiave = SINONIMI.get(chiave, chiave)
    if chiave not in fonti:
        return {"ok": False,
                "errore": f"Sezione non valida. Scegli tra: {', '.join(fonti)}"}

    url, etichetta = fonti[chiave]
    quante = max(1, min(int(quante), 6))
    adesso = time.time()

    if chiave in _CACHE and adesso - _CACHE[chiave][0] < TTL:
        titoli = _CACHE[chiave][1]
    else:
        try:
            titoli = _titoli(url)
        except Exception:
            return {"ok": False, "errore": f"Non riesco a leggere {etichetta} adesso"}
        _CACHE[chiave] = (adesso, titoli)

    if not titoli:
        return {"ok": False, "errore": f"Nessuna novita' da {etichetta}"}

    # titoli accorciati: la risposta deve restare sotto i 1024 byte
    return {"ok": True, "fonte": etichetta, "titoli": [t[:100] for t in titoli[:quante]]}
