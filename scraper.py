from selenium import webdriver
from bs4 import BeautifulSoup as bs4
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep
import json

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
            loginButtonAddress = '//*[@id="container"]/div/div/div/div/div[2]/form/div[4]/div/button'
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
        self.web.find_element(By.XPATH, '//*[@id="datatbl_filter"]/label/input').send_keys(self.resellerName)

        self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody/tr/td[9]/a[2]').click()

        resellerName = self.web.find_element(By.XPATH, '//*[@id="resellername"]').get_attribute("value")

        address = self.web.find_element(By.XPATH, '//*[@id="reselleraddress"]').get_attribute("value")

        comment = self.web.find_element(By.XPATH, '//*[@id="resellerremarks"]').get_attribute("value")

        phone = self.web.find_element(By.XPATH, '//*[@id="resellercontact"]').get_attribute("value")

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

    def getAllTheReseller(self):
        self.getPage("/reseller")

        Select(self.web.find_element(By.XPATH, '//*[@id="datatbl_length"]/label/select')).select_by_visible_text("All")

        sleep(5)
        dataOfResellers = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")
        dataOfResellersInBs4 = self.getHtmlBs4(dataOfResellers)

        resellersInfo = []

        for reseller in dataOfResellersInBs4.find_all('tr'):
            # reseller info
            resellerRow = [singleResellerInfo.text.strip() for singleResellerInfo in reseller.find_all("td")]
            resellerId, resellerName, resellerAddress, resellerContact, resellerRemarks, resellerBalance, *_ = resellerRow

            # getting reseller package
            self.getPage(f"/package-permission/{resellerId}")
            sleep(2)

            packageTable = self.getHtmlBs4(self.web.find_element(
                By.XPATH, '//*[@id="dtProduct"]/tbody').get_attribute("innerHTML"))

            hasPackage = []
            for package in packageTable.find_all("tr"):
                if package.find("input").has_key("checked"):
                    _, packageId, packageName, packageRate, poolName, *_ = [
                        packageRow.text.strip() for packageRow in package.find_all("td")]

                    hasPackage.append({
                        "id": packageId,
                        "name": packageName,
                        "price": packageRate,
                        "poolName": poolName
                    })

            resellersInfo.append({
                "id": resellerId,
                "name": resellerName,
                "address": resellerAddress,
                "contact": resellerContact,
                "remarks": resellerRemarks,
                "balance": resellerBalance,
                "hasPackage": hasPackage
            })

        return resellersInfo

    def getAllThePop(self):
        self.getPage("/pop")
        Select(self.web.find_element(By.XPATH, '//*[@id="datatbl_length"]/label/select')).select_by_visible_text("All")

        sleep(5)

        dataOfPops = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")
        dataOfPopsInBs4 = self.getHtmlBs4(dataOfPops)

        popsInfo = []

        for pop in dataOfPopsInBs4.find_all('tr'):
            # pop info
            popRow = [singlePop.text.strip() for singlePop in pop.find_all("td")]
            popId, popName, resellerName, popLocation, mkIP, _, _, _, popContact, popStatus, _, popBalance, *_ = popRow

            # getting pop package
            self.getPage(f"/sub-package-permission/{popId}")
            sleep(2)

            packageTable = self.getHtmlBs4(self.web.find_element(
                By.XPATH, '//*[@id="dtProduct"]/tbody').get_attribute("innerHTML"))

            hasSubPackage = []
            for package in packageTable.find_all("tr"):
                if package.find("input").has_key("checked"):
                    _, packageId, packageName, packageRate, *_ = [
                        packageRow.text.strip() for packageRow in package.find_all("td")]

                    hasSubPackage.append({
                        "id": packageId,
                        "name": packageName,
                        "price": packageRate,
                    })

            popsInfo.append({
                "id": popId,
                "name": popName,
                "reseller": resellerName,
                "location": popLocation,
                "mkIp": mkIP,
                "contact": popContact,
                "status": popStatus,
                "balance": popBalance,
                "hasSubPackage": hasSubPackage
            })

        return popsInfo

    def getAllThePackage(self):
        self.getPage("/package")
        Select(self.web.find_element(By.XPATH, '//*[@id="datatbl_length"]/label/select')).select_by_visible_text("All")

        sleep(5)

        tableOfPackage = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")
        dataOfPackages = self.getHtmlBs4(tableOfPackage)

        allPackage = []
        for package in dataOfPackages.find_all("tr"):
            packageId, packageName, packageRate, packagePool, *_ = [pack.text.strip()
                                                                    for pack in package.find_all("td")]
            allPackage.append({
                "name": packageId,
                "name": packageName,
                "price": packageRate,
                "poolName": packagePool
            })

        return allPackage

    def getAllTheSubPackage(self):
        self.getPage("/sub-package")
        Select(self.web.find_element(By.XPATH, '//*[@id="datatbl_length"]/label/select')).select_by_visible_text("All")

        sleep(5)

        tableOfSubPackage = self.web.find_element(By.XPATH, '//*[@id="datatbl"]/tbody').get_attribute("innerHTML")
        dataOfSubPackages = self.getHtmlBs4(tableOfSubPackage)

        allTheSubPackage = []
        for package in dataOfSubPackages.find_all("tr"):
            packageId, packageName, packageRate, motherPackage, motherPackagePrice, * \
                _ = [pack.text.strip() for pack in package.find_all("td")]

            allTheSubPackage.append({
                "id": packageId,
                "name": packageName,
                "price": packageRate,
                "motherPackage": motherPackage,
                "motherPackagePrice": motherPackagePrice,
            })

        return allTheSubPackage


if __name__ == "__main__":
    w = SuperScrapper()
    print(json.dumps(w.getAllTheSubPackage(), indent=2))
