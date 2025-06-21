from app.service.avaliar import avaliar_dados_paciente
from fastapi import APIRouter, Query, HTTPException, Form, Body
from app.model.avaliacao_response import AvaliacaoResponse

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
        genero=genero,g
        igg=igg,
        igm=igm,
        area=area,
        areat=areat,
        casat=casat,
        avaliacao=resultado
    )
