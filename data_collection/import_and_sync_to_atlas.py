import csv
import os

from dotenv import load_dotenv
from evento_de_corrida import EventoDeCorrida
from pymongo import MongoClient

# Tentar carregar do .env
load_dotenv()

# Carregar variáveis de ambiente do .env
# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Conexão remota (Atlas)
REMOTE_URI = os.getenv('MONGODB_URI')
if not REMOTE_URI:
    raise Exception('A variável MONGODB_REMOTE_URI não está definida no .env')
remote_client = MongoClient(REMOTE_URI)
remote_db = remote_client['corridas_db']
remote_collection = remote_db['eventos']

def import_csv_to_mongodb(db, csv_file, fonte):
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            novos_eventos = 0
            eventos_atualizados = 0
            for row in reader:
                try:
                    evento = EventoDeCorrida.from_csv_row(row, fonte)
                    evento_existente = db.eventos.find_one({'nome_evento': evento.nome_evento})
                    if not evento_existente:
                        db.eventos.insert_one(evento.to_dict())
                        novos_eventos += 1
                    else:
                        evento_dict = evento.to_dict()
                        evento_existente_dict = {k: v for k, v in evento_existente.items() if k != '_id'}
                        campos_nao_comparaveis = ['data_coleta']
                        for campo in campos_nao_comparaveis:
                            evento_dict.pop(campo, None)
                            evento_existente_dict.pop(campo, None)
                        if evento_dict != evento_existente_dict:
                            db.eventos.update_one(
                                {'nome_evento': evento.nome_evento},
                                {'$set': evento.to_dict()}
                            )
                            eventos_atualizados += 1
                except Exception as e:
                    print(f"❌ Erro ao processar linha do CSV: {str(e)}")
                    print(f"Conteúdo da linha: {row}")
                    continue
        print(f"✅ Dados de {fonte} processados com sucesso no Atlas")
        print(f"📝 {novos_eventos} novos eventos adicionados")
        print(f"🔄 {eventos_atualizados} eventos atualizados")
    except Exception as e:
        print(f"❌ Erro ao importar dados de {fonte}: {str(e)}")

def main():
    try:
        db = remote_db
        import_csv_to_mongodb(db, 'eventos_brasilcorrida.csv', 'brasilcorrida')
        import_csv_to_mongodb(db, 'eventos_brasilquecorre.csv', 'brasilquecorre')
        total = db.eventos.count_documents({})
        print(f"\n📊 Total de eventos na base Atlas: {total}")
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")

if __name__ == "__main__":
    main() 