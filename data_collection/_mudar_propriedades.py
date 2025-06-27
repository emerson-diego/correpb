import os
from dotenv import load_dotenv

from pymongo import MongoClient

load_dotenv()

# Conectar ao MongoDB
client = MongoClient(os.getenv("MONGODB_REMOTE_URI"))
db = client['corridas_db']
collection = db['eventos']

# Mapeamento de nomes antigos para novos
mapeamento = {
    "Nome do Evento": "nome_evento",
    "Link de Inscrição": "url_inscricao",
    "Link da Imagem": "url_imagem",
    "Data": "data_realizacao",
    "Cidade": "cidade",
    "Distância": "distancias",
    "Organizador": "organizador",
    "fonte": "site_coleta",
    "data_importacao": "data_coleta"
}

# Processar cada documento
for doc in collection.find({}):
    updates = {"$set": {}, "$unset": {}}
    needs_update = False

    # Para cada campo no mapeamento
    for nome_antigo, nome_novo in mapeamento.items():
        if nome_antigo in doc:
            # Copia o valor exatamente como está
            updates["$set"][nome_novo] = doc[nome_antigo]
            updates["$unset"][nome_antigo] = ""
            needs_update = True

    # Limpa $unset se não houver campos para remover
    if not updates["$unset"]:
        del updates["$unset"]
    # Limpa $set se não houver campos para adicionar/modificar
    if not updates["$set"]:
        del updates["$set"]

    # Aplica as atualizações se necessário
    if needs_update and ("$set" in updates or "$unset" in updates):
        collection.update_one({"_id": doc["_id"]}, updates)

print(f"Processamento da coleção 'eventos' concluído. Campos renomeados mantendo seus valores originais.") 