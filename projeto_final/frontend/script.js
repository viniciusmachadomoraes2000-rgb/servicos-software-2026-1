const botaoPlanejar = document.getElementById("botao-planejar");
const resultado = document.getElementById("resultado");
const resumoViagem = document.getElementById("resumo-viagem");
const listaPostos = document.getElementById("lista-postos");
const mensagemCarregando = document.getElementById("mensagem-carregando");


// =========================================================
// LIMPA OS CAMPOS AO ABRIR A PÁGINA
// =========================================================

window.addEventListener("DOMContentLoaded", function () {

    document.getElementById("origem").value = "";
    document.getElementById("destino").value = "";
    document.getElementById("tipo-veiculo").value = "";
    document.getElementById("consumo").value = "";
    document.getElementById("preco").value = "";
    document.getElementById("passageiros").value = "";
    document.getElementById("pedagios").value = "";
    document.getElementById("ida-volta").checked = false;

});


// =========================================================
// BOTÃO PLANEJAR VIAGEM
// =========================================================

botaoPlanejar.addEventListener("click", async function () {

    const origem =
        document.getElementById("origem").value.trim();

    const destino =
        document.getElementById("destino").value.trim();

    const tipoVeiculo =
        document.getElementById("tipo-veiculo").value;

    const consumo =
        Number(document.getElementById("consumo").value);

    const preco =
        Number(document.getElementById("preco").value);

    const passageiros =
        Number(document.getElementById("passageiros").value);

    const pedagios =
        Number(document.getElementById("pedagios").value || 0);

    const idaVolta =
        document.getElementById("ida-volta").checked;


    // =====================================================
    // VALIDAÇÃO
    // =====================================================

    if (
        origem === "" ||
        destino === "" ||
        tipoVeiculo === "" ||
        consumo <= 0 ||
        preco <= 0 ||
        passageiros <= 0
    ) {

        alert(
            "Preencha todos os campos obrigatórios antes de planejar a viagem."
        );

        return;
    }


    // =====================================================
    // DADOS ENVIADOS PARA O BACKEND
    // =====================================================

    const dados = {

        origem: origem,
        destino: destino,
        tipo_veiculo: tipoVeiculo,
        consumo: consumo,
        preco: preco,
        passageiros: passageiros,
        pedagios: pedagios,
        ida_volta: idaVolta

    };


    // =====================================================
    // CARREGAMENTO
    // =====================================================

    resultado.classList.add("oculto");

    mensagemCarregando.classList.remove("oculto");

    botaoPlanejar.disabled = true;


    // =====================================================
    // CHAMADA DA API
    // =====================================================

    try {

        const resposta = await fetch(
            "/api/planejar",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(dados)
            }
        );


        const retorno = await resposta.json();


        if (!resposta.ok) {

            throw new Error(
                retorno.erro ||
                "Não foi possível planejar a viagem."
            );

        }


        mostrarResumo(retorno);

        mostrarPostos(retorno.postos);

        resultado.classList.remove("oculto");


    } catch (erro) {

        alert(
            "Erro ao planejar a viagem:\n" +
            erro.message
        );


    } finally {

        mensagemCarregando.classList.add("oculto");

        botaoPlanejar.disabled = false;

    }

});


// =========================================================
// FORMATA VALOR EM REAL
// =========================================================

function formatarDinheiro(valor) {

    return Number(valor).toLocaleString(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL"
        }
    );

}


// =========================================================
// FORMATA TIPO DO VEÍCULO
// =========================================================

function formatarTipoVeiculo(tipo) {

    if (tipo === "carro") {
        return "Carro";
    }

    if (tipo === "moto") {
        return "Moto";
    }

    if (tipo === "utilitario") {
        return "Utilitário";
    }

    return tipo;

}


// =========================================================
// MOSTRA RESUMO DA VIAGEM
// =========================================================

function mostrarResumo(retorno) {

    const viagem = retorno.viagem;


    resumoViagem.innerHTML = `

        <div class="card-resumo">

            <span class="titulo-card">
                Origem
            </span>

            <strong>
                ${retorno.origem.nome}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Destino
            </span>

            <strong>
                ${retorno.destino.nome}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Tipo de veículo
            </span>

            <strong>
                ${formatarTipoVeiculo(viagem.tipo_veiculo)}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Tipo de viagem
            </span>

            <strong>
                ${
                    viagem.ida_volta
                        ? "Ida e volta"
                        : "Somente ida"
                }
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Distância de ida
            </span>

            <strong>
                ${viagem.distancia_ida_km} km
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Distância total
            </span>

            <strong>
                ${viagem.distancia_total_km} km
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Tempo estimado
            </span>

            <strong>
                ${viagem.tempo_estimado_horas} horas
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Combustível necessário
            </span>

            <strong>
                ${viagem.litros_necessarios} litros
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Custo de combustível
            </span>

            <strong>
                ${formatarDinheiro(viagem.custo_combustivel)}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Pedágios
            </span>

            <strong>
                ${formatarDinheiro(viagem.pedagios)}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Custo total
            </span>

            <strong>
                ${formatarDinheiro(viagem.custo_total)}
            </strong>

        </div>


        <div class="card-resumo">

            <span class="titulo-card">
                Custo por passageiro
            </span>

            <strong>
                ${formatarDinheiro(viagem.custo_por_pessoa)}
            </strong>

        </div>

    `;

}


// =========================================================
// MOSTRA POSTOS PRÓXIMOS DA ROTA
// =========================================================

function mostrarPostos(postos) {

    listaPostos.innerHTML = "";


    if (!postos || postos.length === 0) {

        listaPostos.innerHTML = `

            <div class="posto-card">

                <strong>
                    Nenhum posto encontrado a até 3 km da rota.
                </strong>

            </div>

        `;

        return;

    }


    postos.forEach(function (posto, indice) {

        const card =
            document.createElement("div");

        card.className =
            "posto-card";


        card.innerHTML = `

            <h3>
                ⛽ ${indice + 1}. ${posto.razao_social}
            </h3>


            <p>
                <strong>Bandeira:</strong>
                ${posto.bandeira || "Não informada"}
            </p>


            <p>
                <strong>Endereço:</strong>
                ${posto.endereco || "Não informado"}
            </p>


            <p>
                <strong>Bairro:</strong>
                ${posto.bairro || "Não informado"}
            </p>


            <p>
                <strong>Município:</strong>
                ${posto.municipio || "Não informado"}
                ${posto.uf ? " - " + posto.uf : ""}
            </p>


            <p>
                <strong>CEP:</strong>
                ${posto.cep || "Não informado"}
            </p>


            <p>
                <strong>Distância da rota:</strong>
                ${posto.distancia_rota_km} km
            </p>

        `;


        listaPostos.appendChild(card);

    });

}