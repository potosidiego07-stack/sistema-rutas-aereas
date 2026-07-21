from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
import datetime

class Aeropuerto(Base):
    __tablename__ = "aeropuertos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_iata = Column(String, unique=True, index=True)
    nombre = Column(String)
    ciudad = Column(String)
    pais = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
    clima = Column(String, default="DESPEJADO")

class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    origen_id = Column(Integer, ForeignKey("aeropuertos.id"))
    destino_id = Column(Integer, ForeignKey("aeropuertos.id"))
    distancia_km = Column(Float)
    tiempo_estimado_min = Column(Integer)
    costo_operativo = Column(Float)
    consumo_combustible_gal = Column(Float)

class Aeronave(Base):
    __tablename__ = "aeronaves"

    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String)
    matricula = Column(String)
    factor_velocidad = Column(Float, default=1.0)
    factor_consumo = Column(Float, default=1.0)

class HistorialSimulacion(Base):
    __tablename__ = "historial_simulaciones"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    origen_iata = Column(String)
    destino_iata = Column(String)
    aeronave_matricula = Column(String)
    criterio = Column(String)
    distancia_total = Column(Float)
    tiempo_total_min = Column(Integer)
    costo_total = Column(Float)
    combustible_total = Column(Float)
    escalas = Column(Integer, default=0)