const botao = document.getElementById("botao-calcular");
const resultado = document.getElementById("resultado");

botao.addEventListener("click", async function () {

    const distancia = Number(document.getElementById("distancia").value);
    const consumo = Number(document.getElementById("consumo").value);
    const preco = Number(document.getElementById("preco").value);

    if (distancia <= 0 || consumo <= 0 || preco <= 0) {
        resultado.innerHTML = "Preencha todos os valores corretamente.";
        return;
    }

    const dados = {
        distancia: distancia,
        consumo: consumo,
        preco: preco
    };

    try {

        const resposta = await fetch("/api/calcular", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        const retorno = await resposta.json();

        resultado.innerHTML =
            "Combustível necessário: " +
            retorno.litros_necessarios +
            " litros <br>" +
            "Custo total: R$ " +
            retorno.custo_total.toFixed(2);

    } catch (erro) {

        resultado.innerHTML = "Erro ao conectar com o backend.";

    }

});