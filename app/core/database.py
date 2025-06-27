import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls):
        """Estabelece conexão com o banco de dados MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info(f"Conectado ao banco de dados {settings.MONGODB_DB_NAME}")
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    @classmethod
    async def close(cls):
        """Fecha a conexão com o banco de dados."""
        if cls.client is not None:  # Usar 'is not None' em vez de verificação booleana
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("Conexão com o banco de dados fechada")

    @classmethod
    async def get_database(cls) -> AsyncIOMotorDatabase:
        """
        Retorna a instância do banco de dados.

        Returns:
            AsyncIOMotorDatabase: Instância do banco de dados
        """
        if cls.db is None:  # Usar 'is None' em vez de verificação booleana
            await cls.connect()
        return cls.db

    @classmethod
    async def get_collection(cls, collection_name: str) -> AsyncIOMotorCollection:
        """
        Retorna uma coleção do banco de dados.

        Args:
            collection_name: Nome da coleção

        Returns:
            AsyncIOMotorCollection: Coleção do banco de dados
        """
        db = await cls.get_database()
        return db[collection_name]