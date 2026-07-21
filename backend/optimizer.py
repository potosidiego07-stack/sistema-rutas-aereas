import networkx as nx
from sqlalchemy.orm import Session
import models

def calcular_ruta_optima(db: Session, origen_id: int, destino_id: int, criterio: str, aeronave_id: int):
    rutas = db.query(models.Ruta).all()
    aeropuertos = {a.id: a for a in db.query(models.Aeropuerto).all()}
    aeronave = db.query(models.Aeronave).filter(models.Aeronave.id == aeronave_id).first()

    if not aeronave:
        return {"error": "Aeronave no encontrada"}

    if origen_id not in aeropuertos or destino_id not in aeropuertos:
        return {"error": "Aeropuerto de origen o destino no válido"}

    G = nx.DiGraph()

    for r in rutas:
        dist = r.distancia_km
        tiempo = r.tiempo_estimado_min * aeronave.factor_velocidad
        costo = r.costo_operativo
        combustible = r.consumo_combustible_gal * aeronave.factor_consumo

        if criterio == "distancia":
            peso = dist
        elif criterio == "tiempo":
            peso = tiempo
        elif criterio == "costo":
            peso = costo
        else:
            peso = (dist * 0.4) + (tiempo * 0.3) + (costo * 0.3)

        G.add_edge(
            r.origen_id, 
            r.destino_id, 
            weight=peso,
            distancia=dist,
            tiempo=tiempo,
            costo=costo,
            combustible=combustible
        )

    try:
        camino_ids = nx.dijkstra_path(G, origen_id, destino_id, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return {"error": "No existe una ruta conectada entre el origen y el destino seleccionados."}

    distancia_total = 0.0
    tiempo_total = 0.0
    costo_total = 0.0
    combustible_total = 0.0

    for i in range(len(camino_ids) - 1):
        u, v = camino_ids[i], camino_ids[i+1]
        edge_data = G[u][v]
        distancia_total += edge_data['distancia']
        tiempo_total += edge_data['tiempo']
        costo_total += edge_data['costo']
        combustible_total += edge_data['combustible']

    camino_iata = [aeropuertos[nid].codigo_iata for nid in camino_ids]
    num_escalas = max(0, len(camino_ids) - 2)

    # AQUÍ SE GUARDA CON EL VALOR ENTERO
    nuevo_historial = models.HistorialSimulacion(
        origen_iata=aeropuertos[origen_id].codigo_iata,
        destino_iata=aeropuertos[destino_id].codigo_iata,
        aeronave_matricula=aeronave.matricula,
        criterio=criterio.upper(),
        distancia_total=round(distancia_total, 2),
        tiempo_total_min=round(tiempo_total),
        costo_total=round(costo_total, 2),
        combustible_total=round(combustible_total, 2),
        escalas=num_escalas
    )
    db.add(nuevo_historial)
    db.commit()

    return {
        "camino_ids": camino_ids,
        "camino_iata": camino_iata,
        "distancia_total": round(distancia_total, 2),
        "tiempo_total_min": round(tiempo_total),
        "costo_total": round(costo_total, 2),
        "combustible_total": round(combustible_total, 2),
        "numero_escalas": num_escalas
    }