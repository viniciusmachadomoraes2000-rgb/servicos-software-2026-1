import csv
import unicodedata


CAMINHO_ARQUIVO = "dados/postos.csv"


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


municipios_rota = {
    "SAO BERNARDO DO CAMPO": "São Bernardo do Campo",
    "RIBEIRAO PIRES": "Ribeirão Pires",
    "MOGI DAS CRUZES": "Mogi das Cruzes",
    "SAO JOSE DOS CAMPOS": "São José dos Campos",
    "TAUBATE": "Taubaté",
    "SAO LUIZ DO PARAITINGA": "São Luiz do Paraitinga",
    "NATIVIDADE DA SERRA": "Natividade da Serra",
    "UBATUBA": "Ubatuba"
}


contagem = {
    municipio: 0
    for municipio in municipios_rota
}


exemplos = {
    municipio: []
    for municipio in municipios_rota
}


with open(
    CAMINHO_ARQUIVO,
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
            and municipio in municipios_rota
        ):

            contagem[municipio] += 1

            # Guardamos somente 3 exemplos
            # para não lotar o terminal.
            if len(exemplos[municipio]) < 3:
                exemplos[municipio].append(posto)


total = sum(contagem.values())


print("\nPOSTOS ENCONTRADOS NOS MUNICÍPIOS DA ROTA:\n")


for municipio, nome_exibicao in municipios_rota.items():

    print(
        nome_exibicao,
        ":",
        contagem[municipio],
        "postos"
    )


print("\nTOTAL DE POSTOS CANDIDATOS:")
print(total)


print("\nEXEMPLOS DE POSTOS:\n")


for municipio, nome_exibicao in municipios_rota.items():

    print("\n", nome_exibicao.upper())

    if not exemplos[municipio]:
        print("Nenhum posto encontrado.")
        continue

    for posto in exemplos[municipio]:

        print(
            "\nRazão Social:",
            posto.get("RAZAOSOCIAL")
        )

        print(
            "Bandeira:",
            posto.get("BANDEIRA")
        )

        print(
            "Endereço:",
            posto.get("ENDERECO")
        )

        print(
            "Bairro:",
            posto.get("BAIRRO")
        )

        print(
            "CEP:",
            posto.get("CEP")
        )

        print("-" * 50)