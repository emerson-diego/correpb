import os
import time
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pyperclip
import json

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configurações ---
GEMINI_URL = "https://gemini.google.com/app/3fb09e64298c2898"
CHROME_DEBUG_PORT = "9222"
DELAY_ENTRE_DOCUMENTOS = 5
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR.parent / "jsonl" / "2_dataset_treinamento_anonimizado.jsonl"
OUTPUT_FILE = SCRIPT_DIR.parent / "jsonl" / "3_dataset_treinamento_entidades.jsonl"
PROMPT_FILE_PATH = SCRIPT_DIR.parent.parent / "prompt_reconhece_ners"


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
    """Envia um texto para o Gemini e retorna a lista de entidades extraídas."""
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
        return resultado_texto
    except TimeoutException as e:
        if "A resposta do Gemini não foi marcada como 'completa' no tempo esperado." in e.msg:
            raise
        logging.error(f"Tempo de espera excedido: {e.msg}")
        return None
    except (NoSuchElementException, IndexError):
        logging.error("Não foi possível encontrar um dos elementos (prompt, botão ou resposta) na página do Gemini.")
        return None

def main():
    driver = conectar_chrome_existente(CHROME_DEBUG_PORT)
    if not driver:
        return
    prompt_revisao = carregar_prompt(PROMPT_FILE_PATH)
    if not prompt_revisao:
        logging.error("Não foi possível carregar o prompt. Encerrando o script.")
        return
    driver.get(GEMINI_URL)
    time.sleep(5)
    if not INPUT_FILE.exists():
        logging.error(f"Arquivo de entrada não encontrado: {INPUT_FILE}")
        return
    with open(INPUT_FILE, "r", encoding="utf-8") as fin, open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin, 1):
            try:
                dado = json.loads(line)
                doc_id = dado.get("id")
                texto = dado.get("text")
                if not texto:
                    logging.warning(f"Linha {i} ignorada: campo 'text' vazio ou ausente.")
                    continue
                logging.info(f"Processando documento {i} (ID: {doc_id})")
                max_tentativas = 2
                resultado = None
                for tentativa in range(max_tentativas):
                    try:
                        resultado = revisar_com_gemini(driver, texto, prompt_revisao)
                        if resultado is not None:
                            break
                    except TimeoutException as e:
                        logging.error(f"Timeout na tentativa {tentativa + 1}/{max_tentativas} para o doc {doc_id}: {e.msg}")
                        if tentativa < max_tentativas - 1:
                            logging.info("Recarregando a página para tentar novamente...")
                            driver.get(GEMINI_URL)
                            time.sleep(5)
                        else:
                            logging.error(f"Falha final para o doc {doc_id} após {max_tentativas} tentativas. Pulando.")
                if resultado is not None:
                    # Tenta converter a resposta para lista de entidades
                    try:
                        resposta_texto = resultado.strip()
                        # Remove prefixo "JSON\n" se existir
                        if resposta_texto.startswith("JSON\n"):
                            resposta_texto = resposta_texto[5:]
                        if resposta_texto.startswith("```json"):
                            resposta_texto = resposta_texto[7:-3].strip()
                        elif resposta_texto.startswith("```python"):
                            resposta_texto = resposta_texto[9:-3].strip()
                        elif resposta_texto.startswith("```"):
                            resposta_texto = resposta_texto[3:-3].strip()
                        if resposta_texto.startswith("python"):
                            resposta_texto = resposta_texto[len("python"):].strip()
                        try:
                            entities_raw = json.loads(resposta_texto)
                        except json.JSONDecodeError:
                            import ast
                            entities_raw = ast.literal_eval(resposta_texto)
                        if not isinstance(entities_raw, list):
                            raise ValueError("A resposta não é uma lista.")
                    except Exception as e:
                        logging.warning(f"A resposta do Gemini não pôde ser convertida para lista. Salvando como lista vazia. Erro: {e}")
                        entities_raw = []
                    saida = {"id": doc_id, "text": texto, "entities_raw": entities_raw}
                    json.dump(saida, fout, ensure_ascii=False)
                    fout.write("\n")
                    logging.info(f"Documento {i} processado e salvo.")
                    logging.info(f"Aguardando {DELAY_ENTRE_DOCUMENTOS} segundos...")
                    time.sleep(DELAY_ENTRE_DOCUMENTOS)
                else:
                    logging.error(f"Falha não recuperável ao processar documento {doc_id}. Pulando.")
            except Exception as e:
                logging.error(f"Erro inesperado na linha {i}: {e}")
    logging.info("Processo concluído. Todos os documentos foram processados.")
    driver.quit()

if __name__ == "__main__":
    main() 