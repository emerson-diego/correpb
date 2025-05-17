import csv
from datetime import datetime

from evento_de_corrida import EventoDeCorrida
from pymongo import MongoClient


def connect_mongodb():
    # Conectar ao MongoDB na porta 27018
    client = MongoClient('mongodb://localhost:27018/')
    return client['corridas_db']

def import_csv_to_mongodb(db, csv_file, fonte):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Ler o CSV com ponto e vírgula como separador
            reader = csv.DictReader(file, delimiter=';')
            
            # Contador para novos eventos
            novos_eventos = 0
            
            # Converter cada linha para um documento MongoDB
            for row in reader:
                try:
                    # Criar instância de EventoDeCorrida
                    evento = EventoDeCorrida.from_csv_row(row, fonte)
                    
                    # Verificar se já existe um evento com o mesmo nome
                    evento_existente = db.eventos.find_one({'nome_evento': evento.nome_evento})
                    
                    if not evento_existente:
                        # Converter para dicionário e inserir no MongoDB
                        db.eventos.insert_one(evento.to_dict())
                        novos_eventos += 1
                        
                except Exception as e:
                    print(f"❌ Erro ao processar linha do CSV: {str(e)}")
                    print(f"Conteúdo da linha: {row}")
                    continue
                
        print(f"✅ Dados de {fonte} processados com sucesso")
        print(f"📝 {novos_eventos} novos eventos adicionados")
        
    except Exception as e:
        print(f"❌ Erro ao importar dados de {fonte}: {str(e)}")

def main():
    try:
        # Conectar ao MongoDB
        db = connect_mongodb()
        
        # Importar dados dos CSVs
        import_csv_to_mongodb(db, 'data_collection/eventos_brasilcorrida.csv', 'brasilcorrida')
        import_csv_to_mongodb(db, 'data_collection/eventos_brasilquecorre.csv', 'brasilquecorre')
        
        # Contar documentos importados
        total = db.eventos.count_documents({})
        print(f"\n📊 Total de eventos na base: {total}")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

if __name__ == "__main__":
    main() 