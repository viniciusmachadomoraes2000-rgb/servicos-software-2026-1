import csv
import json
import os
import time
import unicodedata
import urllib.parse
import urllib.request


CAMINHO_POSTOS = "dados/postos.csv"
CAMINHO_CACHE = "dados/cache_geocodificacao.json"

USER_AGENT = (
    "SmartTrip-Projeto-Academico/1.0 "
    "(Projeto universitario)"
)


def normalizar_texto(texto):

    texto = (texto or "").strip().upper()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    return texto


MUNICIPIOS_ROTA = {
    "SAO BERNARDO DO CAMPO",
    "RIBEIRAO PIRES",
    "MOGI DAS CRUZES",
    "SAO JOSE DOS CAMPOS",
    "TAUBATE",
    "SAO LUIZ DO PARAITINGA",
    "NATIVIDADE DA SERRA",
    "UBATUBA"
}


def carregar_cache():

    if not os.path.exists(CAMINHO_CACHE):
        return {}

    with open(
        CAMINHO_CACHE,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def salvar_cache(cache):

    with open(
        CAMINHO_CACHE,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            cache,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def consultar_nominatim(endereco):

    parametros = urllib.parse.urlencode({
        "q": endereco,
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

    try:

        with urllib.request.urlopen(
            requisicao,
            timeout=20
        ) as resposta:

            dados = json.loads(
                resposta.read().decode("utf-8")
            )

    except Exception as erro:

        print(
            "Erro na consulta:",
            erro
        )

        return None

    if not dados:
        return None

    return {
        "latitude": float(dados[0]["lat"]),
        "longitude": float(dados[0]["lon"]),
        "endereco_encontrado": dados[0]["display_name"]
    }


def geocodificar_posto(posto):

    endereco = posto.get("ENDERECO", "")
    bairro = posto.get("BAIRRO", "")
    municipio = posto.get("MUNICIPIO", "")
    uf = posto.get("UF", "")
    cep = posto.get("CEP", "")

    tentativas = [

        # Tentativa mais completa
        (
            f"{endereco}, {bairro}, "
            f"{municipio} - {uf}, "
            f"{cep}, Brasil"
        ),

        # Sem bairro e CEP
        (
            f"{endereco}, "
            f"{municipio} - {uf}, Brasil"
        ),

        # Versão mais simples
        (
            f"{endereco}, "
            f"{municipio}, Brasil"
        )
    ]

    for numero, endereco_teste in enumerate(
        tentativas,
        start=1
    ):

        print(
            f"Tentativa {numero}:",
            endereco_teste
        )

        resultado = consultar_nominatim(
            endereco_teste
        )

        if resultado:

            resultado["consulta_utilizada"] = (
                endereco_teste
            )

            return resultado

        # Pausa entre consultas
        time.sleep(1.1)

    return None


postos_selecionados = {}


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

        municipio = normalizar_texto(
            posto.get("MUNICIPIO")
        )

        uf = normalizar_texto(
            posto.get("UF")
        )

        if (
            uf == "SP"
            and municipio in MUNICIPIOS_ROTA
            and municipio not in postos_selecionados
        ):

            postos_selecionados[municipio] = posto


cache = carregar_cache()


print("\nTESTE DE GEOCODIFICAÇÃO\n")


for municipio, posto in postos_selecionados.items():

    chave_cache = (
        f'{posto.get("RAZAOSOCIAL", "")}|'
        f'{posto.get("ENDERECO", "")}|'
        f'{posto.get("MUNICIPIO", "")}|'
        f'{posto.get("UF", "")}'
    )

    print("\n" + "=" * 70)

    print(
        "Posto:",
        posto.get("RAZAOSOCIAL")
    )

    print(
        "Bandeira:",
        posto.get("BANDEIRA")
    )

    print(
        "Município:",
        posto.get("MUNICIPIO")
    )

    # Só usamos o cache se houver
    # uma localização válida.
    if (
        chave_cache in cache
        and cache[chave_cache] is not None
    ):

        print("Usando coordenadas do cache.")

        resultado = cache[chave_cache]

    else:

        print(
            "Procurando coordenadas..."
        )

        resultado = geocodificar_posto(
            posto
        )

        if resultado:

            cache[chave_cache] = resultado

            salvar_cache(cache)

    if resultado:

        print("\nLOCALIZADO!")

        print(
            "Latitude:",
            resultado["latitude"]
        )

        print(
            "Longitude:",
            resultado["longitude"]
        )

        print(
            "Endereço encontrado:",
            resultado["endereco_encontrado"]
        )

    else:

        print(
            "\nNão foi possível localizar "
            "este posto."
        )


print("\nTESTE FINALIZADO.")