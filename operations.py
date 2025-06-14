from datetime import datetime

from mongo_helper import MongoHelper


class Operations:

    _mongo_collection = None

    @classmethod
    def initialize(
        cls,
    ):
        cls._mongo_collection = MongoHelper()

    @classmethod
    def eventos(
        cls,
        nome_evento: str | None,
        cidade: str | None,
        estado: str | None,
        organizador: str | None,
        distancia: str | None,
        data_realizacao_inicio: datetime | None,
        data_realizacao_fim: datetime | None,
        order: dict | None,
    ):
        filtros = {}

        if nome_evento:
            nome_evento = {
                "nome_evento": {
                    "$regex": f".*{nome_evento}.*",
                    "$options": "i",
                }
            }
            filtros.update(nome_evento)

        if cidade:
            cidade = {
                "cidade": {
                    "$regex": f".*{cidade}.*",
                    "$options": "i",
                }
            }
            filtros.update(cidade)

        if estado:
            estado = {
                "estado": {
                    "$regex": f".*{estado}.*",
                    "$options": "i",
                }
            }
            filtros.update(estado)

        if organizador:
            organizador = {
                "organizador": {
                    "$regex": f".*{organizador}.*",
                    "$options": "i",
                }
            }
            filtros.update(organizador)

        if distancia:
            distancia = {
                "distancias": {
                    "$regex": f".*{distancia}.*",
                    "$options": "i",
                }
            }
            filtros.update(distancia)

        if data_realizacao_inicio:
            if not data_realizacao_fim:
                data_realizacao_fim = datetime.now()

            data_filtro = {
                "datas_realizacao": {
                    "$gte": data_realizacao_inicio,
                    "$lte": data_realizacao_fim,
                }
            }

            filtros.update(data_filtro)

        calls_page = cls._mongo_collection.find_all_objects_as_page(
            filtros,
            order,
        )

        return calls_page
