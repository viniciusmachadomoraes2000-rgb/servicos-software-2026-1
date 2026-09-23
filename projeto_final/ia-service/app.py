from flask import Flask, jsonify, request
from transformers import pipeline


app = Flask(__name__)


print("Carregando modelo de IA...")

gerador = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
    device=-1
)

print("Modelo de IA carregado!")


@app.route("/")
def inicio():

    return jsonify({
        "mensagem":
            "SmartTrip IA Service funcionando com modelo de IA!"
    })


@app.route(
    "/recomendar",
    methods=["POST"]
)
def recomendar():

    try:

        dados = request.get_json()


        origem = dados.get(
            "origem",
            "não informada"
        )

        destino = dados.get(
            "destino",
            "não informado"
        )

        preferencia = dados.get(
            "preferencia",
            "economia"
        )

        tipo_veiculo = dados.get(
            "tipo_veiculo",
            "carro"
        )

        passageiros = dados.get(
            "passageiros",
            1
        )

        distancia = dados.get(
            "distancia_total_km",
            0
        )

        tempo = dados.get(
            "tempo_estimado_horas",
            0
        )

        litros = dados.get(
            "litros_necessarios",
            0
        )

        custo_total = dados.get(
            "custo_total",
            0
        )

        custo_pessoa = dados.get(
            "custo_por_pessoa",
            0
        )

        quantidade_postos = dados.get(
            "quantidade_postos",
            0
        )

        postos = dados.get(
            "postos",
            []
        )


        nomes_postos = []

        for posto in postos:

            nome = posto.get(
                "razao_social",
                ""
            )

            municipio = posto.get(
                "municipio",
                ""
            )

            distancia_rota = posto.get(
                "distancia_rota_km",
                ""
            )

            if nome:

                nomes_postos.append(
                    f"{nome}, em {municipio}, "
                    f"a {distancia_rota} km da rota"
                )


        if nomes_postos:

            texto_postos = "; ".join(
                nomes_postos
            )

        else:

            texto_postos = (
                "Nenhum posto próximo foi encontrado."
            )


        prompt = f"""
Você é um assistente de planejamento de viagens.

Gere uma recomendação curta em português para esta viagem.

Origem: {origem}
Destino: {destino}
Tipo de veículo: {tipo_veiculo}
Preferência do usuário: {preferencia}
Número de passageiros: {passageiros}
Distância total: {distancia} km
Tempo estimado: {tempo} horas
Combustível necessário: {litros} litros
Custo total: R$ {custo_total}
Custo por passageiro: R$ {custo_pessoa}
Quantidade de postos encontrados: {quantidade_postos}
Postos próximos: {texto_postos}

A recomendação deve:
- mencionar o custo da viagem;
- mencionar o custo por passageiro;
- considerar a preferência do usuário;
- comentar sobre os postos encontrados;
- dar uma dica útil de viagem;
- não inventar valores diferentes dos fornecidos.

Responda em português, em um único parágrafo.
"""


        resultado = gerador(
            prompt,
            max_new_tokens=180,
            do_sample=False
        )


        recomendacao = resultado[0][
            "generated_text"
        ]


        return jsonify({
            "recomendacao":
                recomendacao
        })


    except Exception as erro:

        return jsonify({
            "erro": str(erro)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=6000
    )