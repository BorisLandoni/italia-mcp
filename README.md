# italia-mcp

**Servizi italiani essenziali per assistenti vocali, via MCP.** Meteo, allerte della
Protezione Civile, notizie ANSA e promemoria — in italiano, con 8 strumenti in tutto.

> *Italian essentials (weather, Civil Protection alerts, ANSA news, reminders) as a
> Model Context Protocol server. Tool descriptions and responses are in Italian.*

Nato per il chatbot vocale **[xiaozhi-esp32](https://github.com/78/xiaozhi-esp32)**
(il "panda"), ma è un normale server MCP: funziona con Claude Desktop, Cursor,
Cherry Studio e qualsiasi client compatibile.

## Perché esiste

I server MCP meteo che si trovano in giro sono pensati per assistenti da scrivania,
dove il contesto è enorme e nessuno conta i byte. Su un dispositivo vocale basato su
ESP32 i vincoli sono un altro mondo:

| | server MCP meteo tipico | `italia-mcp` |
|---|---|---|
| Numero di strumenti | 17 | **8** |
| Peso dell'elenco strumenti | ~29.700 token | **~800 token** |
| Risposta | JSON grezzo, fino a 25.000 caratteri | **sotto 1.024 byte** |
| Lingua | inglese, fuso GMT | **italiano, fuso locale** |
| Come indichi il luogo | latitudine e longitudine | **nome del comune** |
| Dipendenze | varie | **una sola** (`mcp`) |

L'elenco degli strumenti viaggia in *ogni* richiesta al modello: è lì che si vince o
si perde. Tutto il resto del progetto discende da questo.

## Strumenti

| Strumento | Che cosa fa |
|---|---|
| `meteo_adesso(citta)` | Tempo attuale: cielo, temperatura, percepita, umidità, vento |
| `meteo_previsioni(citta, giorni)` | Previsioni da 1 a 7 giorni con probabilità di pioggia |
| `allerte_protezione_civile(comune)` | Allerta gialla/arancione/rossa per temporali, rischio idraulico e idrogeologico |
| `qualita_aria(citta)` | Indice europeo, PM10, PM2.5 |
| `notizie_italia(argomento)` | Ultimi titoli ANSA: principali, cronaca, politica, economia, mondo, tecnologia, sport |
| `promemoria_aggiungi(testo)` | Aggiunge un promemoria o un articolo alla lista della spesa |
| `promemoria_elenco()` | Legge la lista |
| `promemoria_rimuovi(numero_o_testo)` | Toglie una voce, o svuota tutto con `"tutto"` |

## Installazione

```bash
pip install italia-mcp
```

Poi, per provarlo:

```bash
italia-mcp
```

Il server parla MCP su stdio: da solo non stampa nulla, è normale.

## Uso con Claude Desktop, Cursor e simili

```json
{
  "mcpServers": {
    "italia": { "command": "italia-mcp" }
  }
}
```

## Uso con il panda (xiaozhi)

Il panda non chiama un URL: è il tuo server che deve **collegarsi** all'endpoint MCP
del dispositivo e tenere aperta la connessione. Serve il ponte ufficiale
[`mcp_pipe.py`](https://github.com/78/mcp-calculator).

1. Nella console di [xiaozhi.me](https://xiaozhi.me) apri
   **Configure → Extensions → MCP Endpoint** e copia l'indirizzo
   `wss://api.xiaozhi.me/mcp/?token=...` (è un segreto, trattalo come una password).
2. Togli la spunta all'estensione ufficiale **Weather**, altrimenti il modello ha due
   strumenti meteo e sceglie a caso.
3. Avvia il ponte:

```bash
pip install italia-mcp websockets python-dotenv
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=..."
python mcp_pipe.py xiaozhi/italia_server.py
```

Vedi [`xiaozhi/`](xiaozhi/) per gli script pronti e la guida passo passo.

### Vincoli della piattaforma da rispettare

Dalla [documentazione ufficiale](https://my.feishu.cn/wiki/HiPEwZ37XiitnwktX13cEM5KnSb):

- la risposta di uno strumento è limitata a circa **1.024 byte**;
- l'elenco degli strumenti ha un tetto misurato in token;
- ogni endpoint ha un **limite di connessioni**: usa un solo server MCP, non uno per
  servizio;
- mai `print()` nel codice di uno strumento: stdin/stdout sono il canale di trasporto.

## Fonti dei dati

| Dato | Fonte | Licenza |
|---|---|---|
| Meteo, previsioni, qualità aria | [Open-Meteo](https://open-meteo.com) | CC BY 4.0, gratuito senza chiave |
| Allerte meteo-idro | [Dipartimento della Protezione Civile](https://github.com/pcm-dpc/DPC-Bollettini-Criticita-Idrogeologica-Idraulica), in CSV via [OpenData Sicilia](https://github.com/opendatasicilia/DPC-bollettini-criticita-idrogeologica-idraulica) | CC BY 4.0 |
| Notizie | Feed RSS pubblici [ANSA](https://www.ansa.it) | uso citazionale dei soli titoli |

**Nessuna chiave API richiesta.**

### Nota importante sulle allerte

Il bollettino della Protezione Civile esce entro le 16:00 e il mirror può avere
qualche ora di ritardo. Il codice **non si fida del nome del file**: legge la finestra
di validità dichiarata dentro il bollettino e usa solo quello valido in questo
momento. Se nessuno è valido, lo dice invece di rispondere con dati vecchi.
Ogni risposta include `valido_fino`.

> Questo software non è un servizio di allerta ufficiale e non sostituisce i canali
> della Protezione Civile. Per le emergenze fai sempre riferimento alle fonti ufficiali.

## Limiti noti

- **Non può svegliare il dispositivo.** I promemoria si consultano a voce, non
  suonano da soli: nel protocollo xiaozhi il server non può iniziare una
  conversazione.
- **Non riproduce musica.** Il canale audio è Opus binario, gli strumenti MCP
  scambiano solo testo.
- I promemoria sono salvati in un file locale, senza account: chi ha accesso al
  server li vede tutti.

## Licenza

Codice: MIT. I dati restano dei rispettivi titolari, alle licenze indicate sopra.
