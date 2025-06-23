from geopy.geocoders import Nominatim
import time
import re
import requests
import json

def extrair_cep(texto):
    padrao = r'\b\d{5}-?\d{3}\b'
    match = re.search(padrao, texto)
    if match:
        return match.group(0).replace("-", "")
    return None

def obter_coordenadas_por_cep(cep):
    try:
        url_viacep = f"https://viacep.com.br/ws/{cep}/json/"
        
        try:
            response = requests.get(url_viacep, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                
                if "erro" not in dados:
                    logradouro = dados.get("logradouro", "")
                    bairro = dados.get("bairro", "")
                    cidade = dados.get("localidade", "")
                    estado = dados.get("uf", "")
                    
                    quadra_pattern = re.search(r'(Q[A-Z]{1,3})\s*(\d+)', logradouro)

                    if quadra_pattern and estado == "DF":
                        sigla_quadra = quadra_pattern.group(1)
                        numero_quadra = quadra_pattern.group(2)
                        endereco_completo = f"{sigla_quadra} {numero_quadra}, {bairro}, {cidade}, {estado}, Brasil"
                        print(f"Detectado padrão de quadra: {endereco_completo}")
                    else:
                        endereco_completo = f"{logradouro}, {bairro}, {cidade}, {estado}, Brasil"

                    geolocator = Nominatim(user_agent="infodengue_app")
                    
                    location = geolocator.geocode(endereco_completo, timeout=10)
                    time.sleep(1)

                    if location:
                        print(f"Coordenadas encontradas para {endereco_completo}: {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)
                    
                    endereco_aproximado = f"{bairro}, {cidade}, {estado}, Brasil"
                    location = geolocator.geocode(endereco_aproximado, timeout=10)
                    time.sleep(1)
                    
                    if location:
                        print(f"Coordenadas aproximadas encontradas para o bairro {bairro}: {location.latitude}, {location.longitude}")
                        return (location.latitude, location.longitude)
                    
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

        print(f"Não foi possível encontrar coordenadas para o CEP {cep}")
        return None
        
    except Exception as e:
        print(f"Erro geral ao obter coordenadas para o CEP {cep}: {str(e)}")
        return None

def transformar_endereco_para_cord(entrada):
    cep = extrair_cep(entrada)
    
    if cep:
        print(f"CEP encontrado: {cep}")
        return obter_coordenadas_por_cep(cep)
    
    try:
        geolocator = Nominatim(user_agent="infodengue_app")
        
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
    from app.data.upas_df import UPAS_DF
    import math

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

    distancia_minima = float('inf')
    upa_mais_proxima = None

    for upa in UPAS_DF:
        dist = calcular_distancia(lat, lon, upa["lat"], upa["lon"])
        if dist < distancia_minima:
            distancia_minima = dist
            upa_mais_proxima = upa

    if upa_mais_proxima:
        upa_mais_proxima["distancia_km"] = round(distancia_minima, 2)

    return upa_mais_proxima
