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

        # Adiciona campos opcionais apenas se não forem None ou vazios
        if self.url_inscricao and self.url_inscricao.strip():
            documento['url_inscricao'] = self.url_inscricao
        if self.url_imagem and self.url_imagem.strip():
            documento['url_imagem'] = self.url_imagem
        if self.categoria and self.categoria.strip():
            documento['categoria'] = self.categoria

        return documento

    def __eq__(self, other):
        """Compara dois eventos, ignorando campos específicos"""
        if not isinstance(other, EventoDeCorrida):
            return False
            
        # Campos a serem comparados
        campos_comparacao = [
            'nome_evento', 'data_realizacao', 'cidade', 'estado',
            'organizador', 'site_coleta', 'distancias', 'url_inscricao',
            'url_imagem', 'categoria'
        ]
        
        # Compara cada campo
        for campo in campos_comparacao:
            valor_self = getattr(self, campo)
            valor_other = getattr(other, campo)
            
            # Trata listas de forma especial
            if isinstance(valor_self, list) and isinstance(valor_other, list):
                if sorted(valor_self) != sorted(valor_other):
                    return False
            elif valor_self != valor_other:
                return False
                
        return True

    @classmethod
    def from_csv_row(cls, row: dict, fonte: str) -> 'EventoDeCorrida':
        """Cria uma instância de EventoDeCorrida a partir de uma linha do CSV"""
        # Função auxiliar para tratar campos vazios
        def get_value(key: str) -> str:
            value = row.get(key, '')
            return value if value and value.strip() else ''

        return cls(
            nome_evento=get_value('Nome do Evento'),
            data_realizacao=get_value('Data'),
            cidade=get_value('Cidade'),
            estado='PB',  # Estado fixo para este projeto
            organizador=get_value('Organizador'),
            site_coleta=fonte,
            data_coleta=datetime.now(),
            distancias=get_value('Distância'),
            url_inscricao=get_value('Link de Inscrição'),
            url_imagem=get_value('Link da Imagem'),
            categoria=get_value('Categoria')
        ) 