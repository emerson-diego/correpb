import csv
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
                for element in text_elements:
                    text = element.text.strip()
                    if text and not text.isspace():
                        if 'de' in text and 'de' in text and 'de' in text:  # Data
                            event_info['data'] = text
                        elif text.endswith('(corrida)') or text.endswith('(caminhada)') or text.endswith('(trail)') or text.endswith('(ultra)'):  # Distância
                            event_info['distancia'] = text
                        elif text.isupper() or text.endswith('RUN') or text.endswith('SPORTS'):  # Organizador
                            event_info['organizador'] = text
                        else:  # Cidade
                            event_info['cidade'] = text
                
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
    
    try:
        # Criar arquivo CSV
        with open('eventos_brasilquecorre.csv', 'w', newline='', encoding='utf-8') as csvfile:
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