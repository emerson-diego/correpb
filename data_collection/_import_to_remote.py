import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

# Carregar variáveis de ambiente do .env na raiz do projeto
load_dotenv()

# Conexão local
LOCAL_URI = os.getenv("MONGODB_URI_LOCAL")
local_client = MongoClient(LOCAL_URI)
local_db = local_client['corridas_db']
local_collection = local_db['eventos']

# Conexão remota
REMOTE_URI = os.getenv('MONGODB_URI')

if not REMOTE_URI:
    raise Exception('A variável MONGODB_REMOTE_URI não está definida no .env')
remote_client = MongoClient(REMOTE_URI)
remote_db = remote_client['corridas_db']
remote_collection = remote_db['eventos']

# Buscar todos os documentos do local
eventos = list(local_collection.find({}))

# Remover o _id para evitar conflito de chave
for evento in eventos:
    if '_id' in evento:
        del evento['_id']

if eventos:
    # Inserir todos no remoto
    result = remote_collection.insert_many(eventos)
    print(f"✅ {len(result.inserted_ids)} eventos exportados para o MongoDB remoto.")
else:
    print("Nenhum evento encontrado na base local para exportar.") 