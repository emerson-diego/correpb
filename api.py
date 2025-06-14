from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination

from configs import convert_to_json
from operations import Operations

Operations.initialize()

api = FastAPI(
    title="Corre PB - Backend",
    description="Backend da Aplicação Corre PB",
)
add_pagination(api)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["https://correpbfrontend.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/")
async def read_root():
    return "O Backend do Corre PB está funcionando!"


@api.post("/eventos", response_model=Page)
async def eventos(
    nome_evento: str | None = None,
    cidade: str | None = None,
    estado: str | None = None,
    organizador: str | None = None,
    distancia: str | None = None,
    data_realizacao_inicio: datetime | None = None,
    data_realizacao_fim: datetime | None = None,
    order: dict | None = {"datas_realizacao": -1},
):
    eventos_pagina = Operations.eventos(
        nome_evento=nome_evento,
        cidade=cidade,
        estado=estado,
        organizador=organizador,
        distancia=distancia,
        data_realizacao_inicio=data_realizacao_inicio,
        data_realizacao_fim=data_realizacao_fim,
        order=order,
    )

    eventos_pagina.items = convert_to_json(eventos_pagina.items)

    return eventos_pagina

if __name__ == "__main__":
    uvicorn.run("api:api", host="localhost", port=8181)
