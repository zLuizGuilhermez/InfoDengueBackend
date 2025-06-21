from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
import os

model = "gemma2:2b"

Settings.llm = Ollama(model = model)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

base_dir = os.path.dirname(os.path.abspath(__file__))
dados_dir = os.path.join(base_dir, '..', 'data', 'dados_dengue')
documentos = SimpleDirectoryReader(dados_dir).load_data()
index = VectorStoreIndex.from_documents(documentos)
query_engine = index.as_query_engine()

def avaliar_paciente(genero: str, idade: int, igg: float, igm: float, area: str, areat: str, casat: str) -> str:
    prompt = (
        f"""Você é um especialista médico em doenças infecciosas. Sua função é avaliar se um paciente possui sinais que indicam dengue, com base nos seguintes critérios médicos:
- Lembre-se de responder em Português-BR
- NS1 positivo indica alta probabilidade de dengue.
- IgM elevado (>1.0) indica infecção recente, compatível com dengue.
- IgG elevado isolado (>1.0) geralmente indica infecção passada, mas se acompanhado de IgM elevado, reforça dengue recente.
- Febre, área residencial com alta incidência de dengue e tipo de moradia (como alvenaria em áreas desenvolvidas) também são fatores relevantes.

Aqui estão os dados do paciente:

- G��nero: {genero}
- Idade: {idade}
- IgG: {igg}
- IgM: {igm}
- Área: {area}
- Tipo de Área: {areat}
- Tipo de casa: {casat}

        'Sim, é possível que você esteja com dengue, mas lembre-se de consultar um médico.' 
        ou
        'Não, é improvável que você esteja com dengue, mas lembre-se de consultar um médico.' 
        Escreva a frase completa.

Explique o motivo técnico da sua resposta, sem repetir e em português."""



    )

    resposta = query_engine.query(prompt)
    return resposta.response.strip()