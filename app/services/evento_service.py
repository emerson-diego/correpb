import errno
import logging
import re
from datetime import datetime
from fastapi_pagination.ext.motor import paginate
from fastapi_pagination import Params
from pymongo import UpdateOne, InsertOne
from bson import ObjectId
from typing import List, Dict, Any, Optional, Union
from app.core.database import Database
from app.utils.json_utils import convert_to_json
from app.models.evento import EventoCreate, EventoUpdate, EventoResponse
from app.utils.pagination_utils import paginate_with_objectid_conversion

logger = logging.getLogger(__name__)

class EventoService:
    """Serviço para operações relacionadas a eventos."""

    collection_name = "eventos"

    @classmethod
    async def listar_eventos(cls, filtro: Dict[str, Any], order: Dict[str, int], params: Params):
        """
        Lista eventos com filtros, ordenação e paginação.

        Args:
            filtro (dict): Filtros para a consulta
            order (dict): Ordenação para a consulta
            params (Params): Parâmetros de paginação

        Returns:
            Page: Página de eventos
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Usar a função personalizada
            return await paginate_with_objectid_conversion(
                collection,
                query_filter=filtro,
                sort=order,
                params=params,
                model_class=EventoResponse
            )
        except Exception as e:
            logger.error(f"Erro ao listar eventos: {e}")
            raise

    @classmethod
    async def listar_eventos_sem_paginacao(cls, limit: int = 100, filtro: Dict[str, Any] = None):
        """
        Lista eventos sem paginação.

        Args:
            limit (int): Limite de eventos a retornar
            filtro (dict, optional): Filtros para a consulta

        Returns:
            list: Lista de eventos
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Criar um cursor para a coleção de eventos
            cursor = collection.find(filtro or {})

            # Ordenar por data de realização (decrescente)
            cursor = cursor.sort("datas_realizacao", -1)

            # Aplicar limite
            cursor = cursor.limit(limit)

            # Converter cursor para lista
            eventos = await cursor.to_list(length=None)

            # Converter para JSON
            return convert_to_json(eventos)
        except Exception as e:
            logger.error(f"Erro ao listar eventos sem paginação: {e}")
            raise

    @classmethod
    async def obter_evento(cls, evento_id: str):
        """
        Obtém um evento pelo ID.

        Args:
            evento_id (str): ID do evento

        Returns:
            dict: Evento encontrado ou None
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Buscar evento pelo ID
            evento = await collection.find_one({"_id": ObjectId(evento_id)})

            # Converter para JSON
            return convert_to_json(evento)
        except Exception as e:
            logger.error(f"Erro ao obter evento {evento_id}: {e}")
            raise

    @classmethod
    async def criar_evento(cls, evento: EventoCreate):
        """
        Cria um novo evento.

        Args:
            evento (EventoCreate): Dados do evento a ser criado

        Returns:
            dict: Evento criado
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Converter modelo para dicionário
            evento_dict = evento.dict()

            # Adicionar timestamps
            now = datetime.now()
            evento_dict["importado_em"] = now
            evento_dict["atualizado_em"] = now
            evento_dict["origem"] = "api"

            # Inserir evento
            result = await collection.insert_one(evento_dict)

            # Buscar evento inserido
            novo_evento = await collection.find_one({"_id": result.inserted_id})

            # Converter para JSON
            return convert_to_json(novo_evento)
        except Exception as e:
            logger.error(f"Erro ao criar evento: {e}")
            raise

    @classmethod
    async def atualizar_evento(cls, evento_id: str, evento: EventoUpdate):
        """
        Atualiza um evento existente.

        Args:
            evento_id (str): ID do evento a ser atualizado
            evento (EventoUpdate): Dados do evento a serem atualizados

        Returns:
            dict: Evento atualizado ou None se não encontrado
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Converter modelo para dicionário, removendo campos None
            evento_dict = {k: v for k, v in evento.dict().items() if v is not None}

            # Adicionar timestamp de atualização
            evento_dict["atualizado_em"] = datetime.now()

            # Atualizar evento
            result = await collection.update_one(
                {"_id": ObjectId(evento_id)},
                {"$set": evento_dict}
            )

            if result.modified_count == 0:
                # Verificar se o evento existe
                evento_existe = await collection.find_one({"_id": ObjectId(evento_id)})
                if not evento_existe:
                    return None

            # Buscar evento atualizado
            evento_atualizado = await collection.find_one({"_id": ObjectId(evento_id)})

            # Converter para JSON
            return convert_to_json(evento_atualizado)
        except Exception as e:
            logger.error(f"Erro ao atualizar evento {evento_id}: {e}")
            raise

    @classmethod
    async def excluir_evento(cls, evento_id: str):
        """
        Exclui um evento.

        Args:
            evento_id (str): ID do evento a ser excluído

        Returns:
            bool: True se excluído com sucesso, False se não encontrado
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Excluir evento
            result = await collection.delete_one({"_id": ObjectId(evento_id)})

            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao excluir evento {evento_id}: {e}")
            raise

    @classmethod
    async def importar_eventos(cls, eventos: List[Dict[str, Any]]):
        """
        Importa múltiplos eventos (upsert).

        Args:
            eventos (List[Dict]): Lista de eventos a serem importados

        Returns:
            dict: Resultado da operação
        """
        try:
            if not eventos:
                return {"inserted": 0, "updated": 0, "total": 0}

            collection = await Database.get_collection(cls.collection_name)

            # Preparar operações em lote (bulk)
            operations = []
            for evento in eventos:
                # Adicionar timestamp de atualização
                evento["atualizado_em"] = datetime.now()

                # Usar nome e data como chave única
                filter_query = {
                    "nome": evento["nome"]
                }

                if "datas_realizacao" in evento and evento["datas_realizacao"]:
                    filter_query["datas_realizacao"] = evento["datas_realizacao"]

                # Operação upsert (inserir se não existir, atualizar se existir)
                operations.append(
                    UpdateOne(
                        filter_query,
                        {"$set": evento},
                        upsert=True
                    )
                )

            # Executar operações em lote
            if operations:
                result = await collection.bulk_write(operations)
                return {
                    "inserted": result.upserted_count,
                    "updated": result.modified_count,
                    "total": len(operations)
                }
            return {"inserted": 0, "updated": 0, "total": 0}
        except Exception as e:
            logger.error(f"Erro ao importar eventos: {e}")
            raise

    @classmethod
    async def obter_estatisticas(cls):
        """
        Obtém estatísticas sobre os eventos.

        Returns:
            dict: Estatísticas dos eventos
        """
        try:
            collection = await Database.get_collection(cls.collection_name)

            # Total de eventos
            total_eventos = await collection.count_documents({})

            # Eventos por estado
            pipeline_estados = [
                {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            estados_cursor = collection.aggregate(pipeline_estados)
            eventos_por_estado = await estados_cursor.to_list(length=None)

        except:
            return errno.EEXIST

    @classmethod
    async def buscar_evento_por_id(cls, id: str):
        """
        Busca um evento pelo ID.

        Args:
            id (str): ID do evento

        Returns:
            dict: Evento encontrado ou None
        """
        try:
            # Validar se o ID é um ObjectId válido
            if not ObjectId.is_valid(id):
                return None

            collection = await Database.get_collection(cls.collection_name)
            evento = await collection.find_one({"_id": ObjectId(id)})

            if evento:
                # Converter ObjectId para string
                evento["_id"] = str(evento["_id"])
                return evento

            return None
        except Exception as e:
            logger.error(f"Erro ao buscar evento por ID: {e}")
            raise