"""Finestra per collegare il panda ai servizi italiani.

Interfaccia minima: si incolla l'indirizzo una volta, viene salvato, e ai lanci
successivi il collegamento parte da solo.

Usa tkinter, che fa parte della libreria standard: nessuna dipendenza in piu'
e PyInstaller la impacchetta senza configurazione.
"""

import logging
import queue
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

from . import config
from .bridge import avvia_in_thread

TITOLO = "Panda Italia"
SOTTOTITOLO = "Meteo, allerte, notizie e promemoria italiani per il tuo assistente vocale"

COLORI = {
    "spento": ("#9aa0a6", "Non collegato"),
    "attesa": ("#e8a33d", "Collegamento in corso..."),
    "collegato": ("#2e9e5b", "Collegato - il panda ha gli strumenti italiani"),
    "errore": ("#d93025", "Errore"),
}

AIUTO = (
    "Come trovare l'indirizzo:\n"
    "xiaozhi.me  >  Console  >  Configure  >  Extensions  >  MCP Endpoint  >  icona copia\n\n"
    "Ricordati di togliere la spunta all'estensione Weather: se resta attiva, il panda ha "
    "due servizi meteo e ne sceglie uno a caso."
)

CREDITI = (
    "Sviluppato da Boris Landoni con l'assistenza di Claude (Anthropic)   |   "
    "Futura Group Srl - futuranet.it   |   Elettronica In - ei.futuranet.it"
)


class CodaLog(logging.Handler):
    """Dirotta i messaggi del ponte verso la finestra."""

    def __init__(self, coda):
        super().__init__()
        self.coda = coda

    def emit(self, record):
        try:
            self.coda.put(("log", self.format(record)))
        except Exception:
            pass


