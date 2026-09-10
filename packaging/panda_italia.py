"""Punto di ingresso dell'eseguibile Panda Italia.

Deve importare il PACCHETTO, non il modulo: puntare PyInstaller direttamente a
un file dentro italia_mcp lo esegue come script isolato e gli import relativi
falliscono a runtime con "attempted relative import with no known parent
package", pur compilando senza errori.

Senza argomenti apre la finestra; con argomenti (--selftest, --endpoint) si
comporta da programma a riga di comando.

L'eseguibile viene compilato in modalita' console, non --windowed: in modalita'
finestra PyInstaller azzera sys.stdout e ogni print() della modalita' testo
solleverebbe un errore. Quando parte la finestra nascondiamo noi la console,
cosi' l'utente grafico non la vede e quello da terminale legge l'output.
"""

import sys


def _nascondi_console():
    if sys.platform != "win32":
        return
    try:
        import ctypes

        finestra = ctypes.windll.kernel32.GetConsoleWindow()
        if finestra:
            ctypes.windll.user32.ShowWindow(finestra, 0)  # 0 = SW_HIDE
    except Exception:
        pass


def main():
    argomenti = [a for a in sys.argv[1:] if a != "--nogui"]

    if len(sys.argv) > 1:
        from italia_mcp.bridge import main as riga_di_comando

        sys.argv = [sys.argv[0]] + argomenti
        return riga_di_comando()

    _nascondi_console()
    from italia_mcp.gui import main as finestra

    return finestra()


if __name__ == "__main__":
    sys.exit(main() or 0)
