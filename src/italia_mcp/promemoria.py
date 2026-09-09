"""Promemoria e lista della spesa, salvati su file.

Attenzione: il dispositivo non puo' essere svegliato dal server, quindi questi
sono promemoria da consultare a voce, non sveglie che suonano da sole.
"""

import json
import os
import tempfile

PERCORSO = os.environ.get(
    "ITALIA_MCP_PROMEMORIA",
    os.path.join(tempfile.gettempdir(), "italia-mcp-promemoria.json"),
)
MASSIMO = 30


def _leggi() -> list[str]:
    try:
        with open(PERCORSO, encoding="utf-8") as f:
            dati = json.load(f)
        return [str(v) for v in dati][:MASSIMO]
    except Exception:
        return []


def _scrivi(voci: list[str]) -> None:
    os.makedirs(os.path.dirname(PERCORSO) or ".", exist_ok=True)
    with open(PERCORSO, "w", encoding="utf-8") as f:
        json.dump(voci[:MASSIMO], f, ensure_ascii=False)


def aggiungi(testo: str) -> dict:
    testo = (testo or "").strip()
    if not testo:
        return {"ok": False, "errore": "Dimmi cosa devo ricordare"}

    voci = _leggi()
    if len(voci) >= MASSIMO:
        return {"ok": False, "errore": f"La lista e' piena ({MASSIMO} voci)"}
    if testo.lower() in (v.lower() for v in voci):
        return {"ok": True, "gia_presente": True, "totale": len(voci)}

    voci.append(testo)
    _scrivi(voci)
    return {"ok": True, "aggiunto": testo, "totale": len(voci)}


def elenco() -> dict:
    voci = _leggi()
    if not voci:
        return {"ok": True, "vuota": True, "voci": []}
    return {"ok": True,
            "voci": [f"{i}. {v}" for i, v in enumerate(voci[:12], 1)],
            "totale": len(voci)}


def rimuovi(numero_o_testo: str) -> dict:
    voci = _leggi()
    if not voci:
        return {"ok": False, "errore": "La lista e' gia' vuota"}

    chiave = str(numero_o_testo or "").strip()
    if chiave.lower() in ("tutto", "tutti", "tutte"):
        _scrivi([])
        return {"ok": True, "svuotata": True}

    indice = None
    if chiave.isdigit() and 1 <= int(chiave) <= len(voci):
        indice = int(chiave) - 1
    else:
        for i, voce in enumerate(voci):
            if chiave.lower() in voce.lower():
                indice = i
                break

    if indice is None:
        return {"ok": False, "errore": f"Non trovo '{chiave}' nella lista"}

    tolto = voci.pop(indice)
    _scrivi(voci)
    return {"ok": True, "rimosso": tolto, "totale": len(voci)}