class Finestra:
    def __init__(self, radice):
        self.radice = radice
        self.coda = queue.Queue()
        self.ferma_ponte = None

        radice.title(TITOLO)
        radice.minsize(700, 520)
        radice.configure(bg="#ffffff")

        self._costruisci()
        self._collega_log()

        salvato = config.endpoint_salvato()
        if salvato:
            self.campo.insert(0, salvato)
            self._scrivi("Indirizzo salvato trovato: mi collego.")
            self.radice.after(400, self.collega)
        else:
            self._scrivi("Incolla qui sopra l'indirizzo preso da xiaozhi.me, poi premi Collega.")

        radice.protocol("WM_DELETE_WINDOW", self.chiudi)
        self.radice.after(120, self._svuota_coda)

    # ------------------------------------------------------------- interfaccia

    def _costruisci(self):
        intestazione = tk.Frame(self.radice, bg="#ffffff", padx=18, pady=14)
        intestazione.pack(fill="x")
        tk.Label(intestazione, text=TITOLO, font=("Segoe UI", 17, "bold"),
                 bg="#ffffff", fg="#1a1a1a").pack(anchor="w")
        tk.Label(intestazione, text=SOTTOTITOLO, font=("Segoe UI", 9),
                 bg="#ffffff", fg="#5f6368").pack(anchor="w")

        stato = tk.Frame(self.radice, bg="#f6f7f9", padx=18, pady=10)
        stato.pack(fill="x")
        self.pallino = tk.Canvas(stato, width=13, height=13, bg="#f6f7f9",
                                 highlightthickness=0)
        self.pallino.pack(side="left")
        self.disegno = self.pallino.create_oval(2, 2, 12, 12,
                                                fill=COLORI["spento"][0], outline="")
        self.etichetta_stato = tk.Label(stato, text=COLORI["spento"][1],
                                        font=("Segoe UI", 10, "bold"),
                                        bg="#f6f7f9", fg="#3c4043")
        self.etichetta_stato.pack(side="left", padx=(9, 0))

        corpo = tk.Frame(self.radice, bg="#ffffff", padx=18, pady=14)
        corpo.pack(fill="both", expand=True)

        tk.Label(corpo, text="Indirizzo MCP del tuo panda",
                 font=("Segoe UI", 9, "bold"), bg="#ffffff",
                 fg="#3c4043").pack(anchor="w")

        riga = tk.Frame(corpo, bg="#ffffff")
        riga.pack(fill="x", pady=(4, 2))
        self.campo = tk.Entry(riga, font=("Consolas", 9), relief="solid", bd=1)
        self.campo.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(riga, text="Incolla", command=self.incolla, relief="flat",
                  bg="#e8eaed", fg="#3c4043", padx=12, pady=4,
                  cursor="hand2").pack(side="left", padx=(7, 0))

        tk.Label(corpo, text=AIUTO, font=("Segoe UI", 8), bg="#ffffff",
                 fg="#80868b", justify="left", wraplength=640).pack(anchor="w",
                                                                   pady=(6, 12))

        pulsanti = tk.Frame(corpo, bg="#ffffff")
        pulsanti.pack(fill="x")
        self.bottone = tk.Button(pulsanti, text="Collega", command=self.commuta,
                                 relief="flat", bg="#1a73e8", fg="white",
                                 font=("Segoe UI", 10, "bold"), padx=26, pady=7,
                                 cursor="hand2", activebackground="#1557b0",
                                 activeforeground="white")
        self.bottone.pack(side="left")
        tk.Button(pulsanti, text="Diagnostica", command=self.diagnostica,
                  relief="flat", bg="#e8eaed", fg="#3c4043", padx=16, pady=7,
                  cursor="hand2").pack(side="left", padx=(8, 0))

        ttk.Separator(corpo, orient="horizontal").pack(fill="x", pady=12)

        self.registro = scrolledtext.ScrolledText(corpo, height=11,
                                                  font=("Consolas", 8),
                                                  bg="#1e1e1e", fg="#d4d4d4",
                                                  relief="flat", state="disabled",
                                                  wrap="word")
        self.registro.pack(fill="both", expand=True)

        piede = tk.Frame(self.radice, bg="#f6f7f9", padx=18, pady=8)
        piede.pack(fill="x")
        tk.Label(piede, text=CREDITI, font=("Segoe UI", 8), bg="#f6f7f9",
                 fg="#80868b").pack(anchor="w")

    def _collega_log(self):
        gestore = CodaLog(self.coda)
        gestore.setFormatter(logging.Formatter("%(asctime)s  %(message)s",
                                               datefmt="%H:%M:%S"))
        radice_log = logging.getLogger()
        radice_log.setLevel(logging.INFO)
        radice_log.addHandler(gestore)

    # ------------------------------------------------------------- azioni

    def incolla(self):
        try:
            testo = self.radice.clipboard_get()
        except tk.TclError:
            self._scrivi("Gli appunti sono vuoti.")
            return
        self.campo.delete(0, "end")
        self.campo.insert(0, config.normalizza_endpoint(testo))

    def commuta(self):
        if self.ferma_ponte:
            self.scollega()
        else:
            self.collega()

    def collega(self):
        endpoint = config.normalizza_endpoint(self.campo.get())
        if not endpoint:
            self._scrivi("Manca l'indirizzo: incollalo nel campo qui sopra.")
            return
        if not endpoint.startswith(("ws://", "wss://")):
            self._scrivi("L'indirizzo deve iniziare con wss:// - hai copiato tutto?")
            self._stato("errore", "indirizzo non valido")
            return

        self.campo.delete(0, "end")
        self.campo.insert(0, endpoint)
        config.salva_endpoint(endpoint)
        self._scrivi("Indirizzo salvato in " + config.percorso_config())
        self._scrivi("Al prossimo avvio il collegamento partira' da solo.")

        self._stato("attesa")
        self.bottone.config(text="Scollega", bg="#5f6368", activebackground="#3c4043")
        self.ferma_ponte = avvia_in_thread(
            endpoint, lambda v, d="": self.coda.put(("stato", (v, d)))
        )

    def scollega(self):
        if self.ferma_ponte:
            self.ferma_ponte()
            self.ferma_ponte = None
        self._stato("spento")
        self.bottone.config(text="Collega", bg="#1a73e8", activebackground="#1557b0")
        self._scrivi("Scollegato. Il panda non ha piu' gli strumenti italiani.")

    def diagnostica(self):
        self._scrivi("--- diagnostica ---")

        def lavoro():
            from . import meteo
            try:
                self.coda.put(("log", "Strumenti disponibili: 9"))
                d = meteo.adesso("Gallarate")
                if d.get("ok"):
                    self.coda.put(("log", "Internet OK - Gallarate: "
                                          f"{d['cielo']}, {d['temperatura_c']} gradi"))
                else:
                    self.coda.put(("log", f"Problema sui dati: {d.get('errore')}"))
            except Exception as errore:
                self.coda.put(("log", f"Diagnostica fallita: {errore}"))

        threading.Thread(target=lavoro, daemon=True).start()

    def chiudi(self):
        if self.ferma_ponte:
            self.ferma_ponte()
        self.radice.destroy()

    # ------------------------------------------------------------- utilita'

    def _stato(self, chiave, dettaglio=""):
        colore, testo = COLORI.get(chiave, COLORI["spento"])
        self.pallino.itemconfig(self.disegno, fill=colore)
        self.etichetta_stato.config(
            text=(testo + " - " + dettaglio) if dettaglio else testo
        )

    def _scrivi(self, riga):
        self.registro.config(state="normal")
        self.registro.insert("end", riga + "\n")
        self.registro.see("end")
        self.registro.config(state="disabled")

    def _svuota_coda(self):
        try:
            while True:
                tipo, valore = self.coda.get_nowait()
                if tipo == "log":
                    self._scrivi(valore)
                elif tipo == "stato":
                    self._stato(valore[0], valore[1])
        except queue.Empty:
            pass
        self.radice.after(120, self._svuota_coda)


def main() -> int:
    try:
        radice = tk.Tk()
    except Exception as errore:
        print("Interfaccia grafica non disponibile (" + str(errore) + ").")
        print("Usa la versione da riga di comando: italia-mcp-bridge --help")
        return 1

    Finestra(radice)
    radice.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
