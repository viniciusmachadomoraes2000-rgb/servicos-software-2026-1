from flask import Flask, jsonify, request

import csv
import json
import math
import os
import time
import urllib.parse
import urllib.request


app = Flask(__name__)


CAMINHO_POSTOS = "dados/postos.csv"

CAMINHO_CACHE = (
    "dados/cache_geocodificacao.json"
)

USER_AGENT = (
    "SmartTrip-Projeto-Academico/1.0"
)


# ---------------------------------------------------------
# ROTA INICIAL
# ---------------------------------------------------------

@app.route("/")
def inicio():

    return jsonify({
        "mensagem":
            "SmartTrip Backend funcionando!"
    })


# ---------------------------------------------------------
# GEOCODIFICAÇÃO
# ---------------------------------------------------------

def geocodificar_local(local):

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
            resposta.read().decode(
                "utf-8"
            )
        )


    if not dados:

        raise Exception(
            f"Local não encontrado: {local}"
        )


    return {

        "nome":
            dados[0]["display_name"],

        "latitude":
            float(dados[0]["lat"]),

        "longitude":
            float(dados[0]["lon"])

    }


# ---------------------------------------------------------
# CALCULAR ROTA
# ---------------------------------------------------------

def calcular_rota(
    origem,
    destino
):

    coordenadas = (
        f'{origem["longitude"]},'
        f'{origem["latitude"]};'
        f'{destino["longitude"]},'
        f'{destino["latitude"]}'
    )


    url = (
        "https://router.project-osrm.org/"
        f"route/v1/driving/{coordenadas}"
        "?overview=full&geometries=geojson"
    )


    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )


    with urllib.request.urlopen(
        requisicao,
        timeout=30
    ) as resposta:

        dados = json.loads(
            resposta.read().decode(
                "utf-8"
            )
        )


    if dados.get("code") != "Ok":

        raise Exception(
            "Não foi possível calcular a rota."
        )


    rota = dados["routes"][0]


    return {

        "distancia_km":
            rota["distance"] / 1000,

        "duracao_horas":
            rota["duration"] / 3600,

        "pontos":
            rota["geometry"]["coordinates"]

    }


# ---------------------------------------------------------
# DISTÂNCIA HAVERSINE
# ---------------------------------------------------------

def distancia_haversine(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):

    raio_terra = 6371.0


    lat1 = math.radians(
        latitude1
    )

    lon1 = math.radians(
        longitude1
    )

    lat2 = math.radians(
        latitude2
    )

    lon2 = math.radians(
        longitude2
    )


    delta_lat = (
        lat2 - lat1
    )

    delta_lon = (
        lon2 - lon1
    )


    a = (
        math.sin(
            delta_lat / 2
        ) ** 2

        +

        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(
            delta_lon / 2
        ) ** 2
    )


    c = (
        2
        * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )


    return (
        raio_terra * c
    )


# ---------------------------------------------------------
# DISTÂNCIA DO POSTO ATÉ A ROTA
# ---------------------------------------------------------

def distancia_posto_rota(
    latitude_posto,
    longitude_posto,
    pontos_rota
):

    menor_distancia = None


    for (
        longitude_rota,
        latitude_rota
    ) in pontos_rota:

        distancia = distancia_haversine(

            latitude_posto,

            longitude_posto,

            latitude_rota,

            longitude_rota
        )


        if (
            menor_distancia is None
            or
            distancia < menor_distancia
        ):

            menor_distancia = distancia


    return menor_distancia


# ---------------------------------------------------------
# CARREGAR POSTOS
# ---------------------------------------------------------

def carregar_postos():

    postos = {}


    if not os.path.exists(
        CAMINHO_POSTOS
    ):

        return postos


    with open(
        CAMINHO_POSTOS,
        "r",
        encoding="utf-8-sig"
    ) as arquivo:

        leitor = csv.DictReader(
            arquivo,
            delimiter=";"
        )


        for posto in leitor:

            chave = (
                f'{posto.get("RAZAOSOCIAL", "")}|'
                f'{posto.get("ENDERECO", "")}|'
                f'{posto.get("MUNICIPIO", "")}|'
                f'{posto.get("UF", "")}'
            )


            postos[chave] = posto


    return postos


# ---------------------------------------------------------
# CARREGAR CACHE
# ---------------------------------------------------------

