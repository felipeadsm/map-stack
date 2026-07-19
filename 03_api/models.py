"""Modelos ORM (Object-Relational Mapper): classes Python que representam
tabelas do banco. Cada instancia = uma linha; cada atributo = uma coluna.
Isso evita escrever SQL na mao no dia a dia -- o SQLAlchemy traduz
`select(Telemetria).where(...)` em SQL por baixo dos panos.

Estas classes so *descrevem* as tabelas que ja existem (criadas no
02_postgis/01_setup.sql) -- nao criam nada novas aqui.

`Geometry(...)` vem do GeoAlchemy2, a extensao que ensina o SQLAlchemy a
entender a coluna espacial do PostGIS como um tipo de dado Python (em vez
de trata-la como texto opaco).
"""

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Geocerca(Base):
    __tablename__ = "geocercas"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    geom = Column(Geometry(geometry_type="POLYGON", srid=4326))


class Telemetria(Base):
    __tablename__ = "telemetria"

    id = Column(Integer, primary_key=True)
    veiculo_id = Column(String, nullable=False)
    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    capturado_em = Column(DateTime(timezone=True))
