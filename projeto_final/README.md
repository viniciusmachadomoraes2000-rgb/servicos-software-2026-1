# Calculadora de Custo de Viagem

Projeto desenvolvido para a disciplina de Serviços de Software.

Os dois containers Docker são compostos por:

- Frontend: HTML, CSS e JavaScript servidos por Nginx.
- Backend: Python com Flask.

O frontend envia os dados para o backend por meio de uma API REST.

## Funcionalidade

O usuário informa:

- Distância da viagem em quilômetros;
- Consumo médio do veículo em km/l;
- Preço do combustível em R$/litro.

O backend calcula:

- Quantidade de combustível necessária;
- Custo total estimado da viagem.

## Tecnologias utilizadas

- Docker
- Docker Compose
- Python
- Flask
- HTML
- CSS
- JavaScript
- Nginx

## Como executar o projeto

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
