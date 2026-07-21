from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from optimizer import calcular_ruta_optima

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Optimizador de Rutas Aéreas Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def cargar_datos_por_defecto():
    db = next(get_db())
    if db.query(models.Aeropuerto).count() == 0:
        db.add_all([
            models.Aeropuerto(codigo_iata="UIO", nombre="Aeropuerto Internacional Mariscal Sucre", ciudad="Quito", pais="Ecuador", latitud=-0.129, longitud=-78.35, clima="DESPEJADO"),
            models.Aeropuerto(codigo_iata="GYE", nombre="Aeropuerto Internacional José Joaquín de Olmedo", ciudad="Guayaquil", pais="Ecuador", latitud=-2.16, longitud=-79.88, clima="DESPEJADO"),
            models.Aeropuerto(codigo_iata="MEC", nombre="Aeropuerto Internacional Eloy Alfaro", ciudad="Manta", pais="Ecuador", latitud=-0.95, longitud=-80.68, clima="DESPEJADO"),
            models.Aeropuerto(codigo_iata="GPS", nombre="Aeropuerto Ecológico Galápagos Seymour", ciudad="Baltra", pais="Ecuador", latitud=-0.45, longitud=-90.26, clima="DESPEJADO"),
            models.Aeropuerto(codigo_iata="PTY", nombre="Aeropuerto Internacional Tocumen", ciudad="Panamá", pais="Panamá", latitud=9.07, longitud=-79.38, clima="DESPEJADO"),
            models.Aeropuerto(codigo_iata="MIA", nombre="Aeropuerto Internacional de Miami", ciudad="Miami", pais="EE.UU.", latitud=25.79, longitud=-80.28, clima="DESPEJADO")
        ])
        db.commit()
    
    if db.query(models.Aeronave).count() == 0:
        db.add_all([
            models.Aeronave(modelo="Boeing 737-800", matricula="HC-CTR", factor_velocidad=1.0, factor_consumo=1.0),
            models.Aeronave(modelo="Airbus A320neo", matricula="HC-BVP", factor_velocidad=0.95, factor_consumo=0.85),
            models.Aeronave(modelo="Embraer 190", matricula="HC-CML", factor_velocidad=1.1, factor_consumo=1.2)
        ])
        db.commit()

@app.post("/aeropuertos/", response_model=schemas.AeropuertoResponse)
def registrar_aeropuerto(aeropuerto: schemas.AeropuertoCreate, db: Session = Depends(get_db)):
    db_aeropuerto = models.Aeropuerto(**aeropuerto.model_dump())
    db.add(db_aeropuerto)
    db.commit()
    db.refresh(db_aeropuerto)
    return db_aeropuerto

@app.get("/aeropuertos/", response_model=List[schemas.AeropuertoResponse])
def listar_aeropuertos(db: Session = Depends(get_db)):
    return db.query(models.Aeropuerto).all()

@app.post("/rutas/", response_model=schemas.RutaResponse)
def registrar_ruta(ruta: schemas.RutaBase, db: Session = Depends(get_db)):
    nueva_ruta = models.Ruta(**ruta.model_dump())
    db.add(nueva_ruta)
    db.commit()
    db.refresh(nueva_ruta)
    return nueva_ruta

@app.get("/rutas/", response_model=List[schemas.RutaResponse])
def listar_rutas(db: Session = Depends(get_db)):
    return db.query(models.Ruta).all()

@app.get("/aeronaves/", response_model=List[schemas.AeronaveResponse])
def listar_aeronaves(db: Session = Depends(get_db)):
    return db.query(models.Aeronave).all()

@app.get("/optimizar/")
def optimizar(origen_id: int, destino_id: int, criterio: str, aeronave_id: int, db: Session = Depends(get_db)):
    resultado = calcular_ruta_optima(db, origen_id, destino_id, criterio, aeronave_id)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado

@app.get("/historial/", response_model=List[schemas.HistorialResponse])
def obtener_historial(db: Session = Depends(get_db)):
    return db.query(models.HistorialSimulacion).order_by(models.HistorialSimulacion.fecha.desc()).all()

@app.delete("/limpiar-rutas/")
def limpiar_rutas(db: Session = Depends(get_db)):
    db.query(models.Ruta).delete()
    db.commit()
    return {"message": "Rutas eliminadas correctamente"}