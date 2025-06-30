from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://gemini.google.com/app")
wait = WebDriverWait(driver, 30)
prompt_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ql-editor[contenteditable="true"]')))
prompt_box.send_keys("Teste de prompt Gemini. Responda apenas: OK.")
submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.input-area-container button.send-button')))
submit_button.click()

# Espera resposta
response_selector = (By.CSS_SELECTOR, '.response-content .markdown')
resposta = WebDriverWait(driver, 60).until(
    EC.presence_of_all_elements_located(response_selector)
)
print("Resposta Gemini:", resposta[-1].text.strip())
driver.quit()