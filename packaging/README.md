# Creare l'eseguibile Windows

Un file unico da ~16 MB che contiene Python, il server MCP e il ponte verso
xiaozhi. Sulla macchina del cliente non serve installare nulla.

```powershell
.venv\Scripts\python.exe -m pip install pyinstaller
.venv\Scripts\python.exe -m PyInstaller --onefile --name PandaItalia --console ^
    --collect-submodules italia_mcp packaging\panda_italia.py
```

L'eseguibile finisce in `dist\PandaItalia.exe`.

**Il punto di ingresso deve essere `packaging/panda_italia.py`, non
`src/italia_mcp/bridge.py`.** Puntare PyInstaller direttamente al modulo lo
esegue come script isolato e gli import relativi falliscono con
`attempted relative import with no known parent package`.

## Verifica dopo la compilazione

```powershell
dist\PandaItalia.exe --selftest --endpoint "wss://api.xiaozhi.me/mcp/?token=QUALSIASI"
```

Con un token non valido la terza riga deve dire `handshake OK ma token rifiutato
(HTTP 401)`: significa che TLS, WebSocket e raggiungibilita' dell'endpoint
funzionano, e manca solo il token vero.

## Da sapere prima di distribuirlo

- **L'eseguibile non e' firmato**: Windows SmartScreen mostrera' "PC protetto"
  al primo avvio e alcuni antivirus danno falsi positivi sui binari PyInstaller.
  Un certificato code signing OV costa alcune centinaia di euro l'anno.
- **Windows va in sospensione** e i riavvii di Windows Update interrompono il
  ponte. Per un uso continuativo conviene una macchina Linux con systemd
  (vedi `docs/raspberry.md`); questo eseguibile e' pensato per la prova rapida.
- Il primo avvio impiega qualche secondo in piu': l'onefile si scompatta.
