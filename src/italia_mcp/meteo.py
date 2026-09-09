"""Meteo e qualita dell'aria. Fonte: Open-Meteo."""

import datetime
import urllib.parse

from .geo import scarica_json, trova

# Codici meteo WMO tradotti in italiano parlato
CODICI = {
    0: "sereno", 1: "prevalentemente sereno", 2: "parzialmente nuvoloso", 3: "coperto",
    45: "nebbia", 48: "nebbia con brina",
    51: "pioviggine leggera", 53: "pioviggine", 55: "pioviggine intensa",
    56: "pioviggine gelata", 57: "pioviggine gelata intensa",
    61: "pioggia leggera", 63: "pioggia", 65: "pioggia forte",
    66: "pioggia gelata", 67: "pioggia gelata forte",
    71: "neve leggera", 73: "neve", 75: "neve abbondante", 77: "granelli di neve",
    80: "rovesci leggeri", 81: "rovesci", 82: "rovesci violenti",
    85: "rovesci di neve", 86: "rovesci di neve intensi",
    95: "temporale", 96: "temporale con grandine", 99: "temporale con forte grandine",
}

GIORNI = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]


def _cielo(codice) -> str:
    return CODICI.get(codice, "condizioni variabili")


def _previsione_url(luogo: dict, **extra) -> str:
    parametri = {
        "latitude": luogo["latitude"],
        "longitude": luogo["longitude"],
        "timezone": "auto",
        **extra,
    }
    return "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(parametri)


def adesso(citta: str) -> dict:
    luogo = trova(citta)
    if not luogo:
        return {"ok": False, "errore": f"Non trovo la localita '{citta}'"}

    d = scarica_json(
        _previsione_url(
            luogo,
            current="temperature_2m,apparent_temperature,relative_humidity_2m,"
                    "precipitation,weather_code,wind_speed_10m",
        )
    )["current"]

    return {
        "ok": True,
        "citta": luogo["name"],
        "cielo": _cielo(d["weather_code"]),
        "temperatura_c": round(d["temperature_2m"]),
        "percepita_c": round(d["apparent_temperature"]),
        "umidita_pct": d["relative_humidity_2m"],
        "vento_kmh": round(d["wind_speed_10m"]),
        "pioggia_mm": d["precipitation"],
    }


def previsioni(citta: str, giorni: int = 3) -> dict:
    giorni = max(1, min(int(giorni), 7))
    luogo = trova(citta)
    if not luogo:
        return {"ok": False, "errore": f"Non trovo la localita '{citta}'"}

    d = scarica_json(
        _previsione_url(
            luogo,
            daily="weather_code,temperature_2m_max,temperature_2m_min,"
                  "precipitation_probability_max",
            forecast_days=giorni,
        )
    )["daily"]

    elenco = []
    for i, giorno in enumerate(d["time"]):
        data = datetime.date.fromisoformat(giorno)
        elenco.append({
            "giorno": GIORNI[data.weekday()],
            "cielo": _cielo(d["weather_code"][i]),
            "min_c": round(d["temperature_2m_min"][i]),
            "max_c": round(d["temperature_2m_max"][i]),
            "prob_pioggia_pct": d["precipitation_probability_max"][i],
        })

    return {"ok": True, "citta": luogo["name"], "previsioni": elenco}


def _giudizio_aria(indice) -> str:
    """Scala dell'indice europeo di qualita dell'aria."""
    if indice is None:
        return "non disponibile"
    for soglia, etichetta in ((20, "ottima"), (40, "buona"), (60, "discreta"),
                              (80, "scarsa"), (100, "cattiva")):
        if indice <= soglia:
            return etichetta
    return "pessima"


def aria(citta: str) -> dict:
    luogo = trova(citta)
    if not luogo:
        return {"ok": False, "errore": f"Non trovo la localita '{citta}'"}

    query = urllib.parse.urlencode({
        "latitude": luogo["latitude"],
        "longitude": luogo["longitude"],
        "current": "european_aqi,pm10,pm2_5",
        "timezone": "auto",
    })
    d = scarica_json(
        "https://air-quality-api.open-meteo.com/v1/air-quality?" + query
    )["current"]

    indice = d.get("european_aqi")
    return {
        "ok": True,
        "citta": luogo["name"],
        "qualita_aria": _giudizio_aria(indice),
        "indice_europeo": indice,
        "pm10": d.get("pm10"),
        "pm2_5": d.get("pm2_5"),
    }
