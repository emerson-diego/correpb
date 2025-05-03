import uvicorn
from fastapi import FastAPI
from fastapi_pagination import Page, add_pagination

from datetime import date

from configs import convert_to_json
from operations import Operations

Operations.initialize()

api = FastAPI(
    title="Corre PB - Backend",
    description="Backend da Aplicação Corre PB",
)
add_pagination(api)

@api.get("/")
async def read_root():
    return "O Backend do Corre PB está funcionando!"

@api.post("/eventos", response_model=Page)
async def eventos(
    nome: str | None = None,
    cidade: str | None = None,
    distancia: int | None = None,
    organizacao: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    order: dict | None = {"Data": -1},
):
    eventos_pagina = Operations.eventos(
        nome=nome,
        cidade=cidade,
        distancia=distancia,
        organizacao=organizacao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        order=order,
    )

    eventos_pagina.items = convert_to_json(eventos_pagina.items)

    return eventos_pagina

if __name__ == "__main__":
    uvicorn.run("api:api", host="localhost", port=8181)