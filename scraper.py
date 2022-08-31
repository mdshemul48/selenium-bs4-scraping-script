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


class Reseller(Scraper):
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

    def getResellerAllClient(self):
        self.getPage("/customer-search-report")
        Select(self.web.find_element(By.XPATH, '//*[@id="reseller_id"]')).select_by_visible_text(self.resellerName)

        self.web.find_element(By.XPATH, '//*[@id="btnSearch"]').click()

        sleep(5)
        tableOfClients = self.web.find_element(
            By.XPATH, '//*[@id="search-result"]/div/div/div[2]/table/tbody').get_attribute("innerHTML")

        allClientRows = self.getHtmlBs4(tableOfClients)
        allTheResellerClient = []
        for clientRow in allClientRows.find_all("tr"):
            if clientRow.has_key("align"):
                continue
            user_detail = clientRow.find_all("td")
            user_id: str = user_detail[1].getText()

            self.getPage(f"/mac-customer/{user_id}")

            table_element = self.web.find_elements(
                By.XPATH, '//*[@id="container"]/div/div/div/div/div[2]/table'
            )[0]

            table_html = table_element.get_attribute("innerHTML")
            table_soup = self.getHtmlBs4(table_html)

            allTheFiledOfClient = table_soup.find_all("tr")
            user_data = {}
            for filed in allTheFiledOfClient:
                key = filed.find("th").getText()
                value = filed.find("td").getText()
                user_data[key] = value

            address = user_data["Address"].split(",")
            flat_no = address[0]
            building = address[1]
            road = address[2]
            block = address[3]
            user_data["Address"] = {
                "flat_no": flat_no,
                "building": building,
                "road": road,
                "block": block,
            }
            allTheResellerClient.append(user_data)

        return allTheResellerClient


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
            # sleep(2)

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
            # sleep(2)

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
    superScraper = SuperScrapper()

    allMk = open("dist/allMikroTik.json", "w")
    allMk.write(json.dumps(superScraper.getAllTheMikroTik(), indent=2))
    allMk.close()
    print("done")

    allTheReseller = open("dist/allTheReseller.json", "w")
    allTheReseller.write(json.dumps(superScraper.getAllTheReseller(), indent=2))
    allTheReseller.close()

    print("done")

    allThePop = open("dist/allThePop.json", "w")
    allThePop.write(json.dumps(superScraper.getAllThePop(), indent=2))
    allThePop.close()

    print("done")

    allTHePackage = open("dist/allThePackage.json", "w")
    allTHePackage.write(json.dumps(superScraper.getAllThePackage(), indent=2))
    allTHePackage.close()

    print("done")

    allTheSubPackage = open("dist/allTheSubPackage", 'w')
    allTheSubPackage.write(json.dumps(superScraper.getAllThePackage(), indent=2))
    allTheSubPackage.close()

    print("done")

    w = Reseller("ASKONA")
    resellerClients = open("dist/allTheClient.json", "w")
    resellerClients.write(json.dumps(w.getResellerAllClient(), indent=2))
    resellerClients.close()

    print("done")
