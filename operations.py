from datetime import date

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
        nome: str | None,
        cidade: str | None,
        distancia: int | None,
        organizacao: bool | None,
        data_inicio: date | None,
        data_fim: date | None,
        order: dict | None,
    ):
        filtros = {}

        if nome:
            nome = {
                "Nome do Evento": {
                    "$regex": f".*{nome}.*",
                    "$options": "i",
                }
            }
            filtros.update(nome)

        if cidade:
            cidade = {
                "Cidade": {
                    "$regex": f".*{cidade}.*",
                    "$options": "i",
                }
            }
            filtros.update(cidade)

        if distancia:
            distancia = {
                "Distância": {
                    "$regex": f".*{distancia}.*",
                    "$options": "i",
                }
            }
            filtros.update(distancia)

        if organizacao:
            organizacao = {
                "Organizador": {
                    "$regex": f".*{organizacao}.*",
                    "$options": "i",
                }
            }
            filtros.update(organizacao)

        if data_inicio:
            if not data_fim:
                data_fim = datetime.now()

            data_filtro = {
                "data": {
                    "$gte": data_inicio,
                    "$lte": data_fim,
                }
            }

            filtros.update(data_filtro)

        calls_page = cls._mongo_collection.find_all_objects_as_page(
            filtros,
            order,
        )

        return calls_page