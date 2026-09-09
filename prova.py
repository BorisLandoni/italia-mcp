#!/usr/bin/env python3
"""Prova tutti gli strumenti senza bisogno di un client MCP.

    python prova.py            prova tutto
    python prova.py meteo      prova solo gli strumenti che contengono "meteo"

Per ogni strumento stampa il risultato e quanto pesa la risposta: il limite
della piattaforma xiaozhi e' 1024 byte, e questo script serve a non superarlo
mai per sbaglio.
"""

import json
import sys
import time

from italia_mcp import allerte, futura, meteo, notizie, promemoria

LIMITE = 1024

PROVE = [
    ("meteo_adesso", lambda: meteo.adesso("Gallarate")),
    ("meteo_previsioni", lambda: meteo.previsioni("Arsago Seprio", 3)),
    ("allerte_protezione_civile", lambda: allerte.allerte("Arsago Seprio")),
    ("qualita_aria", lambda: meteo.aria("Milano")),
    ("notizie_italia", lambda: notizie.notizie("tecnologia")),
    ("novita_futura [rivista]", lambda: futura.novita("elettronica-in")),
    ("novita_futura [pro]", lambda: futura.novita("elettronica-in-pro")),
    ("novita_futura [shop]", lambda: futura.novita("prodotti")),
    ("promemoria_aggiungi", lambda: promemoria.aggiungi("comprare il latte")),
    ("promemoria_elenco", lambda: promemoria.elenco()),
    ("promemoria_rimuovi", lambda: promemoria.rimuovi("latte")),
]


def main() -> int:
    filtro = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    prove = [p for p in PROVE if filtro in p[0].lower()]
    if not prove:
        print(f"Nessuno strumento corrisponde a '{filtro}'")
        return 1

    problemi = 0
    peggiore = 0

    for nome, funzione in prove:
        inizio = time.time()
        try:
            risultato = funzione()
        except Exception as errore:
            print(f"[ERRORE] {nome}: {errore}")
            problemi += 1
            continue

        ms = (time.time() - inizio) * 1000
        testo = json.dumps(risultato, ensure_ascii=False)
        byte = len(testo.encode("utf-8"))
        peggiore = max(peggiore, byte)

        if byte > LIMITE:
            stato, problemi = "TROPPO GRANDE", problemi + 1
        elif not risultato.get("ok", True):
            stato = "risposta di errore"
        else:
            stato = "ok"

        print(f"[{stato:>14}] {byte:4d} byte {ms:6.0f} ms  {nome}")
        print(f"                 {testo[:160]}")

    print(f"\nRisposta piu' pesante: {peggiore} byte su un limite di {LIMITE}.")
    if problemi:
        print(f"{problemi} strumenti da controllare.")
    else:
        print("Tutti gli strumenti rispondono correttamente.")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
