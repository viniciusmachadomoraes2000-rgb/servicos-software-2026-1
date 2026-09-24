# SmartTrip - Planejador de Viagens

Projeto desenvolvido para a disciplina de Serviços de Software.

O SmartTrip é uma aplicação web para planejamento de viagens. O sistema calcula informações da rota, estima os custos da viagem e utiliza um banco de dados de postos de combustíveis para identificar estabelecimentos próximos ao trajeto.

## Arquitetura

A aplicação é composta por dois containers Docker:

### Frontend

Desenvolvido utilizando:

- HTML
- CSS
- JavaScript
- Nginx

O frontend é responsável pela interface com o usuário e envia os dados da viagem para o backend através de uma API REST.

### Backend

Desenvolvido utilizando:

- Python
- Flask

O backend recebe as informações enviadas pelo frontend, realiza os cálculos da viagem, consulta serviços de rota e utiliza o banco de dados de postos para localizar estabelecimentos próximos ao trajeto.

## Comunicação entre os containers

O fluxo principal da aplicação é:

```text
Usuário
   ↓
Frontend
HTML + CSS + JavaScript
Nginx
   ↓
API REST
POST /api/planejar
   ↓
Backend
Python + Flask
   ↓
Processamento da viagem
   ↓
Resposta JSON
   ↓
Frontend
```

## Funcionalidades

O usuário pode informar:

- Origem
- Destino
- Tipo de veículo
- Consumo médio do veículo em km/L
- Preço do combustível
- Número de passageiros
- Valor dos pedágios
- Preferência da viagem
- Ida ou ida e volta

O sistema apresenta:

- Distância da viagem
- Distância total
- Tempo estimado
- Quantidade de combustível necessária
- Custo estimado de combustível
- Valor dos pedágios
- Custo total da viagem
- Custo por passageiro
- Postos de combustíveis próximos da rota

## Cálculo da viagem

A quantidade estimada de combustível é calculada através da fórmula:

```text
litros = distância total / consumo médio
```

O custo do combustível é calculado através de:

```text
custo combustível = litros necessários × preço do combustível
```

O custo total considera combustível e pedágios:

```text
custo total = custo combustível + pedágios
```

E o custo individual é:

```text
custo por passageiro = custo total / número de passageiros
```

## Rota

O sistema utiliza serviços de geolocalização e roteamento para transformar a origem e o destino informados pelo usuário em coordenadas geográficas e obter uma rota rodoviária entre os dois pontos.

A partir da rota são obtidos dados como:

- Distância
- Tempo estimado
- Coordenadas que representam o trajeto

## Banco de dados de postos

O projeto utiliza um arquivo CSV contendo dados cadastrais de postos de combustíveis.

Entre as informações disponíveis estão:

- Razão social
- Bandeira
- Endereço
- Bairro
- Município
- Estado
- CEP

O arquivo utilizado pelo projeto está localizado em:

```text
dados/postos.csv
```

## Identificação dos postos próximos da rota

Como o banco original não possui latitude e longitude, os endereços dos postos selecionados são geocodificados.

Após obter as coordenadas do posto, o sistema compara sua localização com os pontos que representam a rota.

Neste projeto, um posto é considerado próximo quando está localizado a até aproximadamente 3 km do trajeto.

As coordenadas já pesquisadas são armazenadas em cache:

```text
dados/cache_geocodificacao.json
```

Isso evita realizar novamente a mesma consulta de geocodificação.

## Estrutura do projeto

```text
projeto_final
│
├── backend
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── dados
│   ├── postos.csv
│   └── cache_geocodificacao.json
│
├── frontend
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   ├── script.js
│   └── style.css
│
├── compose.yaml
└── README.md
```

## Docker Compose

O arquivo `compose.yaml` é responsável por iniciar os dois serviços da aplicação:

```text
frontend
backend
```

O frontend fica disponível na porta:

```text
8080
```

O backend fica disponível na porta:

```text
5000
```

## API REST

A principal rota utilizada pelo projeto é:

```text
POST /api/planejar
```

Exemplo de requisição:

```json
{
    "origem": "São Bernardo do Campo, SP, Brasil",
    "destino": "Ubatuba, SP, Brasil",
    "tipo_veiculo": "carro",
    "consumo": 12,
    "preco": 6,
    "passageiros": 4,
    "pedagios": 0,
    "preferencia": "economia",
    "ida_volta": true
}
```

O backend processa os dados e devolve uma resposta JSON contendo as informações da viagem e os postos encontrados próximos ao trajeto.

## Como executar

É necessário possuir Docker e Docker Compose instalados.

Abra o terminal na pasta:

```text
projeto_final
```

Execute:

```bash
docker compose up --build
```

Depois abra no navegador:

```text
http://localhost:8080
```

## Objetivo acadêmico

O objetivo do projeto é demonstrar uma aplicação baseada em serviços de software, utilizando containers Docker independentes para frontend e backend e comunicação entre os componentes por meio de API REST.