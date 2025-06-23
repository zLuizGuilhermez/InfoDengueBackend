from app.service.avaliar import avaliar_dados_paciente
from app.service.gerar_mapa import gerar_mapa_upas_e_endereco, salvar_mapa_arquivo
from app.service.encontrar_upas import transformar_endereco_para_cord, encontrar_upa_mais_proxima
from fastapi import APIRouter, Query, HTTPException, Form, Body, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.model.avaliacao_response import AvaliacaoResponse
from app.data.upas_df import UPAS_DF
import os
import math

router = APIRouter()

@router.get("/avaliar", response_model=AvaliacaoResponse)
def avaliar(
    genero: str = Query(...),
    idade: int = Query(...),
    igg: float = Query(...),
    igm: float = Query(...),
    area: str = Query(...),
    areat: str = Query(...),
    casat: str = Query(...),
):
    resultado = avaliar_dados_paciente(idade, genero,igg, igm, area, areat, casat)
    return AvaliacaoResponse(
        idade=idade,
        genero=genero,
        igg=igg,
        igm=igm,
        area=area,
        areat=areat,
        casat=casat,
        avaliacao=resultado
    )

@router.get("/mapa", response_class=HTMLResponse)
def obter_mapa_upas(
    endereco: str = Query(None, description="Endereço completo para localizar no mapa"),
    lat: float = Query(None, description="Latitude (se já conhecida)"),
    lon: float = Query(None, description="Longitude (se já conhecida)"),
):
    try:
        mapa_html = gerar_mapa_upas_e_endereco(endereco, lat, lon)
        return HTMLResponse(content=mapa_html, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mapa: {str(e)}")

@router.get("/mapa/arquivo")
def salvar_mapa_upas(
    endereco: str = Query(None, description="Endereço completo para localizar no mapa"),
    lat: float = Query(None, description="Latitude (se já conhecida)"),
    lon: float = Query(None, description="Longitude (se já conhecida)"),
):
    try:
        arquivo_mapa = salvar_mapa_arquivo(endereco, lat, lon, "mapa_upas_temp.html")
        return FileResponse(
            path=arquivo_mapa,
            filename="mapa_upas.html",
            media_type="text/html"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar arquivo do mapa: {str(e)}")

@router.get("/upas/proxima")
def encontrar_proxima(
    endereco: str = Query(None, description="Endereço completo"),
    lat: float = Query(None, description="Latitude"),
    lon: float = Query(None, description="Longitude"),
):
    if endereco and not (lat is not None and lon is not None):
        coordenadas = transformar_endereco_para_cord(endereco)
        if not coordenadas:
            raise HTTPException(status_code=404, detail="Não foi possível geocodificar o endereço fornecido")
        lat, lon = coordenadas

    if not (lat is not None and lon is not None):
        raise HTTPException(status_code=400, detail="É necessário fornecer um endereço ou coordenadas (latitude/longitude)")

    upa_proxima = encontrar_upa_mais_proxima(lat, lon)
    if not upa_proxima:
        raise HTTPException(status_code=404, detail="Não foi possível encontrar uma UPA próxima")

    return upa_proxima

@router.get("/upas-proximas")
def upas_proximas(
    endereco: str = Query(..., description="Endereço completo"),
    raio: float = Query(10.0, description="Raio de busca em km")
):
    coordenadas = transformar_endereco_para_cord(endereco)
    if not coordenadas:
        raise HTTPException(status_code=404, detail="Não foi possível geocodificar o endereço fornecido")

    lat, lon = coordenadas

    def calcular_distancia(lat1, lon1, lat2, lon2):
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distancia = R * c

        return distancia

    upas_no_raio = []

    for upa in UPAS_DF:
        dist = calcular_distancia(lat, lon, upa["lat"], upa["lon"])
        if dist <= raio:
            upa_com_distancia = dict(upa)
            upa_com_distancia["distancia"] = round(dist, 2)
            upas_no_raio.append(upa_com_distancia)

    upas_no_raio.sort(key=lambda x: x["distancia"])

    return upas_no_raio
