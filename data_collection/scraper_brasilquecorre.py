import csv
import re
import time
import os
import requests
import io
from urllib.parse import urlparse

from PyPDF2 import PdfReader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Configura o driver do Selenium."""
    options = webdriver.ChromeOptions()
    # Removendo o modo headless para ver o navegador em ação
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def get_event_data(driver):
    """
    Extrai os dados dos eventos, incluindo o link e o texto do edital.
    """
    try:
        # Acessar a página principal de eventos da Paraíba
        driver.get("https://brasilquecorre.com/paraiba")
        
        # Esperar os elementos carregarem
        wait = WebDriverWait(driver, 10)
        event_boxes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cs-box")))
        
        event_data = []
        data_pattern = re.compile(r'\d{1,2}\s+de\s+[A-Za-zçÇ]+\s+de\s+\d{4}')
        
        # Armazena as janelas para poder navegar entre abas
        main_window = driver.current_window_handle

        for box in event_boxes:
            event_info = {}
            try:
                # Extrair dados básicos da página principal
                name_element = box.find_element(By.CSS_SELECTOR, "h5 a")
                event_info['nome'] = name_element.text
                event_info['link_inscricao'] = name_element.get_attribute('href')
                
                img_element = box.find_element(By.CSS_SELECTOR, "img.cs-chosen-image")
                event_info['link_imagem'] = img_element.get_attribute('src')
                
                text_elements = box.find_elements(By.CSS_SELECTOR, "div.text-editor p")
                distancias_encontradas = []
                for idx, element in enumerate(text_elements):
                    text = element.text.strip()
                    if text and not text.isspace():
                        if data_pattern.search(text):
                            event_info['data'] = text
                        elif any(term in text for term in ['(corrida)', '(caminhada)', '(trail)', '(ultra)', '(infantil)']):
                            distancias_encontradas.append(text)
                        elif idx == len(text_elements) - 1:
                            event_info['organizador'] = text
                        elif 'cidade' not in event_info:
                            event_info['cidade'] = text
                if distancias_encontradas:
                    event_info['distancia'] = ', '.join(distancias_encontradas)

                # --- Início da nova funcionalidade: Extrair Edital ---

                event_info['link_edital'] = 'edital não encontrado'

                # Abrir link do evento em uma nova aba
                driver.execute_script("window.open(arguments[0]);", event_info['link_inscricao'])
                driver.switch_to.window(driver.window_handles[1])

                try:
                    page_url = driver.current_url
                    domain = urlparse(page_url).netloc

                    if 'zeniteesportes.com' in domain:
                        try:
                            # Procura por links que contenham "regulamento" no texto ou que tenham onclick com PDF
                            reg_links = driver.find_elements(By.XPATH, "//a[contains(translate(text(), 'REGULAMENTO', 'regulamento'), 'regulamento') or contains(@onclick, '.PDF') or contains(@onclick, '.pdf')]")
                            
                            for link in reg_links:
                                # Verifica se tem onclick com PDF
                                onclick = link.get_attribute('onclick')
                                if onclick and ('.PDF' in onclick or '.pdf' in onclick):
                                    # Extrai o URL do PDF do onclick
                                    pdf_match = re.search(r"abrirPDF\('([^']+)'\)", onclick)
                                    if pdf_match:
                                        event_info['link_edital'] = pdf_match.group(1)
                                        break
                                # Se não tem onclick, verifica se o href é um PDF
                                elif link.get_attribute('href') and ('.pdf' in link.get_attribute('href').lower() or '.PDF' in link.get_attribute('href')):
                                    event_info['link_edital'] = link.get_attribute('href')
                                    break
                            
                            # Se não encontrou nenhum link específico, mantém 'edital não encontrado'
                            if event_info['link_edital'] == 'edital não encontrado':
                                print(f"Não foi possível encontrar o link do edital para: {event_info.get('nome', '')}")
                        except Exception:
                            pass

                    elif 'race83.com.br' in domain:
                        try:
                            pdf_link = driver.find_element(By.XPATH, "//a[contains(@href, '.pdf')]")
                            event_info['link_edital'] = pdf_link.get_attribute('href')
                        except Exception:
                            pass

                    elif 'correparaiba.com' in domain:
                        try:
                            pdf_link = driver.find_element(By.XPATH, "//a[contains(@href, '.pdf')]")
                            event_info['link_edital'] = pdf_link.get_attribute('href')
                        except Exception:
                            pass
                    # Se não encontrar, mantém 'edital não encontrado'
                except Exception:
                    pass

                # Fechar a aba do evento e voltar para a principal
                driver.close()
                driver.switch_to.window(main_window)
                
                # --- Fim da nova funcionalidade ---

                event_data.append(event_info)
                print(f"Dados extraídos para o evento: {event_info.get('nome', '')}")

            except Exception as e:
                # print(f"Erro ao extrair dados de um evento: {e}")
                # Se ocorrer um erro em um evento, fecha a aba extra e continua
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(main_window)
                continue
                
        return event_data
        
    except Exception as e:
        print(f"Erro crítico ao buscar dados dos eventos: {e}")
        return []

def main():
    """Função principal para executar o scraper e salvar os dados."""
    driver = setup_driver()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'eventos_brasilquecorre.csv')

    try:
        # Obter dados dos eventos
        event_data = get_event_data(driver)
        
        if not event_data:
            print("Nenhum evento encontrado ou ocorreu um erro.")
            return

        print(f"\nTotal de {len(event_data)} eventos encontrados. Salvando no CSV...")

        # Criar arquivo CSV e salvar os dados
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Adiciona os novos campos ao cabeçalho
            fieldnames = ['Nome do Evento', 'Link de Inscrição', 'Link da Imagem', 'Data', 'Cidade', 'Distância', 'Organizador', 'Link do Edital']
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(fieldnames)
            
            # Escrever os dados de cada evento
            for event in event_data:
                writer.writerow([
                    event.get('nome', ''),
                    event.get('link_inscricao', ''),
                    event.get('link_imagem', ''),
                    event.get('data', ''),
                    event.get('cidade', ''),
                    event.get('distancia', ''),
                    event.get('organizador', ''),
                    event.get('link_edital', '')
                ])
        
        print(f"\nDados salvos com sucesso em: {csv_path}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()