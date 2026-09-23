import csv
import unicodedata


caminho_arquivo = "dados/postos.csv"


def normalizar_texto(texto):
    texto = texto.strip().upper()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    return texto


cidade_procurada = "SAO BERNARDO DO CAMPO"

postos_encontrados = []


with open(caminho_arquivo, "r", encoding="utf-8-sig") as arquivo:

    leitor = csv.DictReader(
        arquivo,
        delimiter=";"
    )

    for posto in leitor:

        municipio = normalizar_texto(
            posto["MUNICIPIO"]
        )

        uf = normalizar_texto(
            posto["UF"]
        )

        if municipio == cidade_procurada and uf == "SP":

            postos_encontrados.append(posto)


print(
    "Quantidade de postos encontrados:",
    len(postos_encontrados)
)


print("\nPRIMEIROS POSTOS DE SAO BERNARDO DO CAMPO:\n")


for posto in postos_encontrados[:10]:

    print("Razão Social:", posto["RAZAOSOCIAL"])
    print("Bandeira:", posto["BANDEIRA"])
    print("Endereço:", posto["ENDERECO"])
    print("Bairro:", posto["BAIRRO"])
    print("CEP:", posto["CEP"])

    print("-" * 60)