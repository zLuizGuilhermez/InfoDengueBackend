# Documentação do Fluxo de Geração de Mapas - InfoDengue

Este documento descreve o processo completo de geração de mapas no sistema InfoDengue, desde a entrada do CEP pelo usuário até a exibição do mapa com UPAs próximas.

## 1. Visão Geral do Processo

O fluxo de geração de mapas no sistema InfoDengue segue estas etapas principais:

1. O usuário informa seu CEP na interface
2. O sistema converte o CEP em coordenadas geográficas (latitude e longitude)
3. O sistema calcula as distâncias entre a localização do usuário e todas as UPAs cadastradas
4. O sistema seleciona as UPAs que estão dentro do raio definido (padrão: 20km)
5. O sistema gera um mapa interativo mostrando a localização do usuário e as UPAs próximas
6. O mapa é exibido na interface para o usuário

## 2. Componentes Principais

### 2.1. Frontend (Inicio.tsx)

O frontend coleta o CEP do usuário e faz duas chamadas principais:
- Chamada para `/upas-proximas` para obter a lista de UPAs próximas
- Chamada para `/mapa` para exibir o mapa interativo

### 2.2. API (routes.py)

A API possui endpoints que fornecem:
- Informações sobre UPAs próximas (`/upas-proximas`)
- Mapa interativo com a localização das UPAs (`/mapa`)

### 2.3. Serviços de Backend

- `encontrar_upas.py`: Contém a lógica de geocodificação e cálculo de distâncias
- `gerar_mapa.py`: Contém a lógica de geração de mapas interativos usando Folium

## 3. Fluxo Detalhado

### 3.1. Geocodificação do CEP

Quando o usuário informa um CEP, o sistema:

1. Recebe o CEP formatado do frontend
2. Utiliza o serviço `transformar_endereco_para_cord()` para converter o CEP em coordenadas
3. O serviço tenta obter as coordenadas usando várias abordagens:
   - Consulta à API do ViaCEP para obter detalhes do endereço
   - Identificação de padrões de quadra (especialmente para o DF)
   - Formação de endereço preciso para geocodificação
   - Uso do serviço Nominatim (OpenStreetMap) para obter coordenadas
   - Estratégia de fallback para casos onde a geocodificação precisa falha

### 3.2. Cálculo de UPAs Próximas

Com as coordenadas do usuário, o sistema:

1. Acessa a lista de todas as UPAs cadastradas (`UPAS_DF`)
2. Para cada UPA, calcula a distância usando a fórmula de Haversine:
   - Esta fórmula calcula a distância entre dois pontos em uma esfera (Terra)
   - Leva em consideração latitude e longitude dos pontos
   - Retorna a distância em quilômetros
3. Seleciona as UPAs que estão dentro do raio especificado (padrão: 20km)
4. Ordena as UPAs da mais próxima para a mais distante

### 3.3. Geração do Mapa

Para gerar o mapa interativo, o sistema:

1. Utiliza a biblioteca Folium (baseada em Leaflet.js)
2. Cria um mapa centrado na localização do usuário
3. Adiciona um marcador na posição do usuário
4. Para cada UPA próxima, adiciona um marcador com:
   - Nome da UPA
   - Endereço
   - Distância do usuário
   - Outras informações disponíveis (telefone, horário, etc.)
5. Configura o zoom do mapa para mostrar adequadamente o usuário e as UPAs
6. Converte o mapa em HTML interativo
7. Retorna o HTML para ser exibido no frontend

## 4. Diagramas

### 4.1. Fluxo de Dados
```
Usuário (CEP) -> Frontend -> API (/upas-proximas) -> Serviço de Geocodificação -> Cálculo de Distâncias -> Lista de UPAs próximas
       |
       v
    Frontend -> API (/mapa) -> Serviço de Geração de Mapa -> HTML do Mapa -> Exibição na Interface
```

### 4.2. Processamento do CEP
```
CEP -> ViaCEP API -> Detalhes do Endereço -> Formação de Endereço Completo -> Nominatim -> Coordenadas (lat, lon)
```

## 5. Considerações Sobre Precisão

A precisão da localização depende de diversos fatores:

- **Qualidade dos dados do CEP**: Os CEPs do DF, especialmente em áreas com quadras numeradas (QNL, QNN, etc.), podem necessitar de tratamento especial.
- **Serviço de geocodificação**: O Nominatim (OpenStreetMap) tem boa cobertura para o Brasil, mas pode ter limitações em alguns casos.
- **Distância calculada**: A fórmula de Haversine fornece uma boa aproximação da distância real, mas não considera rotas de estradas.

## 6. Possíveis Melhorias

- Implementar cache de geocodificação para CEPs já consultados
- Adicionar integração com serviços adicionais como Google Maps API para casos onde o Nominatim falha
- Incluir informações de rotas entre o usuário e as UPAs
- Adicionar filtros para busca de UPAs com base em critérios adicionais (atendimento 24h, especialidades, etc.)
