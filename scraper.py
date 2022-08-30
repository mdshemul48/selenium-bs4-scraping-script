import secrets
from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep

from envInfo import SITE_EMAIL, SITE_LINK, SITE_PASSWORD


def getSiteLink(path): return SITE_LINK + path


class Scraper:
    web: webdriver.Chrome = None

    def __init__(self) -> None:

        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        service = Service(ChromeDriverManager().install())
        self.web = webdriver.Chrome(service=service, options=options)

    def login(self):
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

    def getPage(self, path):
        self.web.get(getSiteLink(path))
        try:
            loginButtonAddress = (
                '//*[@id="container"]/div/div/div/div/div[2]/form/div[4]/div/button'
            )
            self.web.find_element(By.XPATH, loginButtonAddress)
            self.login()
            self.web.get(getSiteLink(path))
        except:
            pass

    def getHtmlBs4(self, htmlSource=None):
        if not htmlSource:
            htmlSource = self.web.page_source
        return bs4(htmlSource, "html.parser")


class ScraperSingle(Scraper):
    def __init__(self, resellerName: str) -> None:
        super().__init__()
        self.resellerName = resellerName

    def getResellerInfo(self):
        self.getPage("/reseller")
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

    def getResellerPop(self):
        self.getPage("/pop")
        self.web.find_element(By.XPATH, '//*[@id="datatbl_filter"]/label/input').send_keys(self.resellerName)

        sleep(4)

        elementHtml = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")

        bs4 = self.getHtmlBs4(elementHtml)
        pops = bs4.find_all("tr")

        AllThePop = []
        for pop in pops:
            popId = str(pop.find_all("td")[0].renderContents())
            print(popId)
            # pop info


class SuperScrapper(Scraper):
    def __init__(self) -> None:
        super().__init__()

    def getAllTheMikroTik(self):
        self.getPage("/mikrotik")

        Select(self.web.find_element(By.XPATH, '//*[@id="datatbl_length"]/label/select')).select_by_visible_text("All")

        sleep(5)

        dataTable = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")

        dataOfMKs = self.getHtmlBs4(dataTable)

        allMKInfo = []

        for mk in dataOfMKs.find_all('tr'):
            mkRow = [singleMkInfo.text.strip() for singleMkInfo in mk.find_all("td")]
            mkId, mkIp, mkSecret, mkName, mkType, mkDescription, *_ = mkRow

            allMKInfo.append({
                "id": mkId,
                "name": mkName,
                "ip": mkIp,
                "secret": mkSecret,
                "type": mkType,
                "description": mkDescription
            })

        return allMKInfo


if __name__ == "__main__":
    w = SuperScrapper()
    print(w.getAllTheMikroTik())
    print(w)
