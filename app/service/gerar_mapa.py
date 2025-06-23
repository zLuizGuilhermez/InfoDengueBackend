import folium
from app.data.upas_df import UPAS_DF
from app.service.encontrar_upas import transformar_endereco_para_cord, encontrar_upa_mais_proxima

def gerar_mapa_upas_e_endereco(endereco=None, lat=None, lon=None):
    """
    Gera um mapa interativo mostrando todas as UPAs do DF e o endereço da pessoa (opcional)

    Args:
        endereco (str, opcional): Endereço do usuário para geocodificar
        lat (float, opcional): Latitude do usuário se já conhecida
        lon (float, opcional): Longitude do usuário se já conhecida

    Returns:
        str: HTML do mapa interativo que pode ser incorporado em uma página web
    """
    # Se temos o endereço mas não as coordenadas, vamos obter as coordenadas
    if endereco and not (lat and lon):
        coordenadas = transformar_endereco_para_cord(endereco)
        if coordenadas:
            lat, lon = coordenadas
        else:
            # Se não conseguimos obter as coordenadas, criamos um mapa centralizado no DF
            lat, lon = -15.8, -47.9  # Centro aproximado do DF

    # Se não temos nem endereço nem coordenadas, centralizamos no DF
    if not (lat and lon):
        lat, lon = -15.8, -47.9  # Centro aproximado do DF

    # Criamos o mapa inicial centralizado na localização do usuário ou no centro do DF
    mapa = folium.Map(location=[lat, lon], zoom_start=12)

    # Adicionamos todas as UPAs ao mapa
    for upa in UPAS_DF:
        popup_text = f"""
            <b>{upa['nome']}</b><br>
            {upa['endereco']}
        """
        folium.Marker(
            location=[upa['lat'], upa['lon']],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='hospital-o', prefix='fa')
        ).add_to(mapa)

    # Se tivermos o endereço/coordenadas do usuário, adicionamos ao mapa
    if lat and lon:
        # Encontramos a UPA mais próxima
        upa_proxima = encontrar_upa_mais_proxima(lat, lon)

        # Adicionamos o marcador do usuário
        folium.Marker(
            location=[lat, lon],
            popup=f"Sua localização{f'<br>{endereco}' if endereco else ''}",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(mapa)

        # Traçamos uma linha da localização do usuário até a UPA mais próxima
        if upa_proxima:
            points = [(lat, lon), (upa_proxima['lat'], upa_proxima['lon'])]
            folium.PolyLine(
                points,
                color="red",
                weight=2.5,
                opacity=1,
                popup=f"Distância: {upa_proxima['distancia_km']} km"
            ).add_to(mapa)

            # Destacamos a UPA mais próxima
            folium.Marker(
                location=[upa_proxima['lat'], upa_proxima['lon']],
                popup=f"""
                    <b>{upa_proxima['nome']} (MAIS PRÓXIMA)</b><br>
                    {upa_proxima['endereco']}<br>
                    Distância: {upa_proxima['distancia_km']} km
                """,
                icon=folium.Icon(color='green', icon='plus', prefix='fa')
            ).add_to(mapa)

    # Salvamos o mapa em uma string HTML
    mapa_html = mapa._repr_html_()

    return mapa_html

def salvar_mapa_arquivo(endereco=None, lat=None, lon=None, caminho_saida="mapa_upas.html"):
    """
    Gera um mapa e salva em um arquivo HTML

    Args:
        endereco (str, opcional): Endereço do usuário
        lat (float, opcional): Latitude do usuário
        lon (float, opcional): Longitude do usuário
        caminho_saida (str): Caminho do arquivo HTML de saída

    Returns:
        str: Caminho do arquivo salvo
    """
    # Se temos o endereço mas não as coordenadas, vamos obter as coordenadas
    if endereco and not (lat and lon):
        coordenadas = transformar_endereco_para_cord(endereco)
        if coordenadas:
            lat, lon = coordenadas
        else:
            # Se não conseguimos obter as coordenadas, criamos um mapa centralizado no DF
            lat, lon = -15.8, -47.9  # Centro aproximado do DF

    # Se não temos nem endereço nem coordenadas, centralizamos no DF
    if not (lat and lon):
        lat, lon = -15.8, -47.9  # Centro aproximado do DF

    # Criamos o mapa inicial centralizado na localização do usuário ou no centro do DF
    mapa = folium.Map(location=[lat, lon], zoom_start=12)

    # Adicionamos todas as UPAs ao mapa
    for upa in UPAS_DF:
        popup_text = f"""
            <b>{upa['nome']}</b><br>
            {upa['endereco']}
        """
        folium.Marker(
            location=[upa['lat'], upa['lon']],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='hospital-o', prefix='fa')
        ).add_to(mapa)

    # Se tivermos o endereço/coordenadas do usuário, adicionamos ao mapa
    if lat and lon:
        # Encontramos a UPA mais próxima
        upa_proxima = encontrar_upa_mais_proxima(lat, lon)

        # Adicionamos o marcador do usuário
        folium.Marker(
            location=[lat, lon],
            popup=f"Sua localização{f'<br>{endereco}' if endereco else ''}",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(mapa)

        # Traçamos uma linha da localização do usuário até a UPA mais próxima
        if upa_proxima:
            points = [(lat, lon), (upa_proxima['lat'], upa_proxima['lon'])]
            folium.PolyLine(
                points,
                color="red",
                weight=2.5,
                opacity=1,
                popup=f"Distância: {upa_proxima['distancia_km']} km"
            ).add_to(mapa)

            # Destacamos a UPA mais próxima
            folium.Marker(
                location=[upa_proxima['lat'], upa_proxima['lon']],
                popup=f"""
                    <b>{upa_proxima['nome']} (MAIS PRÓXIMA)</b><br>
                    {upa_proxima['endereco']}<br>
                    Distância: {upa_proxima['distancia_km']} km
                """,
                icon=folium.Icon(color='green', icon='plus', prefix='fa')
            ).add_to(mapa)

    # Salvamos o mapa em um arquivo HTML
    mapa.save(caminho_saida)

    return caminho_saida
