from fastapi_pagination import Page, Params
from fastapi_pagination.ext.motor import paginate as motor_paginate
from typing import Any, Dict, List, TypeVar
from bson import ObjectId

T = TypeVar('T')


async def paginate_with_objectid_conversion(
        collection,
        query_filter: Dict[str, Any],
        sort: Dict[str, int],
        params: Params,
        model_class
):
    """
    Função personalizada para paginação que converte ObjectId para string
    antes de passar os dados para o modelo Pydantic.

    Args:
        collection: Coleção do MongoDB
        query_filter: Filtro para a consulta
        sort: Ordenação para a consulta
        params: Parâmetros de paginação
        model_class: Classe do modelo Pydantic para validação

    Returns:
        Page: Página de objetos do modelo
    """
    # Obter a contagem total de documentos que correspondem ao filtro
    total = await collection.count_documents(query_filter)

    # Calcular o número de documentos a pular
    skip = (params.page - 1) * params.size

    # Obter os documentos para a página atual
    cursor = collection.find(query_filter).sort(list(sort.items())).skip(skip).limit(params.size)

    # Converter para lista
    items_list = await cursor.to_list(length=None)

    # Converter ObjectId para string
    for item in items_list:
        if '_id' in item and isinstance(item['_id'], ObjectId):
            item['_id'] = str(item['_id'])

    # Criar objetos do modelo
    items = [model_class.model_validate(item) for item in items_list]

    # Criar a página
    return Page(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
    )