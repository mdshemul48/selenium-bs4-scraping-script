from selenium import webdriver
import time
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from envInfo import SITE_EMAIL, SITE_LINK, SITE_PASSWORD

getSiteLink = lambda path: SITE_LINK + path


class Scraper:
    web: webdriver.Chrome = None
    resellerName: str = None

    def __init__(self, resellerName: str) -> None:
        self.resellerName = resellerName

        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        service = Service(ChromeDriverManager().install())
        self.web = webdriver.Chrome(service=service, options=options)

    def __login(self):
        self.web.get(getSiteLink("/auth/login"))
        emailInputBox = self.web.find_element(
            By.XPATH,
            '//*[@id="container"]/div/div/div/div/div[2]/form/div[1]/div/input',
        )
        passwordInputBox = self.web.find_element(
            By.XPATH,
            '//*[@id="container"]/div/div/div/div/div[2]/form/div[2]/div/input',
        )
        loginButton = self.web.find_element(
            By.XPATH,
            '//*[@id="container"]/div/div/div/div/div[2]/form/div[4]/div/button',
        )
        emailInputBox.send_keys(SITE_EMAIL)
        passwordInputBox.send_keys(SITE_PASSWORD)
        loginButton.click()

    def __getPage(self, path):
        self.web.get(getSiteLink(path))
        try:
            loginButtonAddress = (
                '//*[@id="container"]/div/div/div/div/div[2]/form/div[4]/div/button'
            )
            self.web.find_element(By.XPATH, loginButtonAddress)
            self.__login()
            self.web.get(getSiteLink(path))
        except:
            pass

    def __getPageHtml(self):
        pageHtml = self.web.page_source
        return BeautifulSoup(pageHtml, "html.parser")

    def getResellerInfo(self):
        self.__getPage("/reseller")
        self.web.find_element(
            By.XPATH, '//*[@id="datatbl_filter"]/label/input'
        ).send_keys(self.resellerName)
        self.web.find_element(
            By.XPATH, '//*[@id="datatbl"]/tbody/tr/td[9]/a[2]'
        ).click()

        resellerName = self.web.find_element(
            By.XPATH, '//*[@id="resellername"]'
        ).get_attribute("value")

        address = self.web.find_element(
            By.XPATH, '//*[@id="reselleraddress"]'
        ).get_attribute("value")

        comment = self.web.find_element(
            By.XPATH, '//*[@id="resellerremarks"]'
        ).get_attribute("value")

        phone = self.web.find_element(
            By.XPATH, '//*[@id="resellercontact"]'
        ).get_attribute("value")

        return {
            "name": resellerName,
            "address": address,
            "comment": comment,
            "phone": phone,
        }


if __name__ == "__main__":
    w = Scraper("CN-BARISHAL")
    print(w.getResellerInfo())
    print(w)
