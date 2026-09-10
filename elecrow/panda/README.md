# Elecrow AI Panda ChatBot

Guida specifica per questo dispositivo. Per la documentazione generale del
progetto vedi il [README principale](../../README.md).

## Il dispositivo

| | |
|---|---|
| Prodotto | AI Panda ChatBot — "compagno emotivo" con controllo vocale |
| Modello | **AIB00101D** |
| Modulo | **ESP32-S3N16R8** — 16 MB flash, 8 MB PSRAM ottale |
| Display | IPS tondo 1.28", 240×240, non touch |
| Altro | LED ambientali RGB, microfono, altoparlante, batteria, USB-C |
| Backend | [xiaozhi.me](https://xiaozhi.me) (account creato dall'utente) |
| Pagina prodotto | [elecrow.com](https://www.elecrow.com/ai-panda-chatbot-with-intelligent-voice-control-emotional-companion-voice-assistant.html) |
| Wiki | [AI_Panda_ChatBot](https://www.elecrow.com/wiki/AI_Panda_ChatBot.html) |

## Avvio rapido su Windows

1. Scarica **`PandaItalia.exe`** dalla pagina
   [Releases](https://github.com/BorisLandoni/italia-mcp/releases).
2. Sulla console di [xiaozhi.me](https://xiaozhi.me):
   **Configure → Extensions**, togli la spunta a **`Weather`** e premi **Save**.
   *(Se resta attiva, il panda ha due servizi meteo e ne sceglie uno a caso —
   è l'errore più comune.)*
3. Sempre lì, apri **MCP Endpoint** e clicca l'icona **copia**.
4. Avvia `PandaItalia.exe`, premi **Incolla**, poi **Collega**.

Il pallino diventa verde. L'indirizzo viene salvato: **dal secondo avvio in poi
il collegamento parte da solo**, non devi reinserire nulla.

Prova a voce: *"Che tempo fa a Gallarate?"*, *"C'è allerta meteo ad Arsago
Seprio?"*, *"Dammi le notizie di tecnologia"*.

### Dove finisce l'indirizzo salvato

```
Windows   %APPDATA%\PandaItalia\config.json
macOS     ~/Library/Application Support/PandaItalia/config.json
Linux     ~/.config/panda-italia/config.json
```

Contiene il token del tuo agente: trattalo come una password. Per cambiarlo,
riapri il programma e incolla il nuovo indirizzo.

### Cosa aspettarsi al primo avvio

L'eseguibile **non è firmato digitalmente**, quindi Windows SmartScreen mostra
*"Windows ha protetto il PC"*. Serve **Ulteriori informazioni → Esegui
comunque**. Alcuni antivirus segnalano falsi positivi sui binari PyInstaller.

## L'eseguibile è per la prova, non per l'uso quotidiano

Funziona benissimo per collaudare il panda in cinque minuti, ma per tenerlo
sempre operativo ha due limiti che non dipendono dal software:

- **Windows va in sospensione** e il ponte cade con lui;
- **i riavvii di Windows Update** lo interrompono circa una volta al mese, e
  serve rientrare nel PC per farlo ripartire.

Per l'uso continuativo conviene un dispositivo Linux sempre acceso — anche un
Raspberry Pi Zero 2 W basta e avanza: vedi
**[docs/raspberry.md](../../docs/raspberry.md)**, dove `systemd` riavvia il
servizio da solo anche dopo un blackout.

## Un guasto silenzioso, e come riconoscerlo

Se il ponte cade, **il panda continua a parlare benissimo** e semplicemente non
sa più il meteo. Non sembra rotto: sembra diventato stupido. E il server non può
avvisarti, perché nel protocollo xiaozhi non può iniziare una conversazione.

La frase di verifica è questa:

> *"Che tempo fa a Gallarate?"*

Se risponde con dati precisi (cielo, gradi, umidità, vento) il ponte è attivo.
Se risponde in modo vago o dice di non saperlo, controlla il programma.

Il pulsante **Diagnostica** nella finestra distingue i due casi: verifica gli
strumenti e l'accesso a Internet separatamente dal collegamento.

## Firmware: stato della ricerca

**I sorgenti del firmware non sono pubblici.** Verificato il 10 settembre 2026
su tre fronti:

| Dove | Esito |
|---|---|
| Wiki Elecrow del prodotto | Solo guida utente per xiaozhi.me. Nessun `.bin`, nessuno schema, nessuna istruzione di flash |
| Organizzazione [Elecrow-RD](https://github.com/Elecrow-RD) su GitHub | 138 repository, alcuni aggiornati di recente, **nessuno per l'AI Panda**. I sorgenti vengono pubblicati per CrowPanel e CrowPi, cioè i prodotti rivolti a chi programma |
| [78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) | Nessuna board Elecrow fra quelle supportate a monte |

Un tentativo di integrazione a livello di firmware — che eliminerebbe del tutto
la necessità di un computer acceso — richiederebbe il *board file* con la
mappatura dei pin di display, codec audio, microfono e LED. Senza quello non è
un port, è un bring-up hardware da zero.

Unico canale: `techsupport@elecrow.com`.

Nota anche che, con la partition table di default, i 16 MB di flash risultano
già occupati (nvs, otadata, phy_init, due partizioni OTA e gli asset): la cache
del bollettino della Protezione Civile, da circa 2,7 MB, non avrebbe dove
stare senza sacrificare il rollback OTA.
