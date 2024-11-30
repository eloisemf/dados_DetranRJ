from selenium import webdriver  #pip install selenium webdriver-manager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import logging 
import pandas as pd 

class DetranScraping(object):

    def __init__(self, logger: object = None) -> None: 
        super().__init__()
        self.className = 'DetranScraping'
        self.initializeLogger(logger=logger)
        self.url = ""        
        self.driver = None

    def initializeLogger(self, logger: object = None, level: int = logging.INFO) -> logging.Logger:
        if logger == None:
            self.logger = logging.getLogger(self.className)
            self.logger.setLevel(level)
            ch = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s")
            ch.setFormatter(formatter)
            ch.addFilter(logging.Filter(self.className))
            self.logger.addHandler(ch)
        else:
            self.logger = logger
            if self.logger.level != level:
                self.logger.setLevel(level)
    
    def link (self) -> str:
        self.url = "https://www.detran.rj.gov.br/_estatisticas.veiculos/09.asp"
        self.logger.info(f"Acessando url:{self.url}")
        return self.url

    def browser (self) -> bool:
        try:
            options = Options()
            options.add_argument("--headless")  
            options.add_argument("--disable-gpu") 

            driver_service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=driver_service, options=options)
            
            self.driver.get(self.url)
            self.logger.info("Navegador iniciado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro de acesso a URL: {e}")
            return False

    def acessarModelo(self):
        try:
            select_element = self.driver.find_element(By.NAME, "menuzinho") 
            select = Select(select_element)
            
            select.select_by_value("09.asp?menuzinho=09.asp")
            self.logger.info(f'{select_element} encontrado com sucesso')
        except NoSuchElementException:
            self.logger.error(f"{select_element} não encontrado")

    def acessarAno(self):
        try:
            select_element = self.driver.find_element(By.NAME, "ano") 
            select = Select(select_element)
            
            select.select_by_value("2024")

            self.logger.info(f'{select_element} encontrado com sucesso')
        except NoSuchElementException:
            self.logger.error(f"{select_element} não encontrado")

    def acessarMes(self):
        try:
            select_element = self.driver.find_element(By.NAME, "mes") 
            select = Select(select_element)
            
            select.select_by_value("todos")
            self.logger.info(f'{select_element} encontrado com sucesso')
        except NoSuchElementException:
            self.logger.error(f"{select_element} não encontrado")

    def tabela(self):
        try:
            tabelas = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tbArtigo")))

            if len(tabelas) == 0:
                self.logger.Warning("Tabela não encontrada")
                return

            dados_compilados = []

            for tabela in tabelas:
        
                caption = tabela.find_element(By.TAG_NAME, "caption").text
                
                thead = tabela.find_element(By.TAG_NAME, "thead")
                colunas = [th.text for th in thead.find_elements(By.TAG_NAME, "th")]
                
                tbody = tabela.find_element(By.TAG_NAME, "tbody")
                linhas = tbody.find_elements(By.TAG_NAME, "tr")
                
                for linha in linhas:
                    tds = linha.find_elements(By.TAG_NAME, "td")
                   
                    dados = [td.text for td in tds[1:]]  
                    
                    if len(dados) == len(colunas):  
                        dados_compilados.append([caption] + dados)
                    else:
                        self.logger.warning(f"Inconsistência na linha: {dados}")
                
            if dados_compilados:
                colunas_final = ["Categoria"] + colunas
                df = pd.DataFrame(dados_compilados, columns=colunas_final)
                df.to_csv("infrações-DETRAN.csv", index=False)
            else:
                self.logger.warning("Nenhuma tabela de dado encontrado")
        except Exception as e:
            self.logger.error(f"Erro ao acessar tabela: {e}")

    def finalizar(self):
        if self.driver:
            self.driver.quit()
            self.logger.info("Navegador fechado com sucesso")


if __name__ == "__main__":
    rodar = DetranScraping()
    rodar.link()
    if rodar.browser():
        rodar.acessarModelo()
        rodar.acessarAno()
        rodar.acessarMes()
        rodar.tabela()
    rodar.finalizar()
    
