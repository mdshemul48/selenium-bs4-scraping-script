import json
from envInfo import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER
from scraper import SuperScraper, Reseller
from Db import DB
import json
import datetime
from util import find


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

    # w = Reseller("ASKONA")
    # resellerClients = open("dist/allTheClient.json", "w")
    # resellerClients.write(json.dumps(w.getResellerAllClient(), indent=2))
    # resellerClients.close()

    # print("done")


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

        self.AllMikrotikInfo = AllMikrotikInfo
        return AllMikrotikInfo

    def insertAllThePackage(self, fileLocation: str):
        allPackageInfo = self.__getJsonData(fileLocation)

        for package in allPackageInfo:
            _, packageName, packagePrice, packagePoolName = package.values()
            insertedId = self.db.table("packages").insert({
                "package_name": packageName,
                "package_rate": packagePrice,
                "pool_name": packagePoolName
            })
            package["insertedId"] = insertedId

        self.allPackageInfo = allPackageInfo
        return allPackageInfo


def main():
    # scrapData()
    sam = Sam()
    allMikrotik = sam.insertAllMkInfo("dist/allMikroTik.json")
    allThePackages = sam.insertAllThePackage("dist/allThePackage.json")

    resellers = json.loads(open("dist/allTheReseller.json", "r").read())
    pops = json.loads(open("dist/allThePop.json", "r").read())
    subPackages = json.loads(open("dist/allTheSubPackage.json", "r").read())

    db = DB(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)

    for reseller in resellers:
        resellerHasPackage = reseller['hasPackage']
        resellerHasSubPackage = reseller['hasSubPackage']

        # adding reseller
        packageIds = ", ".join([str(find(allThePackages, "id", package["id"])["insertedId"])
                                for package in resellerHasPackage])

        resellerInsertedId = db.table("resellers").insert({
            "name": reseller["name"],
            "address": reseller["address"],
            "contact": reseller["contact"],
            "remark": reseller["remarks"],
            "package_list": packageIds
        })

        # adding reseller SubPackages
        for subPackage in resellerHasSubPackage:
            subPackageWithMotherPackage = find(subPackages, "name", subPackage['name'])
            motherPackage = find(allThePackages, "name", subPackageWithMotherPackage['motherPackage'])

            subPackageInsertedId = db.table("sub_packages").insert({
                "reseller_id": resellerInsertedId,
                "package_id": motherPackage['insertedId'],
                "name": subPackage['name'],
                "rate": subPackage["price"]
            })
            subPackageWithMotherPackage["insertedId"] = subPackageInsertedId

        # adding pops
        resellerPops = list(filter(lambda pop: pop['reseller'] == reseller['name'], pops))
        for pop in resellerPops:
            hasSubPackage = pop['hasSubPackage']

            # adding pop subPackage
            subPackageIds = []
            for subPackage in hasSubPackage:
                subPackageWithMotherPackage = find(subPackages, "name", subPackage['name'])
                subPackageIds.append(str(subPackageWithMotherPackage["insertedId"]))

            subPackageIds = ", ".join(subPackageIds)
            pop["insertedId"] = db.table("pops").insert({
                "popname": pop["name"],
                "reseller_id": resellerInsertedId,
                "pop_location": pop["location"],
                "pop_contact": pop["contact"],
                "nas_id": find(allMikrotik, "ip", pop["mkIp"])['insertedId'],
                "sub_package_list": subPackageIds
            })

        # insert all the Client
        allTheClients = json.load(open("dist/{}.json".format(reseller["name"])))

        for client in allTheClients:

            status = "disable"
            if client['Enable State'] == "Enable":
                status = "active"

            packageId = find(allThePackages, "id", client["Package"].split(" ")[0])['insertedId']

            subResellerId = ""
            if client["Sub Package"]:
                subResellerId = find(subPackages, "id", client["Sub Package"])["insertedId"]

            popId = str(find(pops, "id", client["POP"].split(" ")[0])["insertedId"])

            db.table("clients").insert({
                "pop_id": popId,
                "billing_cycle": client["Billing Cycle"],
                "package_id": packageId,
                "userid": client['Customer Username'],
                "password": client['Password'],
                "created_by": 1,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "required_cable": client["Cable Meter"],
                "clients_status": status,
                "sub_package_id": subResellerId
            })

            break

        break


if __name__ == "__main__":
    main()
