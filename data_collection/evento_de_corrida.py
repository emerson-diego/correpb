from datetime import datetime
from typing import List, Optional

from bson import ObjectId


class EventoDeCorrida:
    def __init__(
        self,
        nome_evento: str,
        datas_realizacao: List[datetime],
        cidade: str,
        estado: str,
        organizador: str,
        site_coleta: str,
        data_coleta: datetime,
        distancias: List[str],
        url_inscricao: Optional[str] = None,
        url_imagem: Optional[str] = None,
        categoria: Optional[str] = None,
        link_edital: Optional[str] = None,
        _id: Optional[ObjectId] = None
    ):
        # Propriedades obrigatórias
        self._id = _id
        self.nome_evento = nome_evento
        self.datas_realizacao = datas_realizacao
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
        self.link_edital = link_edital

    def to_dict(self) -> dict:
        """Converte o objeto para um dicionário compatível com MongoDB"""
        documento = {
            'nome_evento': self.nome_evento,
            'datas_realizacao': self.datas_realizacao,
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
        if self.link_edital is not None:
            documento['link_edital'] = self.link_edital

        return documento

    def __eq__(self, other):
        """Compara dois eventos, ignorando campos específicos"""
        if not isinstance(other, EventoDeCorrida):
            return False
            
        # Campos a serem comparados
        campos_comparacao = [
            'nome_evento', 'datas_realizacao', 'cidade', 'estado',
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

        # Converter datas para lista de datetime
        data_str = get_value('Data')
        datas_realizacao = []
        if data_str:
            try:
                meses = {
                    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
                    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                }
                # Exemplo: '02, 03 e 15 de Agosto de 2025'
                data_str = data_str.lower().replace('  ', ' ').replace(' e ', ', ')
                partes = data_str.split(' de ')
                if len(partes) == 3:
                    dias = [d.strip() for d in partes[0].split(',')]
                    mes = meses[partes[1].strip()]
                    ano = int(partes[2])
                    for dia in dias:
                        try:
                            datas_realizacao.append(datetime(ano, mes, int(dia)))
                        except Exception:
                            continue
            except Exception:
                pass
        # Se não conseguiu converter, salva string original
        if not datas_realizacao:
            datas_realizacao = []

        link_edital = get_value('link_edital') or get_value('Link do Edital')

        # Garante que distancias seja uma lista de strings
        distancias_val = get_value('Distância')
        if isinstance(distancias_val, str):
            distancias = [d.strip() for d in distancias_val.split(',') if d.strip()]
        elif isinstance(distancias_val, list):
            distancias = distancias_val
        else:
            distancias = []

        return cls(
            nome_evento=get_value('Nome do Evento'),
            datas_realizacao=datas_realizacao,
            cidade=get_value('Cidade'),
            estado='PB',  # Estado fixo para este projeto
            organizador=get_value('Organizador'),
            site_coleta=fonte,
            data_coleta=datetime.now(),
            distancias=distancias,
            url_inscricao=get_value('Link de Inscrição'),
            url_imagem=get_value('Link da Imagem'),
            categoria=get_value('Categoria'),
            link_edital=link_edital
        ) 