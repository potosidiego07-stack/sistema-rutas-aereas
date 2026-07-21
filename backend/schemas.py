from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AeropuertoBase(BaseModel):
    codigo_iata: str
    nombre: str
    ciudad: str
    pais: str
    latitud: float
    longitud: float

class AeropuertoCreate(AeropuertoBase):
    clima: Optional[str] = "DESPEJADO"

class AeropuertoResponse(AeropuertoBase):
    id: int
    clima: str
    class Config:
        from_attributes = True

class RutaBase(BaseModel):
    origen_id: int
    destino_id: int
    distancia_km: float
    tiempo_estimado_min: int
    costo_operativo: float
    consumo_combustible_gal: float

class RutaResponse(RutaBase):
    id: int
    class Config:
        from_attributes = True

class AeronaveResponse(BaseModel):
    id: int
    modelo: str
    matricula: str
    factor_velocidad: float
    factor_consumo: float
    class Config:
        from_attributes = True

class HistorialResponse(BaseModel):
    id: int
    fecha: datetime
    origen_iata: str
    destino_iata: str
    aeronave_matricula: str
    criterio: str
    distancia_total: float
    tiempo_total_min: int
    costo_total: float
    combustible_total: float
    escalas: Optional[int] = 0

    class Config:
        from_attributes = True