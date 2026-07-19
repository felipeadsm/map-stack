"""Configuracao compartilhada dos testes.

`api/` nao e um pacote Python instalado -- e so uma pasta de scripts que
rodam com o proprio diretorio no sys.path (o que acontece automaticamente
quando voce roda `python api/main.py` direto). Para os testes importarem
essas mesmas coisas (`import database`, `import main`, etc.) precisamos
adicionar essa pasta ao sys.path manualmente aqui.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "api"))
