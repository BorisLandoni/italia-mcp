# Installare e provare `italia-mcp` su un PC

Guida per Windows, macOS e Linux. Serve **Python 3.10 o superiore**.

```bash
python --version
```

Su Windows, se il comando non esiste, installa Python da
[python.org](https://www.python.org/downloads/) ricordandoti di spuntare
**"Add Python to PATH"** durante l'installazione.

---

## 1. Scarica il progetto

**Windows (PowerShell)**

> ⚠️ In PowerShell 5.1 l'operatore `&&` non esiste: i comandi vanno separati da `;`
> oppure scritti su righe diverse. E `curl` è un alias di `Invoke-WebRequest`,
> quindi `curl -O` non funziona come su Linux.

```powershell
cd $HOME\Documents
git clone https://github.com/BorisLandoni/italia-mcp.git
cd italia-mcp
```

**macOS e Linux**

```bash
cd ~ && git clone https://github.com/BorisLandoni/italia-mcp.git && cd italia-mcp
```

Se non hai `git`, scarica lo zip da GitHub (*Code → Download ZIP*) e scompattalo.

## 2. Crea l'ambiente virtuale

Serve a non sporcare il Python di sistema: tutto quello che installi resta in una
cartella `.venv` dentro il progetto, e per disinstallare basta cancellarla.

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e .
```

**macOS e Linux**

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
```

Il `-e` (*editable*) fa sì che le modifiche al codice abbiano effetto subito, senza
reinstallare: comodo mentre aggiungi strumenti tuoi.

## 3. Provalo

Nel progetto c'è uno script che chiama tutti gli strumenti e misura quanto pesano le
risposte, senza bisogno di collegare niente:

```powershell
.venv\Scripts\python.exe prova.py
```

```bash
./.venv/bin/python prova.py
```

Output atteso:

```
[            ok]  148 byte    448 ms  meteo_adesso
                 {"ok": true, "citta": "Gallarate", "cielo": "coperto", ...
[            ok]  228 byte   1010 ms  allerte_protezione_civile
                 {"ok": true, "comune": "Arsago Seprio", "allerta": "ARANCIONE", ...
...
Risposta piu' pesante: 409 byte su un limite di 1024.
Tutti gli strumenti rispondono correttamente.
```

Per provarne uno solo:

```bash
python prova.py meteo
python prova.py futura
```

Se tutti gli strumenti rispondono `ok`, il server funziona: quello che resta è solo
collegarlo a qualcosa.

## 4. Avvia il server vero

```powershell
.venv\Scripts\python.exe -m italia_mcp
```

**Il cursore resta fermo e non compare niente: è corretto.** Il server parla il
protocollo MCP su stdin/stdout e aspetta che un client gli scriva. Non stampa mai
nulla di suo — se lo facesse romperebbe il protocollo. Chiudi con `Ctrl+C`.

Per verificare che risponda davvero, incolla questo mentre è in esecuzione e premi
Invio due volte:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}
```

Deve rispondere una riga JSON che contiene `"serverInfo"`.

## 5. Collegalo a un client

**Claude Desktop, Cursor, Cherry Studio** — nel file di configurazione MCP:

```json
{
  "mcpServers": {
    "italia": {
      "command": "C:\Users\NOME\Documents\italia-mcp\.venv\Scripts\python.exe",
      "args": ["-m", "italia_mcp"]
    }
  }
}
```

Su macOS e Linux il `command` è `/percorso/italia-mcp/.venv/bin/python`.

**Il panda (xiaozhi)** — vedi [`../xiaozhi/README.md`](../xiaozhi/README.md).

**Sempre acceso su un Raspberry** — vedi [`raspberry.md`](raspberry.md).

## Problemi frequenti

| Sintomo | Causa | Rimedio |
|---|---|---|
| `python non è riconosciuto` | Python non nel PATH | Reinstalla spuntando *Add Python to PATH*, oppure usa `py` al posto di `python` |
| `No module named 'italia_mcp'` | Ambiente virtuale non attivo | Usa il percorso completo `.venv\Scripts\python.exe`, non `python` |
| `No module named 'mcp.server.fastmcp'` | Installato `mcp` 2.x | `pip install "mcp<2"`: in 2.x FastMCP è stato rinominato |
| `Il token '&&' non è un separatore valido` | Comando bash in PowerShell | Usa `;` al posto di `&&` |
| Tutto `ok` ma risposte lentissime | Prima chiamata alle allerte | Il bollettino della Protezione Civile pesa 2,8 MB e viene messo in cache per un'ora: solo la prima volta è lenta |
