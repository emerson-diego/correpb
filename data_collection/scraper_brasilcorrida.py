import csv
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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
        driver.get("https://brasilcorrida.com.br/#/calendario")
        
        # Aguardar a página carregar
        time.sleep(5)
        
        # Clicar no filtro de modalidade "Corrida de Rua"
        modalidade = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'filtro-modalidade-item')]//label[contains(text(), 'Corrida de Rua')]"))
        )
        modalidade.click()
        time.sleep(2)
        
        # Clicar no filtro de local
        local_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-link') and contains(@ng-click, 'ShowHideFiltrosEventos')]"))
        )
        local_button.click()
        time.sleep(2)
        
        # Clicar no input de cidade e selecionar PB
        cidade_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Selecione uma Cidade']"))
        )
        cidade_input.click()
        time.sleep(2)
        
        # Selecionar Paraíba
        paraiba = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table[@data-value='PB']"))
        )
        paraiba.click()
        time.sleep(2)
        
        # Clicar no botão de busca
        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(@class, 'bg-administradora')]"))
        )
        search_button.click()
        time.sleep(3)
        
        # Lista para armazenar os dados dos eventos
        event_data = []
        
        # Encontrar todos os cards de evento
        event_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'col-md-3') and contains(@class, 'col-sm-12')]//div[contains(@class, 'card')]"))
        )
        
        for card in event_cards:
            try:
                # Extrair nome do evento
                nome_element = card.find_element(By.XPATH, ".//h6[contains(@class, 'fs-0')]")
                nome_evento = nome_element.text
                
                # Extrair link do evento
                link_element = card.find_element(By.XPATH, ".//a[contains(@href, 'evento')]")
                link_evento = link_element.get_attribute('href')
                
                # Extrair imagem do evento
                img_element = card.find_element(By.XPATH, ".//img[contains(@class, 'card-span-img')]")
                link_imagem = img_element.get_attribute('src')
                
                # Extrair data do evento
                data_element = card.find_element(By.XPATH, ".//h6[contains(@class, 'fs--2') and contains(text(), '/')]")
                data_evento = data_element.text.strip()
                
                # Extrair local do evento
                local_element = card.find_element(By.XPATH, ".//h6[contains(@class, 'fs--2') and contains(text(), ',')]")
                local_evento = local_element.text.strip()
                
                # Extrair organizador do evento
                try:
                    org_element = card.find_element(By.XPATH, ".//a[contains(@href, 'organizador')]")
                    organizador = org_element.text.strip()
                except:
                    organizador = ""
                
                event_data.append({
                    'nome': nome_evento,
                    'link_inscricao': link_evento,
                    'link_imagem': link_imagem,
                    'data': data_evento,
                    'cidade': local_evento,
                    'distancia': '',  # Deixando em branco conforme solicitado
                    'organizador': organizador
                })
                
            except Exception:
                # Silenciar erros individuais
                continue
                
        return event_data
        
    except Exception:
        # Silenciar erros gerais
        return []

def main():
    # Configurar driver
    driver = setup_driver()
    
    try:
        # Criar arquivo CSV
        with open('data_collection/eventos_brasilcorrida.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Nome do Evento', 'Link de Inscrição', 'Link da Imagem', 'Data', 'Cidade', 'Distância', 'Organizador'])
            
            # Obter dados dos eventos
            event_data = get_event_data(driver)
            print(f"\n✅ Encontrados {len(event_data)} eventos")
            
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
                print(f"📝 Evento salvo: {event.get('nome', '')}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 