from selenium import webdriver
import time
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json


class Scraper:
    web: webdriver.Chrome = None

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        service = Service(ChromeDriverManager().install())
        self.web = webdriver.Chrome(service=service, options=options)

    

if __name__ == "__main__":
    w = Scraper()
    print(w)
