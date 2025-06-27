import pymongo
from pymongo import MongoClient

# String de conexão
connection_string = "mongodb+srv://correpb:mestrado_projeto_bd_2025@cluster0.szqymc6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Criar uma conexão com o MongoDB
    client = MongoClient(connection_string)

    # Verificar a conexão acessando a lista de bancos de dados
    db_list = client.list_database_names()
    print("Conectado ao MongoDB com sucesso!")
    print("Bancos de dados disponíveis:")
    for db in db_list:
        print(f" - {db}")

except pymongo.errors.ConnectionFailure as e:
    print(f"Erro ao conectar ao MongoDB: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")