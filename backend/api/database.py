"""Conexao com o banco. Sem 'ORM' ainda -- so a fiacao basica.

DATABASE_URL segue o padrao de connection string do SQLAlchemy:
  dialeto+driver://usuario:senha@host:porta/banco
"dialeto" e o tipo de banco (postgresql); "driver" e a biblioteca Python
que fala o protocolo do banco (psycopg, o driver do Postgres para Python).
A porta 5433 e a que mapeamos no docker-compose.yml do marco 2.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://mapstack:mapstack@localhost:5433/mapstack"
)

# "engine" e o objeto que sabe abrir conexoes com o banco (gerencia um pool
# delas por baixo dos panos). "SessionLocal" e uma fabrica de "sessions":
# cada session e uma conversa com o banco (abre, faz queries, fecha).
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
