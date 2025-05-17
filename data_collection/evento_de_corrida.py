from datetime import datetime
from typing import List, Optional

from bson import ObjectId


class EventoDeCorrida:
    def __init__(
        self,
        nome_evento: str,
        data_realizacao: str,
        cidade: str,
        estado: str,
        organizador: str,
        site_coleta: str,
        data_coleta: datetime,
        distancias: List[str],
        url_inscricao: Optional[str] = None,
        url_imagem: Optional[str] = None,
        categoria: Optional[str] = None,
        _id: Optional[ObjectId] = None
    ):
        # Propriedades obrigatórias
        self._id = _id
        self.nome_evento = nome_evento
        self.data_realizacao = data_realizacao
        self.cidade = cidade
        self.estado = estado
        self.organizador = organizador
        self.site_coleta = site_coleta
        self.data_coleta = data_coleta
        self.distancias = distancias

        # Propriedades opcionais
        self.url_inscricao = url_inscricao
        self.url_imagem = url_imagem
        self.categoria = categoria

    def to_dict(self) -> dict:
        """Converte o objeto para um dicionário compatível com MongoDB"""
        documento = {
            'nome_evento': self.nome_evento,
            'data_realizacao': self.data_realizacao,
            'cidade': self.cidade,
            'estado': self.estado,
            'organizador': self.organizador,
            'site_coleta': self.site_coleta,
            'data_coleta': self.data_coleta,
            'distancias': self.distancias
        }

        # Adiciona campos opcionais apenas se não forem None
        if self.url_inscricao:
            documento['url_inscricao'] = self.url_inscricao
        if self.url_imagem:
            documento['url_imagem'] = self.url_imagem
        if self.categoria:
            documento['categoria'] = self.categoria

        return documento

    @classmethod
    def from_csv_row(cls, row: dict, fonte: str) -> 'EventoDeCorrida':
        """Cria uma instância de EventoDeCorrida a partir de uma linha do CSV"""
        # Cria a instância mantendo a data como string
        return cls(
            nome_evento=row['Nome do Evento'],
            data_realizacao=row['Data'],
            cidade=row['Cidade'],
            estado='PB',  # Estado fixo para este projeto
            organizador=row['Organizador'],
            site_coleta=fonte,
            data_coleta=datetime.now(),
            distancias=[row['Distância']] if row['Distância'] else [],
            url_inscricao=row.get('Link de Inscrição'),
            url_imagem=row.get('Link da Imagem'),
            categoria=row.get('Categoria')
        ) 