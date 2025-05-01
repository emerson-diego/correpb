import csv
from datetime import datetime

from pymongo import MongoClient


def connect_mongodb():
    # Conectar ao MongoDB na porta 27018
    client = MongoClient('mongodb://localhost:27018/')
    return client['corridas_db']

def clean_collection(db):
    # Limpar a coleção antes de inserir novos dados
    db.eventos.delete_many({})
    print("✅ Coleção 'eventos' limpa com sucesso")

def import_csv_to_mongodb(db, csv_file, fonte):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Ler o CSV com ponto e vírgula como separador
            reader = csv.DictReader(file, delimiter=';')
            
            # Converter cada linha para um documento MongoDB
            for row in reader:
                # Adicionar campos de metadados
                row['fonte'] = fonte
                row['data_importacao'] = datetime.now()
                
                # Inserir no MongoDB
                db.eventos.insert_one(row)
                
        print(f"✅ Dados de {fonte} importados com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao importar dados de {fonte}: {str(e)}")

def main():
    try:
        # Conectar ao MongoDB
        db = connect_mongodb()
        
        # Limpar a coleção
        clean_collection(db)
        
        # Importar dados dos CSVs
        import_csv_to_mongodb(db, 'eventos_brasilcorrida.csv', 'brasilcorrida')
        import_csv_to_mongodb(db, 'eventos_brasilquecorre.csv', 'brasilquecorre')
        
        # Contar documentos importados
        total = db.eventos.count_documents({})
        print(f"\n📊 Total de eventos importados: {total}")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

if __name__ == "__main__":
    main() 