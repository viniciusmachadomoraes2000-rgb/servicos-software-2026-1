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

    if dados["code"] != "Ok":
        raise Exception("Não foi possível calcular a rota.")

    rota = dados["routes"][0]

    return {
        "distancia_km": rota["distance"] / 1000,
        "duracao_horas": rota["duration"] / 3600,
        "geometria": rota["geometry"]
    }


print("Buscando origem...")

origem = geocodificar(
    "São Bernardo do Campo, SP, Brasil"
)

# Nominatim público limita o uso a 1 requisição por segundo.
time.sleep(1.1)

print("Buscando destino...")

destino = geocodificar(
    "Ubatuba, SP, Brasil"
)

print("Calculando rota...")

rota = calcular_rota(
    origem,
    destino
)


print("\nORIGEM")
print(origem["nome"])
print(
    origem["latitude"],
    origem["longitude"]
)


print("\nDESTINO")
print(destino["nome"])
print(
    destino["latitude"],
    destino["longitude"]
)


print("\nROTA")
print(
    "Distância:",
    round(rota["distancia_km"], 1),
    "km"
)

print(
    "Tempo estimado:",
    round(rota["duracao_horas"], 1),
    "horas"
)

print(
    "Quantidade de pontos da rota:",
    len(rota["geometria"]["coordinates"])
)