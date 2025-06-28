import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def analyze_site_structure():
    driver = setup_driver()
    
    try:
        # Acessar a página de eventos
        print("🌐 Acessando https://brasilcorrida.com.br/#/calendario")
        driver.get("https://brasilcorrida.com.br/#/calendario")
        
        # Aguardar a página carregar
        time.sleep(5)
        
        print("\n🔍 Analisando estrutura da página...")
        
        # Procurar por elementos relacionados a filtros
        print("\n📋 Procurando elementos de filtro:")
        
        # 1. Procurar por selects
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"Encontrados {len(selects)} elementos <select>")
        for i, select in enumerate(selects):
            try:
                print(f"  Select {i+1}:")
                print(f"    ID: {select.get_attribute('id')}")
                print(f"    Name: {select.get_attribute('name')}")
                print(f"    Class: {select.get_attribute('class')}")
                
                # Verificar opções
                options = select.find_elements(By.TAG_NAME, "option")
                print(f"    Opções ({len(options)}):")
                for j, option in enumerate(options[:5]):  # Mostrar apenas as primeiras 5
                    print(f"      {j+1}: {option.text} (value: {option.get_attribute('value')})")
                if len(options) > 5:
                    print(f"      ... e mais {len(options)-5} opções")
                print()
            except Exception as e:
                print(f"    Erro ao analisar select {i+1}: {str(e)}")
        
        # 2. Procurar por inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\nEncontrados {len(inputs)} elementos <input>")
        for i, input_elem in enumerate(inputs):
            try:
                placeholder = input_elem.get_attribute('placeholder')
                name = input_elem.get_attribute('name')
                id_attr = input_elem.get_attribute('id')
                
                if any(keyword in (placeholder or '').lower() for keyword in ['estado', 'uf', 'local', 'cidade']) or \
                   any(keyword in (name or '').lower() for keyword in ['estado', 'uf', 'local', 'cidade']) or \
                   any(keyword in (id_attr or '').lower() for keyword in ['estado', 'uf', 'local', 'cidade']):
                    print(f"  Input relevante {i+1}:")
                    print(f"    ID: {id_attr}")
                    print(f"    Name: {name}")
                    print(f"    Placeholder: {placeholder}")
                    print(f"    Type: {input_elem.get_attribute('type')}")
                    print()
            except Exception as e:
                continue
        
        # 3. Procurar por botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nEncontrados {len(buttons)} elementos <button>")
        for i, button in enumerate(buttons):
            try:
                text = button.text.strip()
                if any(keyword in text.lower() for keyword in ['pesquisar', 'buscar', 'filtrar', 'paraíba', 'pb']):
                    print(f"  Botão relevante {i+1}:")
                    print(f"    Texto: '{text}'")
                    print(f"    ID: {button.get_attribute('id')}")
                    print(f"    Class: {button.get_attribute('class')}")
                    print()
            except Exception as e:
                continue
        
        # 4. Procurar por elementos com texto "Paraíba" ou "PB"
        print("\n🔍 Procurando elementos com 'Paraíba' ou 'PB':")
        paraiba_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Paraíba') or contains(text(), 'PB')]")
        print(f"Encontrados {len(paraiba_elements)} elementos com 'Paraíba' ou 'PB'")
        for i, elem in enumerate(paraiba_elements[:10]):  # Mostrar apenas os primeiros 10
            try:
                print(f"  Elemento {i+1}:")
                print(f"    Tag: {elem.tag_name}")
                print(f"    Texto: '{elem.text.strip()}'")
                print(f"    ID: {elem.get_attribute('id')}")
                print(f"    Class: {elem.get_attribute('class')}")
                print(f"    Visível: {elem.is_displayed()}")
                print(f"    Habilitado: {elem.is_enabled()}")
                print()
            except Exception as e:
                print(f"    Erro ao analisar elemento {i+1}: {str(e)}")
        
        # 5. Procurar por elementos de filtro de modalidade
        print("\n🔍 Procurando filtros de modalidade:")
        modalidade_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Corrida de Rua') or contains(text(), 'corrida')]")
        print(f"Encontrados {len(modalidade_elements)} elementos relacionados a corrida")
        for i, elem in enumerate(modalidade_elements[:5]):
            try:
                print(f"  Modalidade {i+1}:")
                print(f"    Tag: {elem.tag_name}")
                print(f"    Texto: '{elem.text.strip()}'")
                print(f"    ID: {elem.get_attribute('id')}")
                print(f"    Class: {elem.get_attribute('class')}")
                print()
            except Exception as e:
                print(f"    Erro ao analisar modalidade {i+1}: {str(e)}")
        
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {str(e)}")
    
    finally:
        input("Pressione Enter para fechar o navegador...")
        driver.quit()

if __name__ == "__main__":
    analyze_site_structure() 