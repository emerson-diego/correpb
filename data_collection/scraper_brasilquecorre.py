import csv
import re
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By


def setup_driver():
    options = webdriver.ChromeOptions()
    # Removendo o modo headless para ver o navegador
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def get_event_data(driver):
    try:
        # Acessar a página de eventos
        driver.get("https://brasilquecorre.com/paraiba")
        
        # Aguardar os elementos carregarem
        time.sleep(3)
        
        # Encontrar todos os elementos de evento
        event_boxes = driver.find_elements(By.CSS_SELECTOR, "div.cs-box")
        
        # Lista para armazenar os dados dos eventos
        event_data = []
        
        # Padrão para identificar datas no formato brasileiro
        data_pattern = re.compile(r'\d{1,2}\s+de\s+[A-Za-zçÇ]+\s+de\s+\d{4}')
        
        for box in event_boxes:
            try:
                # Extrair dados do evento
                event_info = {}
                
                # Nome do evento e link
                name_element = box.find_element(By.CSS_SELECTOR, "h5 a")
                event_info['nome'] = name_element.text
                event_info['link_inscricao'] = name_element.get_attribute('href')
                
                # Link da imagem
                img_element = box.find_element(By.CSS_SELECTOR, "img.cs-chosen-image")
                event_info['link_imagem'] = img_element.get_attribute('src')
                
                # Metadados
                text_elements = box.find_elements(By.CSS_SELECTOR, "div.text-editor p")
                distancias_encontradas = []
                for idx, element in enumerate(text_elements):
                    text = element.text.strip()
                    if text and not text.isspace():
                        # Verificar se é uma data usando regex
                        if data_pattern.search(text):
                            event_info['data'] = text
                        elif text.endswith('(corrida)') or text.endswith('(caminhada)') or text.endswith('(trail)') or text.endswith('(ultra)') or '(corrida' in text or '(trail' in text or '(caminhada' in text or '(infantil' in text:
                            distancias_encontradas.append(text)
                        # Se for o último <p>, considerar como organizador
                        elif idx == len(text_elements) - 1:
                            event_info['organizador'] = text
                        # Preencher cidade apenas se ainda não foi preenchido
                        elif 'cidade' not in event_info:
                            event_info['cidade'] = text
                if distancias_encontradas:
                    event_info['distancia'] = ', '.join(distancias_encontradas)
                
                event_data.append(event_info)
                
            except Exception as e:
                #print(f"Erro ao extrair dados de um evento: {str(e)}")
                continue
                
        return event_data
        
    except Exception as e:
        print(f"Erro ao buscar dados dos eventos: {str(e)}")
        return []

def main():
    # Configurar driver
    driver = setup_driver()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'eventos_brasilquecorre.csv')

    try:
        # Criar arquivo CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Nome do Evento', 'Link de Inscrição', 'Link da Imagem', 'Data', 'Cidade', 'Distância', 'Organizador'])
            
            # Obter dados dos eventos
            event_data = get_event_data(driver)
            print(f"Encontrados {len(event_data)} eventos")
            
            # Processar cada evento
            for event in event_data:
                writer.writerow([
                    event.get('nome', ''),
                    event.get('link_inscricao', ''),
                    event.get('link_imagem', ''),
                    event.get('data', ''),
                    event.get('cidade', ''),
                    event.get('distancia', ''),
                    event.get('organizador', '')
                ])
                print(f"Evento salvo: {event.get('nome', '')}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 