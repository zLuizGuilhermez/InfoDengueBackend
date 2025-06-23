from geopy.geocoders import Nominatim
import time
import re
import requests
import json

def extrair_cep(texto):
    """
    Extrai um CEP de um texto

    Args:
        texto (str): Texto contendo um possível CEP

    Returns:
        str: CEP encontrado ou None
    """
    # Padrão para CEPs brasileiros: XXXXX-XXX ou XXXXXXXX
    padrao = r'\b\d{5}-?\d{3}\b'
    match = re.search(padrao, texto)
    if match:
        return match.group(0).replace("-", "")  # Remove hífen para padronização
    return None

def obter_coordenadas_por_cep(cep):
    """
    Obtém as coordenadas geográficas (latitude e longitude) a partir de um CEP
    usando a melhor abordagem para localização precisa de quadras

    Args:
        cep (str): CEP no formato XXXXXXXX (sem hífen)
        
    Returns:
        tuple: (latitude, longitude) ou None em caso de erro
    """
    try:
        # MÉTODO PRINCIPAL: Consultar ViaCEP para obter detalhes e formar um endereço completo e preciso
        url_viacep = f"https://viacep.com.br/ws/{cep}/json/"
        
        try:
            response = requests.get(url_viacep, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                
                if "erro" not in dados:
                    # Extrair os detalhes do endereço
                    logradouro = dados.get("logradouro", "")
                    bairro = dados.get("bairro", "")
                    cidade = dados.get("localidade", "")
                    estado = dados.get("uf", "")
                    
                    # Identificar padrão de quadra (comum em Brasília/DF)
                    quadra_pattern = re.search(r'(Q[A-Z]{1,3})\s*(\d+)', logradouro)

                    # Formar o endereço da maneira mais precisa possível
                    if quadra_pattern and estado == "DF":
                        # Para endereços de quadras em Brasília/DF (QNL, QNA, QI, etc)
                        sigla_quadra = quadra_pattern.group(1)
                        numero_quadra = quadra_pattern.group(2)
                        endereco_completo = f"{sigla_quadra} {numero_quadra}, {bairro}, {cidade}, {estado}, Brasil"
                        print(f"Detectado padrão de quadra: {endereco_completo}")
                    else:
                        endereco_completo = f"{logradouro}, {bairro}, {cidade}, {estado}, Brasil"

                    # Usar Nominatim para geocodificação
                    geolocator = Nominatim(user_agent="infodengue_app")
                    
                    # Primeira tentativa - endereço completo incluindo referências de quadra
                    location = geolocator.geocode(endereco_completo, timeout=10)
                    time.sleep(1)  # Pausa para respeitar limites de uso

                    if location:
                        print(f"Coordenadas encontradas para {endereco_completo}: {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)
                    
                    # Segunda tentativa - apenas com bairro, cidade e estado (menos preciso, mas abrangente)
                    endereco_aproximado = f"{bairro}, {cidade}, {estado}, Brasil"
                    location = geolocator.geocode(endereco_aproximado, timeout=10)
                    time.sleep(1)
                    
                    if location:
                        print(f"Coordenadas aproximadas encontradas para o bairro {bairro}: {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)
                    
                    # Terceira tentativa - apenas cidade e estado (último recurso)
                    location = geolocator.geocode(f"{cidade}, {estado}, Brasil", timeout=10)
                    time.sleep(1)
                    
                    if location:
                        print(f"Coordenadas da cidade encontradas: {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)

                    print(f"Não foi possível geocodificar o endereço para o CEP {cep}")
                else:
                    print(f"ViaCEP retornou erro para o CEP {cep}")
            else:
                print(f"ViaCEP retornou código de status {response.status_code}")

        except Exception as e:
            print(f"Erro ao processar o CEP {cep}: {str(e)}")

        # Se chegou aqui, todas as tentativas falharam
        print(f"Não foi possível encontrar coordenadas para o CEP {cep}")
        return None
        
    except Exception as e:
        print(f"Erro geral ao obter coordenadas para o CEP {cep}: {str(e)}")
        return None

def transformar_endereco_para_cord(entrada):
    """
    Transforma um endereço ou CEP em coordenadas geográficas (latitude e longitude)
    
    Args:
        entrada (str): CEP ou texto contendo CEP
        
    Returns:
        tuple: (latitude, longitude) ou None em caso de erro
    """
    # Extrair o CEP do texto de entrada
    cep = extrair_cep(entrada)
    
    # Se encontrou um CEP, usar para obter coordenadas
    if cep:
        print(f"CEP encontrado: {cep}")
        return obter_coordenadas_por_cep(cep)
    
    # Se não encontrou CEP, tentar geocodificar o texto como endereço
    try:
        geolocator = Nominatim(user_agent="infodengue_app")
        
        # Tentar geocodificar o endereço
        if "Brasil" not in entrada:
            entrada += ", Brasil"
            
        location = geolocator.geocode(entrada, timeout=10)
        time.sleep(1)
        
        if location:
            return (location.latitude, location.longitude)
            
        print(f"Não foi possível encontrar coordenadas para: {entrada}")
        return None
        
    except Exception as e:
        print(f"Erro ao geocodificar endereço: {str(e)}")
        return None

def encontrar_upa_mais_proxima(lat, lon):
    """
    Encontra a UPA mais próxima com base nas coordenadas fornecidas

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Informações da UPA mais próxima
    """
    from app.data.upas_df import UPAS_DF
    import math

    # Função para calcular a distância entre dois pontos usando a fórmula de Haversine
    def calcular_distancia(lat1, lon1, lat2, lon2):
        # Raio da Terra em km
        R = 6371.0

        # Converte graus para radianos
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Diferença de coordenadas
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distancia = R * c

        return distancia

    distancia_minima = float('inf')
    upa_mais_proxima = None

    # Verificar cada UPA e encontrar a mais próxima
    for upa in UPAS_DF:
        dist = calcular_distancia(lat, lon, upa["lat"], upa["lon"])
        if dist < distancia_minima:
            distancia_minima = dist
            upa_mais_proxima = upa

    if upa_mais_proxima:
        upa_mais_proxima["distancia_km"] = round(distancia_minima, 2)

    return upa_mais_proxima
