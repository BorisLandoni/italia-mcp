"""Definizione degli strumenti MCP.

Regole di progetto (dai vincoli della piattaforma xiaozhi/小智):
  * pochi strumenti: l'elenco viaggia in ogni richiesta al modello;
  * nomi e parametri espliciti in italiano, mai abbreviazioni;
  * ogni risposta deve stare sotto i 1024 byte;
  * mai usare print(): stdin/stdout sono il canale di trasporto MCP.
"""

from mcp.server.fastmcp import FastMCP

from . import allerte as _allerte
from . import meteo as _meteo
from . import notizie as _notizie
from . import promemoria as _promemoria

mcp = FastMCP("Italia")


@mcp.tool()
def meteo_adesso(citta: str) -> dict:
    """Che tempo fa in questo momento in una localita italiana.
    Usalo quando l'utente chiede il tempo, la temperatura, se piove,
    se fa freddo o se serve l'ombrello adesso.
    Il parametro citta e' il nome del comune, per esempio "Milano" o "Arsago Seprio"."""
    return _meteo.adesso(citta)


@mcp.tool()
def meteo_previsioni(citta: str, giorni: int = 3) -> dict:
    """Previsioni del tempo per i prossimi giorni in una localita italiana.
    Usalo quando l'utente chiede il tempo di domani, del fine settimana
    o dei prossimi giorni. Il parametro giorni va da 1 a 7."""
    return _meteo.previsioni(citta, giorni)


@mcp.tool()
def allerte_protezione_civile(comune: str) -> dict:
    """Allerta meteo ufficiale della Protezione Civile per un comune italiano
    (allerta gialla, arancione o rossa per temporali, rischio idraulico
    e rischio idrogeologico). Usalo quando l'utente chiede se c'e' un'allerta
    meteo, se e' pericoloso uscire o se ci sono avvisi per il maltempo.
    Il parametro comune e' il nome esatto del comune, per esempio "Gallarate"."""
    return _allerte.allerte(comune)


@mcp.tool()
def qualita_aria(citta: str) -> dict:
    """Qualita dell'aria in una localita italiana, con indice europeo,
    polveri sottili PM10 e PM2.5. Usalo quando l'utente chiede com'e' l'aria,
    se c'e' smog o se puo' andare a correre."""
    return _meteo.aria(citta)


@mcp.tool()
def notizie_italia(argomento: str = "principali") -> dict:
    """Ultimi titoli delle notizie italiane dall'agenzia ANSA.
    Usalo quando l'utente chiede le notizie, che cosa succede o le ultime novita'.
    Gli argomenti disponibili sono: principali, cronaca, politica, economia,
    mondo, tecnologia, sport."""
    return _notizie.notizie(argomento)


@mcp.tool()
def promemoria_aggiungi(testo: str) -> dict:
    """Aggiunge una cosa da ricordare o un articolo alla lista della spesa.
    Usalo quando l'utente dice di ricordargli qualcosa, di segnarsi una cosa
    o di aggiungere un prodotto alla spesa."""
    return _promemoria.aggiungi(testo)


@mcp.tool()
def promemoria_elenco() -> dict:
    """Legge tutte le cose da ricordare e la lista della spesa.
    Usalo quando l'utente chiede cosa deve fare, cosa aveva segnato
    o cosa c'e' nella lista della spesa."""
    return _promemoria.elenco()


@mcp.tool()
def promemoria_rimuovi(numero_o_testo: str) -> dict:
    """Toglie una voce dalla lista dei promemoria o della spesa.
    Accetta il numero della voce oppure una parola contenuta nella voce.
    Usa la parola "tutto" per svuotare completamente la lista."""
    return _promemoria.rimuovi(numero_o_testo)
