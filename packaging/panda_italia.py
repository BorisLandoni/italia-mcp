"""Punto di ingresso per l'eseguibile impacchettato.

Deve importare il PACCHETTO, non il modulo: puntare PyInstaller direttamente a
bridge.py rompe gli import relativi ("attempted relative import with no known
parent package").
"""

from italia_mcp.bridge import main

if __name__ == "__main__":
    main()
