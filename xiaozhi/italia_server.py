"""Avvio del server per il ponte mcp_pipe.py.

mcp_pipe.py accetta il percorso di uno script Python, non un modulo:
questo file esiste solo per fargli da bersaglio.

    python mcp_pipe.py xiaozhi/italia_server.py
"""

from italia_mcp.__main__ import main

if __name__ == "__main__":
    main()
