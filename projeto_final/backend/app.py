from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def inicio():
    return jsonify({
        "mesagem": "Backend funcionando!"
    })

@app.route("/api/calcular", methods=["POST"])
def calcular():
    dados = request.get_json()

    distancia = float(dados["distancia"])
    consumo = float(dados["consumo"])
    preco = float(dados["preco"])

    litros = distancia / consumo
    custo = litros * preco

    return jsonify({
        "litros_necessarios": round(litros, 2),
        "custo_total": round(custo, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)