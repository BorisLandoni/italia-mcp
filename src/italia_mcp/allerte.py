"""Allerte meteo-idro della Protezione Civile, a livello di singolo comune.

Fonte: bollettini del Dipartimento della Protezione Civile, ripubblicati in CSV
da OpenData Sicilia (licenza CC BY 4.0).
Il DPC pubblica il bollettino entro le 16:00; il mirror puo' avere qualche ora di
ritardo, percio' NON ci fidiamo del nome del file: leggiamo la finestra di
validita' dichiarata dentro il bollettino e scegliamo quello valido adesso.
"""

import csv
import datetime
import io
import os
import tempfile
import time
import urllib.request

from .geo import normalizza

BASE = ("https://raw.githubusercontent.com/opendatasicilia/"
        "DPC-bollettini-criticita-idrogeologica-idraulica/main/data/bollettini/")
FILE = {
    "oggi": BASE + "bollettino-oggi-comuni-latest.csv",
    "domani": BASE + "bollettino-domani-comuni-latest.csv",
}

TTL = 3600  # ricontrolla al massimo una volta all'ora
CARTELLA_CACHE = os.path.join(tempfile.gettempdir(), "italia-mcp-cache")

_MEMORIA: dict[str, tuple[float, dict]] = {}


def _scarica(url: str, intervallo: str | None = None) -> bytes:
    intestazioni = {"User-Agent": "italia-mcp/1.0"}
    if intervallo:
        intestazioni["Range"] = f"bytes={intervallo}"
    req = urllib.request.Request(url, headers=intestazioni)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def _validita(url: str) -> tuple[datetime.datetime, datetime.datetime] | None:
    """Legge solo i primi byte del CSV per sapere da quando a quando vale.
    Evita di scaricare 2,8 MB per scoprire che il bollettino e' scaduto."""
    try:
        testa = _scarica(url, intervallo="0-800").decode("utf-8", "ignore")
        riga = testa.splitlines()[1]
        campi = riga.split(",")
        return (datetime.datetime.fromisoformat(campi[1]),
                datetime.datetime.fromisoformat(campi[2]))
    except Exception:
        return None


def _percorso_cache(nome: str) -> str:
    os.makedirs(CARTELLA_CACHE, exist_ok=True)
    return os.path.join(CARTELLA_CACHE, f"bollettino-{nome}.csv")


def _tabella(nome: str) -> dict:
    """Bollettino indicizzato per comune, con cache su disco e in memoria."""
    adesso = time.time()
    if nome in _MEMORIA and adesso - _MEMORIA[nome][0] < TTL:
        return _MEMORIA[nome][1]

    percorso = _percorso_cache(nome)
    fresco = os.path.exists(percorso) and adesso - os.path.getmtime(percorso) < TTL
    if not fresco:
        dati = _scarica(FILE[nome])
        with open(percorso, "wb") as f:
            f.write(dati)
    with open(percorso, "rb") as f:
        dati = f.read()

    tabella = {}
    lettore = csv.DictReader(io.StringIO(dati.decode("utf-8", "ignore")))
    for riga in lettore:
        tabella[normalizza(riga["comune_nome"])] = riga

    _MEMORIA[nome] = (adesso, tabella)
    return tabella


def _colore(avviso: str) -> str:
    """'Ordinaria per rischio temporali / ALLERTA GIALLA' -> 'GIALLA'."""
    if not avviso:
        return "NESSUNA"
    coda = avviso.split("/")[-1].strip().upper()
    for colore in ("ROSSA", "ARANCIONE", "GIALLA"):
        if colore in coda:
            return colore
    return "NESSUNA"


ORDINE = {"NESSUNA": 0, "GIALLA": 1, "ARANCIONE": 2, "ROSSA": 3}
RISCHI = {
    "avviso_idrogeologico": "idrogeologico",
    "avviso_temporali": "temporali",
    "avviso_idraulico": "idraulico",
}


def allerte(comune: str) -> dict:
    adesso = datetime.datetime.now().astimezone()

    scelto = None
    for nome, url in FILE.items():
        finestra = _validita(url)
        if finestra and finestra[0] <= adesso <= finestra[1]:
            scelto = (nome, finestra)
            break

    if scelto is None:
        return {"ok": False,
                "errore": "Nessun bollettino della Protezione Civile risulta "
                          "valido in questo momento. Riprova piu' tardi."}

    nome, (_, fine) = scelto
    riga = _tabella(nome).get(normalizza(comune))
    if riga is None:
        return {"ok": False, "errore": f"Il comune '{comune}' non e' nel bollettino"}

    livelli = {etichetta: _colore(riga[campo]) for campo, etichetta in RISCHI.items()}
    massimo = max(livelli.values(), key=lambda c: ORDINE[c])
    attivi = [f"{et}: {liv}" for et, liv in livelli.items() if liv != "NESSUNA"]

    return {
        "ok": True,
        "comune": riga["comune_nome"],
        "provincia": riga["provincia_nome"],
        "allerta": massimo,
        "rischi": attivi or ["nessun rischio segnalato"],
        "valido_fino": fine.strftime("%d/%m %H:%M"),
        "fonte": "Protezione Civile",
    }
