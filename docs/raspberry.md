# Raspberry Pi come gateway sempre acceso

Il modo giusto di far vivere questo server. L'endpoint MCP di xiaozhi è un WebSocket
che **il tuo lato deve tenere aperto**: se spegni il PC, il panda perde gli strumenti.
Un Raspberry consuma pochi watt, sta acceso h24 e risolve il problema.

## Quale Raspberry serve

Molto meno di quanto pensi. Il processo occupa **circa 30 MB di RAM** e resta quasi
sempre inattivo, in attesa sul socket.

| Modello | Va bene? |
|---|---|
| Pi Zero 2 W | Sì, abbondantemente |
| Pi 3 / 3B+ | Sì |
| Pi 4 / 5 | Sì, sovradimensionato |
| Pi Zero W (prima serie) | Sconsigliato: single core ARMv6, Python moderno ci gira male |

Serve **Raspberry Pi OS** (o qualsiasi Debian/Ubuntu) e una connessione di rete,
meglio via cavo se il Raspberry sta vicino al router.

Se hai già un Raspberry con Home Assistant, Pi-hole o simili, mettilo lì: non
darà fastidio.

---

## 1. Preparazione

Collegati via SSH e aggiorna:

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git
```

## 2. Installazione

```bash
cd ~
git clone https://github.com/BorisLandoni/italia-mcp.git
cd italia-mcp
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
./.venv/bin/python -m pip install websockets python-dotenv
```

Verifica che tutto risponda prima di andare avanti:

```bash
./.venv/bin/python prova.py
```

## 3. Scarica il ponte

`mcp_pipe.py` è il ponte ufficiale fra il tuo server MCP e xiaozhi. Non è incluso in
questo repository perché il progetto originale non dichiara una licenza.

```bash
wget https://raw.githubusercontent.com/78/mcp-calculator/main/mcp_pipe.py
```

## 4. Metti l'indirizzo dell'endpoint

Dalla console di [xiaozhi.me](https://xiaozhi.me): **Configure → Extensions →
MCP Endpoint → icona copia**. E già che ci sei, **togli la spunta all'estensione
`Weather`** e salva, altrimenti il modello ha due strumenti meteo e sceglie a caso.

```bash
nano ~/italia-mcp/.env
```

Una sola riga, senza spazi e senza virgolette:

```
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=IL_TUO_TOKEN
```

Il token è una password. Proteggi il file:

```bash
chmod 600 ~/italia-mcp/.env
```

## 5. Prova a mano

```bash
cd ~/italia-mcp
./.venv/bin/python mcp_pipe.py xiaozhi/italia_server.py
```

Deve comparire `Successfully connected to WebSocket server`. Sulla console di
xiaozhi.me premi il refresh accanto a *Endpoint Status*: deve diventare
**Connected**. Poi ferma tutto con `Ctrl+C`: adesso lo rendiamo automatico.

---

## 6. Servizio systemd (la parte che conta)

Così parte da solo all'accensione, riparte se va in crash e riparte se salta la rete.

```bash
sudo nano /etc/systemd/system/italia-mcp.service
```

```ini
[Unit]
Description=italia-mcp -> xiaozhi (panda)
Documentation=https://github.com/BorisLandoni/italia-mcp
After=network-online.target
Wants=network-online.target

# se il servizio va in crash loop, systemd di default lo arrende dopo 5 tentativi
# in 10 secondi: qui glielo impediamo, deve insistere per sempre.
# Attenzione: dal systemd 229 questa direttiva vive in [Unit], non in [Service],
# dove verrebbe semplicemente ignorata.
StartLimitIntervalSec=0

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/italia-mcp
EnvironmentFile=/home/pi/italia-mcp/.env
ExecStart=/home/pi/italia-mcp/.venv/bin/python mcp_pipe.py xiaozhi/italia_server.py

# riparte sempre, con 10 secondi di attesa fra un tentativo e l'altro
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal

# irrobustimento di base
NoNewPrivileges=true
PrivateTmp=false
ProtectSystem=full

[Install]
WantedBy=multi-user.target
```

> Se il tuo utente non è `pi`, cambia **sia** `User=` **sia** i percorsi.
> Verifica con `whoami` e `pwd`.

Attiva:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now italia-mcp
```

Controlla:

```bash
systemctl status italia-mcp
```

Deve dire `active (running)`.

## 7. Comandi di gestione quotidiana

| Cosa vuoi fare | Comando |
|---|---|
| Vedere se gira | `systemctl status italia-mcp` |
| Leggere i log dal vivo | `journalctl -u italia-mcp -f` |
| Ultimi 100 log | `journalctl -u italia-mcp -n 100` |
| Riavviare | `sudo systemctl restart italia-mcp` |
| Fermare | `sudo systemctl stop italia-mcp` |
| Non partire più all'avvio | `sudo systemctl disable italia-mcp` |
| Dopo aver cambiato `.env` | `sudo systemctl restart italia-mcp` |

## 8. Aggiornare all'ultima versione

```bash
cd ~/italia-mcp
git pull
./.venv/bin/python -m pip install -e .
sudo systemctl restart italia-mcp
```

## 9. Quanto consuma davvero

```bash
systemctl status italia-mcp | grep Memory
```

Attorno ai **30 MB**. Su una scheda da 512 MB resta il 94% libero. Il traffico di
rete a riposo è solo il ping del WebSocket ogni ~20 secondi: qualche decina di byte.

---

## Problemi frequenti

| Sintomo | Causa | Rimedio |
|---|---|---|
| `Please set the MCP_ENDPOINT environment variable` | `.env` vuoto o percorso sbagliato in `EnvironmentFile` | Controlla il percorso assoluto, poi `daemon-reload` e `restart` |
| Parte prima della rete e va in loop | Rete non pronta al boot | `Restart=always` lo risolve da solo dopo 10 s; per pulizia abilita `sudo systemctl enable systemd-networkd-wait-online` |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Ispezione TLS o certificati di sistema vecchi | `sudo apt install --reinstall ca-certificates`; in ultima istanza usa `ws://` al posto di `wss://` |
| Si scollega ogni tanto e torna | Normale | `mcp_pipe.py` si riconnette da solo, con attesa crescente |
| Stato `Connected` ma il panda ignora gli strumenti | Estensione `Weather` ancora attiva, o troppi strumenti collegati | Togli la spunta a `Weather`; tieni un solo server MCP per endpoint |
| `status` dice `active` ma non si collega mai | Endpoint di un altro agente | Ricopia l'indirizzo dalla scheda dell'agente giusto |

## Un Raspberry per più panda?

Sì, ma con attenzione. `mcp_pipe.py` apre **una connessione WebSocket per ogni server
elencato** in `mcp_config.json`, e ogni endpoint xiaozhi ha un tetto di connessioni.

Per servire più dispositivi, la strada è un servizio systemd per ciascuno, con un file
`.env` diverso:

```bash
sudo cp /etc/systemd/system/italia-mcp.service /etc/systemd/system/italia-mcp@.service
```

Modifica il file `@` sostituendo il percorso dell'`EnvironmentFile` con
`/home/pi/italia-mcp/env/%i.env`, poi crea un file per ogni panda
(`env/salotto.env`, `env/cucina.env`) e attivali:

```bash
sudo systemctl enable --now italia-mcp@salotto
sudo systemctl enable --now italia-mcp@cucina
```

Ogni istanza costa circa 30 MB. Oltre la decina di dispositivi conviene un ponte
multi-tenant che tenga tutte le connessioni in un processo solo: a quel punto il costo
scende a circa 111 KB per dispositivo.
