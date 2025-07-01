from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
from fastapi_pagination import Page, Params, paginate
from app.core.database import Database, logger
from app.models.evento import EventoBase, EventoCreate, EventoUpdate, EventoResponse
from app.services.evento_service import EventoService

router = APIRouter()


@router.get("/", response_model=Page[EventoResponse])
async def listar_eventos(
        estado: Optional[str] = None,
        cidade: Optional[str] = None,
        nome_evento: Optional[str] = None,
        status: Optional[str] = None,  # "pendentes", "realizados" ou "todos"
        ordenar_por: str = "datas_realizacao",
        ordem: int = -1,
        params: Params = Depends(),
):
    """
    Lista eventos com filtros, ordenação e paginação.
    """
    try:
        # Construir filtro
        filtro = {}

        if estado:
            filtro["estado"] = estado

        if cidade:
            filtro["cidade"] = cidade

        if nome_evento:
            filtro["nome_evento"] = {"$regex": nome_evento, "$options": "i"}

        # Filtrar por status (pendentes ou realizados)
        if status:
            hoje = datetime.now()
            if status == "pendentes":
                filtro["datas_realizacao"] = {"$gte": hoje}
            elif status == "realizados":
                filtro["datas_realizacao"] = {"$lt": hoje}

        # Construir ordenação
        order = {ordenar_por: ordem}

        # Buscar eventos
        return await EventoService.listar_eventos(filtro, order, params)
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sem-paginacao", response_model=List[EventoResponse])
async def listar_eventos_sem_paginacao(
        limit: Optional[int] = Query(100, description="Limite de eventos a retornar")
):
    """
    Retorna uma lista de eventos sem paginação.
    Útil para obter dados para filtros ou seleções.
    """
    try:
        return await EventoService.listar_eventos_sem_paginacao(limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar eventos: {str(e)}"
        )


@router.get("/{id}", response_model=EventoResponse)
async def obter_evento(id: str):
    """
    Obtém um evento pelo ID.
    """
    try:
        evento = await EventoService.buscar_evento_por_id(id)

        if not evento:
            raise HTTPException(status_code=404, detail="Evento não encontrado")

        return evento
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao obter evento: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/com-edital/lista", response_model=List[EventoResponse])
async def listar_eventos_com_edital():
    """
    Lista eventos que possuem um edital disponível.
    """
    try:
        filtro = {
            "link_edital": {
                "$exists": True,
                "$ne": None,
                "$ne": "Não disponível"
            }
        }

        return await EventoService.listar_eventos_sem_paginacao(filtro=filtro)
    except Exception as e:
        logger.error(f"Erro ao listar eventos com edital: {e}")
        raise HTTPException(status_code=500, detail=str(e))