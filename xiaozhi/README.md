# Collegare `italia-mcp` al panda (xiaozhi)

## Come funziona davvero

L'endpoint MCP di xiaozhi **non è un URL che il dispositivo chiama**: è un WebSocket a
cui il *tuo* server si collega e che deve restare aperto. Per questo serve qualcosa di
sempre acceso — un PC, un Raspberry, un NAS o un piccolo VPS. Se spegni il processo, il
panda perde gli strumenti.

```
  panda  ──audio──▶  xiaozhi.me  ◀──WebSocket──  mcp_pipe.py  ──stdio──▶  italia-mcp
                                  (connessione aperta dal tuo lato)
```

## Passi

**1. Installa**

```bash
pip install italia-mcp websockets python-dotenv
```

**2. Prendi il ponte ufficiale**

```bash
curl -O https://raw.githubusercontent.com/78/mcp-calculator/main/mcp_pipe.py
```

**3. Copia l'indirizzo dell'endpoint**

Console di [xiaozhi.me](https://xiaozhi.me) → **Configure** → **Extensions** →
**MCP Endpoint** → icona *copia*. Sarà simile a
`wss://api.xiaozhi.me/mcp/?token=...`

⚠️ Contiene un token: è una password, non condividerlo e non metterlo in un repo.

**4. Togli la spunta a `Weather`**

Sempre in **Extensions**, sotto *Official Services*. Se resta attiva, il modello ha due
strumenti meteo e sceglie a caso quello che non parla italiano. Poi **Save**.

**5. Metti l'endpoint in un file `.env`**

```
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=...
```

**6. Avvia**

```bash
python mcp_pipe.py italia_server.py
```

Deve comparire `Successfully connected to WebSocket server`. Torna sulla console,
premi il refresh accanto a *Endpoint Status*: deve diventare **Connected**.

## Prova a voce

- *"Che tempo fa a Gallarate?"*
- *"Che tempo farà nel fine settimana?"*
- *"C'è allerta meteo ad Arsago Seprio?"*
- *"Com'è l'aria a Milano?"*
- *"Dammi le notizie di tecnologia"*
- *"Ricordami di comprare il latte"* → *"Cosa devo ricordare?"*

## Se qualcosa non va

| Sintomo | Causa | Rimedio |
|---|---|---|
| `Please set the MCP_ENDPOINT environment variable` | `.env` vuoto o nella cartella sbagliata | Il `.env` va accanto a `mcp_pipe.py` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Ispezione TLS sulla rete | Usa `ws://` al posto di `wss://` |
| Resta `Not Connected` | Il processo non gira, o l'endpoint è di un altro agente | Ricontrolla la finestra del terminale e ricopia l'indirizzo |
| Si scollega ogni tanto | Normale | `mcp_pipe.py` si riconnette da solo |
| Il panda inventa il meteo | Estensione `Weather` ancora attiva | Togli la spunta e salva |

## Farlo partire da solo (Windows)

Crea un collegamento a `AVVIA.bat` dentro
`shell:startup` (Win+R → `shell:startup`).

```bat
@echo off
cd /d "%~dp0"
python mcp_pipe.py italia_server.py
pause
```
