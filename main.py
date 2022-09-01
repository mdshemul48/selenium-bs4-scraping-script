import json
from envInfo import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER
from scraper import SuperScraper, Reseller
from Db import DB
import json


def scrapData():
    superScraper = SuperScraper()

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

    allTheSubPackage = open("dist/allTheSubPackage.json", 'w')
    allTheSubPackage.write(json.dumps(superScraper.getAllTheSubPackage(), indent=2))
    allTheSubPackage.close()

    print("done")

    w = Reseller("ASKONA")
    resellerClients = open("dist/allTheClient.json", "w")
    resellerClients.write(json.dumps(w.getResellerAllClient(), indent=2))
    resellerClients.close()

    print("done")


class Sam:
    def __init__(self) -> None:
        self.db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)

    def __getJsonData(self, fileLocation: str):
        file = open(fileLocation, "r")
        return json.load(file)

    def insertAllMkInfo(self, fileLocation: str):
        AllMikrotikInfo = self.__getJsonData(fileLocation)

        for mikrotik in AllMikrotikInfo:
            _, mkName, mkIp, mkSecret, mkType,  mkDescription = mikrotik.values()
            insertedId = self.db.table("nas").insert({
                "nasname": mkIp,
                "shortname": mkName,
                "type": mkType,
                "secret": mkSecret,
                "description": mkDescription
            })
            mikrotik["insertedId"] = insertedId

        return AllMikrotikInfo


def main():
    # scrapData()
    sam = Sam()
    print(sam.insertAllMkInfo("dist/allMikroTik.json"))


if __name__ == "__main__":
    main()