def carregar_cache():

    if not os.path.exists(
        CAMINHO_CACHE
    ):

        return {}


    with open(
        CAMINHO_CACHE,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(
            arquivo
        )


# ---------------------------------------------------------
# BUSCAR POSTOS PRÓXIMOS
# ---------------------------------------------------------

def buscar_postos_proximos(
    pontos_rota,
    limite_km=3
):

    cache = carregar_cache()

    postos_csv = carregar_postos()

    encontrados = []


    for (
        chave,
        coordenadas
    ) in cache.items():


        if not coordenadas:

            continue


        if (
            "latitude"
            not in coordenadas

            or

            "longitude"
            not in coordenadas
        ):

            continue


        distancia = distancia_posto_rota(

            coordenadas[
                "latitude"
            ],

            coordenadas[
                "longitude"
            ],

            pontos_rota
        )


        if distancia > limite_km:

            continue


        posto = postos_csv.get(
            chave,
            {}
        )


        encontrados.append({

            "razao_social":
                posto.get(
                    "RAZAOSOCIAL",
                    chave.split("|")[0]
                ),

            "bandeira":
                posto.get(
                    "BANDEIRA",
                    ""
                ),

            "endereco":
                posto.get(
                    "ENDERECO",
                    ""
                ),

            "bairro":
                posto.get(
                    "BAIRRO",
                    ""
                ),

            "municipio":
                posto.get(
                    "MUNICIPIO",
                    ""
                ),

            "uf":
                posto.get(
                    "UF",
                    ""
                ),

            "cep":
                posto.get(
                    "CEP",
                    ""
                ),

            "latitude":
                coordenadas[
                    "latitude"
                ],

            "longitude":
                coordenadas[
                    "longitude"
                ],

            "distancia_rota_km":
                round(
                    distancia,
                    2
                )

        })


    encontrados.sort(
        key=lambda posto:
            posto[
                "distancia_rota_km"
            ]
    )


    return encontrados


# ---------------------------------------------------------
# API PRINCIPAL
# ---------------------------------------------------------

@app.route(
    "/api/planejar",
    methods=["POST"]
)
def planejar():

    try:

        dados = request.get_json()


        if not dados:

            raise Exception(
                "Dados da viagem não foram enviados."
            )


        origem_texto = (
            dados["origem"]
        )

        destino_texto = (
            dados["destino"]
        )


        tipo_veiculo = dados.get(
            "tipo_veiculo",
            "carro"
        )


        consumo = float(
            dados["consumo"]
        )

        preco = float(
            dados["preco"]
        )


        passageiros = int(
            dados.get(
                "passageiros",
                1
            )
        )


        ida_volta = bool(
            dados.get(
                "ida_volta",
                False
            )
        )


        pedagios = float(
            dados.get(
                "pedagios",
                0
            )
            or 0
        )


        # -------------------------------------------------
        # VALIDAÇÃO
        # -------------------------------------------------

        if consumo <= 0:

            raise Exception(
                "O consumo deve ser maior que zero."
            )


        if preco <= 0:

            raise Exception(
                "O preço do combustível deve ser maior que zero."
            )


        if passageiros <= 0:

            raise Exception(
                "O número de passageiros deve ser maior que zero."
            )


        if pedagios < 0:

            raise Exception(
                "O valor dos pedágios não pode ser negativo."
            )


        # -------------------------------------------------
        # ORIGEM
        # -------------------------------------------------

        origem = geocodificar_local(
            origem_texto
        )


        time.sleep(1.1)


        # -------------------------------------------------
        # DESTINO
        # -------------------------------------------------

        destino = geocodificar_local(
            destino_texto
        )


        # -------------------------------------------------
        # ROTA
        # -------------------------------------------------

        rota = calcular_rota(
            origem,
            destino
        )


        distancia_ida = (
            rota["distancia_km"]
        )

        duracao_ida = (
            rota["duracao_horas"]
        )


        # -------------------------------------------------
        # IDA OU IDA E VOLTA
        # -------------------------------------------------

        if ida_volta:

            distancia_total = (
                distancia_ida * 2
            )

            duracao_total = (
                duracao_ida * 2
            )

        else:

            distancia_total = (
                distancia_ida
            )

            duracao_total = (
                duracao_ida
            )


        # -------------------------------------------------
        # CÁLCULOS
        # -------------------------------------------------

        litros = (
            distancia_total
            / consumo
        )


        custo_combustivel = (
            litros
            * preco
        )


        custo_total = (
            custo_combustivel
            + pedagios
        )


        custo_por_pessoa = (
            custo_total
            / passageiros
        )


        # -------------------------------------------------
        # POSTOS
        # -------------------------------------------------

        postos = buscar_postos_proximos(
            rota["pontos"],
            limite_km=3
        )


        # -------------------------------------------------
        # RESPOSTA
        # -------------------------------------------------

        return jsonify({

            "origem": {

                "nome":
                    origem["nome"],

                "latitude":
                    origem["latitude"],

                "longitude":
                    origem["longitude"]

            },


            "destino": {

                "nome":
                    destino["nome"],

                "latitude":
                    destino["latitude"],

                "longitude":
                    destino["longitude"]

            },


            "viagem": {

                "tipo_veiculo":
                    tipo_veiculo,

                "ida_volta":
                    ida_volta,

                "passageiros":
                    passageiros,

                "distancia_ida_km":
                    round(
                        distancia_ida,
                        1
                    ),

                "distancia_total_km":
                    round(
                        distancia_total,
                        1
                    ),

                "tempo_estimado_horas":
                    round(
                        duracao_total,
                        1
                    ),

                "litros_necessarios":
                    round(
                        litros,
                        2
                    ),

                "custo_combustivel":
                    round(
                        custo_combustivel,
                        2
                    ),

                "pedagios":
                    round(
                        pedagios,
                        2
                    ),

                "custo_total":
                    round(
                        custo_total,
                        2
                    ),

                "custo_por_pessoa":
                    round(
                        custo_por_pessoa,
                        2
                    )

            },


            "postos":
                postos,


            "quantidade_postos":
                len(postos)

        })


    except Exception as erro:

        return jsonify({

            "erro":
                str(erro)

        }), 400


# ---------------------------------------------------------
# INICIAR FLASK
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )