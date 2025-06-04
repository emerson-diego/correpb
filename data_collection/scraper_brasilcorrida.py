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
                # Função auxiliar para extrair texto com tratamento de erro
                def get_text_safe(element, xpath):
                    try:
                        return element.find_element(By.XPATH, xpath).text.strip()
                    except:
                        return ''

                # Função auxiliar para extrair atributo com tratamento de erro
                def get_attribute_safe(element, xpath, attribute):
                    try:
                        return element.find_element(By.XPATH, xpath).get_attribute(attribute)
                    except:
                        return ''

                # Extrair dados do evento
                nome_evento = get_text_safe(card, ".//h6[contains(@class, 'fs-0')]")
                link_evento = get_attribute_safe(card, ".//a[contains(@href, 'evento')]", 'href')
                link_imagem = get_attribute_safe(card, ".//img[contains(@class, 'card-span-img')]", 'src')
                data_evento = get_text_safe(card, ".//h6[contains(@class, 'fs--2') and contains(text(), '/')]")
                local_evento = get_text_safe(card, ".//h6[contains(@class, 'fs--2') and contains(text(), ',')]")
                organizador = get_text_safe(card, ".//a[contains(@href, 'organizador')]")

                # Formatar a data para o padrão brasileiro
                if data_evento and '/' in data_evento:
                    try:
                        dia, mes, ano = data_evento.split('/')
                        meses = {
                            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
                            '04': 'Abril', '05': 'Maio', '06': 'Junho',
                            '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
                            '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
                        }
                        data_evento = f"{dia} de {meses[mes]} de {ano}"
                    except:
                        pass

                # Extrair apenas a cidade do local (remover estado)
                if local_evento and ',' in local_evento:
                    local_evento = local_evento.split(',')[0].strip()

                event_data.append({
                    'nome': nome_evento,
                    'link_inscricao': link_evento,
                    'link_imagem': link_imagem,
                    'data': data_evento,
                    'cidade': local_evento,
                    'distancia': '',  # Deixando em branco conforme solicitado
                    'organizador': organizador
                })
                
            except Exception as e:
                print(f"❌ Erro ao processar card: {str(e)}")
                continue
                
        return event_data
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados dos eventos: {str(e)}")
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