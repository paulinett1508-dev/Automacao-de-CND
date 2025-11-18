from flask import Flask, render_template, request, send_from_directory
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

app = Flask(__name__)

# --- Função de Automação Selenium --- #
def run_selenium(email, password, cnpj):
    """
    Executa a automação principal com Selenium para baixar os arquivos.
    """
    download_directory = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    chrome_options = webdriver.ChromeOptions()
    # Roda o navegador em modo "headless" (sem interface gráfica)
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--window-size=1920,1080") # Especificar tamanho da janela é bom para headless
    chrome_options.add_experimental_option("prefs", {
      "download.default_directory": download_directory,
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "safebrowsing.enabled": True
    })

    driver = None # Inicializa o driver como None
    try:
        print("Iniciando automação...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 40) # Aumenta o tempo de espera

        # --- 1. Acessar a página de Login ---
        driver.get("https://hub.sieg.com/IriS/#/Certidoes")
        print("Página de login acessada.")

        # --- 2. Realizar Login ---
        wait.until(EC.presence_of_element_located((By.NAME, 'txtEmail'))).send_keys(email)
        driver.find_element(By.NAME, 'txtPassword').send_keys(password)
        driver.find_element(By.NAME, 'btnSubmit').click()
        print("Tentativa de login realizada.")

        # --- 3. Aguardar o login e redirecionamento ---
        # Espera até que um elemento da página principal pós-login seja clicável
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-selection__placeholder')))
        print("Login bem-sucedido e página de certidões carregada.")
        
        # --- 4. Buscar Empresa e Baixar CNDs ---
        driver.find_element(By.CLASS_NAME, 'select2-selection__placeholder').click() # Abrir busca
        # Espera o campo de busca aparecer e insere o CNPJ
        search_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/span/span/span[1]/input")))
        search_input.send_keys(cnpj + Keys.ENTER)
        print(f"Buscando pelo CNPJ: {cnpj}")
        
        # Espera o botão de download ficar clicável e clica
        download_button = wait.until(EC.element_to_be_clickable((By.ID, 'btnDownloadCertidaoLot')))
        download_button.click()
        print("Comando de download enviado.")

        # --- 5. Aguardar o Download ---
        # Lógica básica de espera: verificar se um novo arquivo apareceu.
        # Para uma solução mais robusta, seria necessário monitorar a pasta.
        time.sleep(30) # Aumentado para garantir tempo de download
        print("Download provavelmente concluído.")

    except Exception as e:
        print(f"Ocorreu um erro durante a automação: {e}")
        # Tira um screenshot para ajudar a depurar o erro em modo headless
        if driver:
            driver.save_screenshot('error_screenshot.png')
            print("Screenshot do erro salvo como 'error_screenshot.png'")

    finally:
        if driver:
            driver.quit()
            print("Navegador fechado. Automação finalizada.")

# --- Rotas da Aplicação Web --- #

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cnpj = request.form['cnpj']
        
        # Inicia a tarefa de automação em uma thread separada
        thread = threading.Thread(target=run_selenium, args=(email, password, cnpj))
        thread.start()
        
        return "Processo de automação iniciado! O download será feito na pasta 'downloads' do projeto. Você pode fechar esta página."
    
    return render_template('index.html')

@app.route('/downloads/<path:filename>')
def download_file(filename):
    """
    Rota para servir os arquivos baixados.
    """
    download_directory = os.path.join(os.getcwd(), "downloads")
    return send_from_directory(download_directory, filename, as_attachment=True)


if __name__ == '__main__':
    # Usa a porta do ambiente (fornecida pela IDE) ou 5001 como padrão
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
