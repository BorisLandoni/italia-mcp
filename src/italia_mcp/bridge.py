"""Ponte fra il server MCP e l'endpoint WebSocket di xiaozhi.

Perche' esiste, invece di usare mcp_pipe.py:
  * mcp_pipe.py non dichiara una licenza, quindi non e' ridistribuibile;
  * lancia un sottoprocesso per ogni connessione, cosa che dentro un
    eseguibile impacchettato (PyInstaller) e' fragile e costosa.

Qui il server MCP gira NELLO STESSO PROCESSO: i messaggi passano per due
stream in memoria invece che per stdin/stdout di un figlio. Un processo solo,
una manciata di megabyte, e nessun eseguibile che rilancia se stesso.

Uso:
    italia-mcp-bridge                    legge MCP_ENDPOINT da .env o ambiente
    italia-mcp-bridge --endpoint wss://...
    italia-mcp-bridge --selftest         diagnostica, non richiede un token valido
"""

import argparse
import logging
import os
import sys

import anyio
import websockets
from mcp.shared.message import SessionMessage
from mcp.types import JSONRPCMessage

from .server import mcp

logger = logging.getLogger("italia-mcp-bridge")

ATTESA_INIZIALE = 2
ATTESA_MASSIMA = 300


def _carica_env() -> None:
    """Legge un file .env accanto all'eseguibile o nella cartella corrente."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()
    if getattr(sys, "frozen", False):
        accanto = os.path.join(os.path.dirname(sys.executable), ".env")
        if os.path.exists(accanto):
            load_dotenv(accanto, override=False)


async def _servi(websocket, server) -> None:
    """Collega il WebSocket al server MCP tramite due stream in memoria."""
    verso_server, dal_websocket = anyio.create_memory_object_stream(0)
    dal_server, verso_websocket = anyio.create_memory_object_stream(0)

    async def in_entrata():
        async with verso_server:
            async for grezzo in websocket:
                if isinstance(grezzo, bytes):
                    grezzo = grezzo.decode("utf-8")
                try:
                    messaggio = JSONRPCMessage.model_validate_json(grezzo)
                except Exception as errore:
                    await verso_server.send(errore)
                    continue
                await verso_server.send(SessionMessage(messaggio))

    async def in_uscita():
        async with verso_websocket:
            async for sessione in verso_websocket:
                await websocket.send(
                    sessione.message.model_dump_json(by_alias=True, exclude_none=True)
                )

    async with anyio.create_task_group() as gruppo:
        gruppo.start_soon(in_entrata)
        gruppo.start_soon(in_uscita)
        await server.run(
            dal_websocket, dal_server, server.create_initialization_options()
        )
        gruppo.cancel_scope.cancel()


async def _ciclo(endpoint: str) -> None:
    """Si collega e resta collegato, riprovando con attesa crescente."""
    server = mcp._mcp_server
    attesa = ATTESA_INIZIALE
    tentativo = 0

    while True:
        try:
            logger.info("Mi collego a xiaozhi...")
            async with websockets.connect(endpoint, ping_interval=20) as websocket:
                logger.info("Collegato. Il panda ora ha gli strumenti italiani.")
                attesa = ATTESA_INIZIALE
                tentativo = 0
                await _servi(websocket, server)
            logger.warning("Connessione chiusa dal server.")
        except Exception as errore:
            logger.error("Errore di connessione: %s", errore)

        tentativo += 1
        logger.info("Nuovo tentativo (%d) fra %d secondi...", tentativo, attesa)
        await anyio.sleep(attesa)
        attesa = min(attesa * 2, ATTESA_MASSIMA)


async def _diagnostica(endpoint: str | None) -> int:
    """Controlla strumenti e raggiungibilita' dell'endpoint, senza restare in ascolto."""
    from . import meteo

    print("1) Strumenti registrati")
    strumenti = await mcp.list_tools()
    print(f"   {len(strumenti)} strumenti: " + ", ".join(t.name for t in strumenti))

    print("2) Accesso a Internet (Open-Meteo)")
    try:
        d = meteo.adesso("Gallarate")
        print(f"   Gallarate: {d.get('cielo')}, {d.get('temperatura_c')} gradi")
    except Exception as errore:
        print(f"   FALLITO: {errore}")
        return 1

    print("3) Handshake WebSocket con xiaozhi")
    if not endpoint:
        print("   saltato: nessun endpoint configurato")
        return 0
    try:
        async with websockets.connect(endpoint, ping_interval=None, open_timeout=20):
            print("   handshake riuscito, endpoint valido")
    except websockets.InvalidStatus as errore:
        codice = errore.response.status_code
        if codice in (401, 403):
            print(f"   handshake OK ma token rifiutato (HTTP {codice})")
            print("   -> il trasporto funziona: controlla di aver copiato tutto l'indirizzo")
            return 1
        print(f"   rifiutato con HTTP {codice}")
        return 1
    except Exception as errore:
        print(f"   FALLITO: {type(errore).__name__}: {errore}")
        return 1
    return 0


def main() -> None:
    _carica_env()

    analizzatore = argparse.ArgumentParser(
        prog="italia-mcp-bridge",
        description="Collega gli strumenti italiani al tuo dispositivo xiaozhi.",
    )
    analizzatore.add_argument("--endpoint", default=os.environ.get("MCP_ENDPOINT"))
    analizzatore.add_argument("--selftest", action="store_true",
                              help="diagnostica e termina")
    analizzatore.add_argument("--verbose", action="store_true")
    argomenti = analizzatore.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if argomenti.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s %(message)s",
        datefmt="%H:%M:%S",
    )

    endpoint = (argomenti.endpoint or "").strip().strip('"').strip("'")

    if argomenti.selftest:
        sys.exit(anyio.run(_diagnostica, endpoint or None))

    if not endpoint:
        print("Manca l'indirizzo dell'endpoint MCP.\n")
        print("Prendilo dalla console di xiaozhi.me:")
        print("  Configure -> Extensions -> MCP Endpoint -> icona copia\n")
        print("Poi mettilo in un file .env accanto a questo programma:")
        print("  MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=...\n")
        print("oppure passalo con  --endpoint wss://...")
        sys.exit(2)

    if not endpoint.startswith(("ws://", "wss://")):
        print(f"L'indirizzo deve iniziare con wss:// oppure ws:// (ricevuto: {endpoint[:30]}...)")
        sys.exit(2)

    try:
        anyio.run(_ciclo, endpoint)
    except KeyboardInterrupt:
        logger.info("Interrotto.")


if __name__ == "__main__":
    main()
