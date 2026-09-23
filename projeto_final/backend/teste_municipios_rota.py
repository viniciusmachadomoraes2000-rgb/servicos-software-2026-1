import json
import time
import urllib.parse
import urllib.request


USER_AGENT = "SmartTrip-Projeto-Academico/1.0"


def geocodificar(local):

    parametros = urllib.parse.urlencode({
        "q": local,
        "format": "json",
        "limit": 1,
        "countrycodes": "br"
    })

    url = (
        "https://nominatim.openstreetmap.org/search?"
        + parametros
    )

    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urllib.request.urlopen(requisicao) as resposta:
        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    if not dados:
        raise Exception(
            f"Local não encontrado: {local}"
        )

    return {
        "nome": dados[0]["display_name"],
        "latitude": float(dados[0]["lat"]),
        "longitude": float(dados[0]["lon"])
    }


def calcular_rota(origem, destino):

    coordenadas = (
        f'{origem["longitude"]},{origem["latitude"]};'
        f'{destino["longitude"]},{destino["latitude"]}'
    )

    url = (
        "https://router.project-osrm.org/"
        f"route/v1/driving/{coordenadas}"
        "?overview=full&geometries=geojson"
    )

    with urllib.request.urlopen(url) as resposta:
        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    rota = dados["routes"][0]

    return rota["geometry"]["coordinates"]


def descobrir_municipio(longitude, latitude):

    parametros = urllib.parse.urlencode({
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "zoom": 10,
        "addressdetails": 1
    })

    url = (
        "https://nominatim.openstreetmap.org/reverse?"
        + parametros
    )

    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    with urllib.request.urlopen(requisicao) as resposta:
        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    endereco = dados.get("address", {})

    municipio = (
        endereco.get("city")
        or endereco.get("town")
        or endereco.get("municipality")
        or endereco.get("village")
    )

    estado = endereco.get("state")

    return municipio, estado


print("Localizando origem...")

origem = geocodificar(
    "São Bernardo do Campo, SP, Brasil"
)

time.sleep(1.1)

print("Localizando destino...")

destino = geocodificar(
    "Ubatuba, SP, Brasil"
)

print("Calculando rota...")

pontos_rota = calcular_rota(
    origem,
    destino
)


# Vamos pegar aproximadamente 8 pontos distribuídos pela rota
quantidade_amostras = 8

passo = max(
    1,
    len(pontos_rota) // quantidade_amostras
)

pontos_amostrados = pontos_rota[::passo]

# Garante que o último ponto também seja analisado
if pontos_rota[-1] not in pontos_amostrados:
    pontos_amostrados.append(
        pontos_rota[-1]
    )


municipios = []


print("\nMUNICÍPIOS ENCONTRADOS NA ROTA:\n")


for longitude, latitude in pontos_amostrados:

    municipio, estado = descobrir_municipio(
        longitude,
        latitude
    )

    if municipio:

        nome = f"{municipio} - {estado}"

        if nome not in municipios:
            municipios.append(nome)

            print(nome)

    
    time.sleep(1.1)


print("\nTOTAL DE MUNICÍPIOS IDENTIFICADOS:")
print(len(municipios))