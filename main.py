import uvicorn
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.core.database import Database
from app.api.eventos import router as eventos_router

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'api.log'))
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar paginação
add_pagination(app)

# Adicionar rotas
app.include_router(eventos_router, prefix="/api/v1/eventos", tags=["eventos"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização
    try:
        await Database.connect()
        logger.info("Conexão com o banco de dados estabelecida")
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")

    yield

    # Finalização
    await Database.close()
    logger.info("Conexão com o banco de dados fechada")

@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Bem-vindo à API do Corre PB!",
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    # Garantir que o diretório de logs exista
    os.makedirs('logs', exist_ok=True)

    # Iniciar servidor
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )