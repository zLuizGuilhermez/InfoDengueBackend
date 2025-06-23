import folium
from app.data.upas_df import UPAS_DF
from app.service.encontrar_upas import transformar_endereco_para_cord, encontrar_upa_mais_proxima

def gerar_mapa_upas_e_endereco(endereco=None, lat=None, lon=None):
    if endereco and not (lat and lon):
        coordenadas = transformar_endereco_para_cord(endereco)
        if coordenadas:
            lat, lon = coordenadas
        else:
            lat, lon = -15.8, -47.9

    if not (lat and lon):
        lat, lon = -15.8, -47.9

    mapa = folium.Map(location=[lat, lon], zoom_start=12)

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

    if lat and lon:
        upa_proxima = encontrar_upa_mais_proxima(lat, lon)

        folium.Marker(
            location=[lat, lon],
            popup=f"Sua localização{f'<br>{endereco}' if endereco else ''}",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(mapa)

        if upa_proxima:
            points = [(lat, lon), (upa_proxima['lat'], upa_proxima['lon'])]
            folium.PolyLine(
                points,
                color="red",
                weight=2.5,
                opacity=1,
                popup=f"Distância: {upa_proxima['distancia_km']} km"
            ).add_to(mapa)

            folium.Marker(
                location=[upa_proxima['lat'], upa_proxima['lon']],
                popup=f"""
                    <b>{upa_proxima['nome']} (MAIS PRÓXIMA)</b><br>
                    {upa_proxima['endereco']}<br>
                    Distância: {upa_proxima['distancia_km']} km
                """,
                icon=folium.Icon(color='green', icon='plus', prefix='fa')
            ).add_to(mapa)

    mapa_html = mapa._repr_html_()

    return mapa_html

def salvar_mapa_arquivo(endereco=None, lat=None, lon=None, caminho_saida="mapa_upas.html"):
    if endereco and not (lat and lon):
        coordenadas = transformar_endereco_para_cord(endereco)
        if coordenadas:
            lat, lon = coordenadas
        else:
            lat, lon = -15.8, -47.9

    if not (lat and lon):
        lat, lon = -15.8, -47.9

    mapa = folium.Map(location=[lat, lon], zoom_start=12)

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

    if lat and lon:
        upa_proxima = encontrar_upa_mais_proxima(lat, lon)

        folium.Marker(
            location=[lat, lon],
            popup=f"Sua localização{f'<br>{endereco}' if endereco else ''}",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(mapa)

        if upa_proxima:
            points = [(lat, lon), (upa_proxima['lat'], upa_proxima['lon'])]
            folium.PolyLine(
                points,
                color="red",
                weight=2.5,
                opacity=1,
                popup=f"Distância: {upa_proxima['distancia_km']} km"
            ).add_to(mapa)

            folium.Marker(
                location=[upa_proxima['lat'], upa_proxima['lon']],
                popup=f"""
                    <b>{upa_proxima['nome']} (MAIS PRÓXIMA)</b><br>
                    {upa_proxima['endereco']}<br>
                    Distância: {upa_proxima['distancia_km']} km
                """,
                icon=folium.Icon(color='green', icon='plus', prefix='fa')
            ).add_to(mapa)

    mapa.save(caminho_saida)
    return caminho_saida
