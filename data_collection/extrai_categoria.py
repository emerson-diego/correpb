import os
import time
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pyperclip
import json
import requests
from PyPDF2 import PdfReader
import csv

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurações ---
GEMINI_URL = "https://gemini.google.com/app/3fb09e64298c2898"
CHROME_DEBUG_PORT = "9222"
DELAY_ENTRE_DOCUMENTOS = 5
SCRIPT_DIR = Path(__file__).parent
PROMPT_FILE_PATH = SCRIPT_DIR / "prompt_obtem_categorias"


def conectar_chrome_existente(port):
    """Conecta a uma instância do Chrome em execução com a porta de depuração remota."""
    logging.info(f"Tentando se conectar ao Chrome na porta de depuração {port}...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logging.info("Conexão com o Chrome estabelecida com sucesso.")
        return driver
    except Exception as e:
        logging.error(f"Não foi possível conectar ao Chrome. Verifique se ele foi iniciado com a porta de depuração remota.")
        logging.error(f"Comando sugerido: google-chrome --remote-debugging-port={port} --user-data-dir=~/.config/google-chrome/Default")
        logging.error(f"Erro: {e}")
        return None

def carregar_prompt(caminho_arquivo):
    """Carrega o conteúdo do prompt de um arquivo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            prompt = f.read()
        logging.info(f"Prompt carregado com sucesso de {caminho_arquivo}")
        return prompt
    except FileNotFoundError:
        logging.error(f"Arquivo de prompt não encontrado em: {caminho_arquivo}")
        return None
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo de prompt: {e}")
        return None

def revisar_com_gemini(driver, texto, prompt):
    """Envia um texto para o Gemini e retorna a linha de categorias premiadas."""
    try:
        prompt_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ql-editor[contenteditable="true"]'))
        )
        prompt_box.send_keys(Keys.CONTROL + "a")
        prompt_box.send_keys(Keys.BACK_SPACE)
        time.sleep(0.5)
        texto_completo = prompt.replace("{texto}", texto)
        pyperclip.copy(texto_completo)
        prompt_box.send_keys(Keys.CONTROL + "v")
        time.sleep(1)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", prompt_box)
        time.sleep(0.5)
        submit_button_selector = (By.CSS_SELECTOR, '.input-area-container button.send-button')
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(submit_button_selector)
        )
        footer_completo_selector = (By.CSS_SELECTOR, 'div.response-footer.complete')
        respostas_completas_antes = driver.find_elements(*footer_completo_selector)
        driver.execute_script("arguments[0].click();", submit_button)
        WebDriverWait(driver, 120).until(
            lambda d: len(d.find_elements(*footer_completo_selector)) > len(respostas_completas_antes),
            message="A resposta do Gemini não foi marcada como 'completa' no tempo esperado."
        )
        response_selector = (By.CSS_SELECTOR, '.response-content .markdown')
        respostas = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(response_selector)
        )
        resultado_texto = respostas[-1].text.strip()
        # Remove qualquer formatação extra, cabeçalho, markdown, etc.
        resposta = resultado_texto.strip()
        if resposta.startswith("```") or resposta.startswith("JSON"):
            resposta = resposta.split('\n', 1)[-1].strip()
        return resposta
    except TimeoutException as e:
        if e.msg and "A resposta do Gemini não foi marcada como 'completa' no tempo esperado." in e.msg:
            raise
        logging.error(f"Tempo de espera excedido: {e.msg}")
        return None
    except (NoSuchElementException, IndexError):
        logging.error("Não foi possível encontrar um dos elementos (prompt, botão ou resposta) na página do Gemini.")
        return None



def extrai_categorias_do_pdf(link_pdf, driver=None, prompt=None):
    """Fluxo completo: passa o link do PDF no prompt e retorna as categorias premiadas como string."""
    if not link_pdf or link_pdf.lower() == 'edital não encontrado':
        return ''
    if driver is None:
        driver = conectar_chrome_existente(CHROME_DEBUG_PORT)
        close_driver = True
    else:
        close_driver = False
    if prompt is None:
        prompt = carregar_prompt(PROMPT_FILE_PATH)
    if not prompt:
        if close_driver and driver is not None:
            driver.quit()
        return ''
    # Monta o prompt substituindo o marcador pelo link
    prompt_final = prompt.replace('{link}', link_pdf)
    print(f"[DEBUG] Prompt enviado ao Gemini:\n{prompt_final}\n---")
    categorias = revisar_com_gemini(driver, '', prompt_final)
    print(f"[DEBUG] Resposta recebida do Gemini: {categorias}")
    if close_driver and driver is not None:
        driver.quit()
    return categorias or ''

def processa_csvs_com_categorias():
    arquivos = ["eventos_brasilquecorre.csv", "eventos_brasilcorrida.csv"]
    for arquivo in arquivos:
        caminho = os.path.join(os.path.dirname(__file__), arquivo)
        linhas = []
        with open(caminho, encoding='utf-8') as fin:
            reader = csv.DictReader(fin, delimiter=';')
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            if 'Categorias Premiadas' not in fieldnames:
                fieldnames.append('Categorias Premiadas')
            for row in reader:
                link_edital = row.get('Link do Edital', '').strip() if 'Link do Edital' in row else ''
                print(f"[DEBUG] Evento: {row.get('Nome do Evento', '')}")
                print(f"[DEBUG] Link do Edital encontrado: {link_edital}")
                if not link_edital or link_edital.lower() == 'edital não encontrado':
                    print("[DEBUG] Nenhum link de edital válido encontrado para este evento.")
                    categorias = 'Não disponível'
                else:
                    try:
                        categorias = extrai_categorias_do_pdf(link_edital)
                        print(f"[DEBUG] Categorias extraídas: {categorias}")
                    except Exception as e:
                        print(f"[DEBUG] Erro ao extrair categorias: {e}")
                        categorias = 'erro ao extrair'
                row['Categorias Premiadas'] = categorias
                linhas.append(row)
        with open(caminho, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(linhas)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'csv':
        processa_csvs_com_categorias()
    elif len(sys.argv) > 1:
        link = sys.argv[1]
        categorias = extrai_categorias_do_pdf(link)
        print(categorias)
    else:
        print("Uso: python extrai_categoria.py <url_pdf> ou python extrai_categoria.py csv") 