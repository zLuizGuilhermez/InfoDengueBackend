from pydantic import BaseModel

class AvaliacaoResponse(BaseModel):
    idade: int
    genero: str
    igg: float
    igm: float
    area: str
    areat: str
    casat: str
    avaliacao: str

