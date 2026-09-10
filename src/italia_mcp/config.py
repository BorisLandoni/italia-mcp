"""Memoria delle impostazioni fra un avvio e l'altro.

Il file NON sta accanto all'eseguibile: se il programma finisce in Programmi o
in Download, quella cartella puo' essere di sola lettura. Sta nella cartella di
configurazione dell'utente, che e' sempre scrivibile.
"""

import json
import os
import sys

NOME_APP = "PandaItalia"


def cartella_config() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, NOME_APP)
    if sys.platform == "darwin":
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", NOME_APP)
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "panda-italia")


def percorso_config() -> str:
    return os.path.join(cartella_config(), "config.json")


def leggi() -> dict:
    try:
        with open(percorso_config(), encoding="utf-8") as f:
            dati = json.load(f)
        return dati if isinstance(dati, dict) else {}
    except Exception:
        return {}


def scrivi(dati: dict) -> None:
    cartella = cartella_config()
    os.makedirs(cartella, exist_ok=True)
    percorso = percorso_config()
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)

    # contiene un token: su Unix togliamo i permessi agli altri utenti
    if sys.platform != "win32":
        try:
            os.chmod(percorso, 0o600)
        except OSError:
            pass


def endpoint_salvato() -> str:
    return (leggi().get("endpoint") or "").strip()


def salva_endpoint(endpoint: str) -> None:
    dati = leggi()
    dati["endpoint"] = (endpoint or "").strip()
    scrivi(dati)


def normalizza_endpoint(testo: str) -> str:
    """Ripulisce quello che l'utente incolla: spazi, virgolette, a capo."""
    testo = (testo or "").strip().strip('"').strip("'").strip()
    return "".join(testo.split())
