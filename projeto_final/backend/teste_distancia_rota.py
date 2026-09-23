import json
import math
import urllib.parse
import urllib.request


CAMINHO_CACHE = "dados/cache_geocodificacao.json"

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

    with urllib.request.urlopen(
        requisicao,
        timeout=20
    ) as resposta:

        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    if not dados:
        raise Exception(
            f"Local não encontrado: {local}"
        )

    return {
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

    with urllib.request.urlopen(
        url,
        timeout=30
    ) as resposta:

        dados = json.loads(
            resposta.read().decode("utf-8")
        )

    return dados["routes"][0]["geometry"]["coordinates"]


def distancia_haversine(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):

    raio_terra = 6371.0

    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)

    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return raio_terra * c


def distancia_posto_rota(
    latitude_posto,
    longitude_posto,
    pontos_rota
):

    menor_distancia = None

    for longitude_rota, latitude_rota in pontos_rota:

        distancia = distancia_haversine(
            latitude_posto,
            longitude_posto,
            latitude_rota,
            longitude_rota
        )

        if (
            menor_distancia is None
            or distancia < menor_distancia
        ):
            menor_distancia = distancia

    return menor_distancia


print("Localizando origem...")

origem = geocodificar(
    "São Bernardo do Campo, SP, Brasil"
)

print("Localizando destino...")

destino = geocodificar(
    "Ubatuba, SP, Brasil"
)

print("Calculando rota...")

pontos_rota = calcular_rota(
    origem,
    destino
)


print(
    "Pontos da rota:",
    len(pontos_rota)
)


with open(
    CAMINHO_CACHE,
    "r",
    encoding="utf-8"
) as arquivo:

    cache = json.load(arquivo)


print("\nPOSTOS GEOCODIFICADOS:\n")


quantidade_validos = 0


for chave, resultado in cache.items():

    # Ignora resultados que falharam.
    if not resultado:
        continue

    # O cache novo possui latitude e longitude.
    if (
        "latitude" not in resultado
        or "longitude" not in resultado
    ):
        continue

    quantidade_validos += 1

    latitude = resultado["latitude"]
    longitude = resultado["longitude"]

    distancia = distancia_posto_rota(
        latitude,
        longitude,
        pontos_rota
    )

    # As novas chaves do cache têm:
    # Razão Social|Endereço|Município|UF
    partes = chave.split("|")

    if len(partes) >= 4:

        nome = partes[0]
        endereco = partes[1]
        municipio = partes[2]
        uf = partes[3]

    else:

        nome = chave
        endereco = ""
        municipio = ""
        uf = ""

    print("=" * 60)

    print("Posto:", nome)

    if endereco:
        print("Endereço:", endereco)

    if municipio:
        print(
            "Município:",
            municipio,
            "-",
            uf
        )

    print(
        "Distância aproximada da rota:",
        round(distancia, 2),
        "km"
    )

    if distancia <= 3:

        print(
            "Status: ✅ POSTO PRÓXIMO DA ROTA"
        )

    else:

        print(
            "Status: ❌ FORA DO LIMITE DE 3 KM"
        )


print("\nRESUMO")

print(
    "Postos geocodificados analisados:",
    quantidade_validos
)