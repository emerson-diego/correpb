from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Evento(BaseModel):
    """Modelo para eventos."""
    id: PyObjectId = Field(alias="_id")
    site_coleta: str
    data_coleta: datetime
    importado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    origem: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class EventoBase(BaseModel):
    """Modelo base para eventos."""
    nome_evento: str  # Usando nome_evento para corresponder ao banco
    datas_realizacao: List[datetime]
    cidade: str
    estado: str
    organizador: str
    distancias: str  # Usando string para corresponder ao banco
    url_inscricao: str
    url_imagem: Optional[str] = None
    categorias_premiadas: Optional[str] = None

class EventoCreate(EventoBase):
    """Modelo para criação de eventos."""
    site_coleta: str
    data_coleta: datetime = Field(default_factory=datetime.now)

class EventoUpdate(BaseModel):
    """Modelo para atualização de eventos."""
    nome_evento: Optional[str] = None
    datas_realizacao: Optional[List[datetime]] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    organizador: Optional[str] = None
    distancias: Optional[str] = None
    url_inscricao: Optional[str] = None
    url_imagem: Optional[str] = None
    site_coleta: Optional[str] = None
    data_coleta: Optional[datetime] = None
    categorias_premiadas: Optional[str] = None

class EventoResponse(EventoBase):
    """Modelo para resposta de eventos."""
    id: str = Field(alias="_id")
    site_coleta: str
    data_coleta: datetime
    importado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    origem: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }