def find(listOfElement, key, value):

    try:
        return [x for x in listOfElement if x[key] == value][0]
    except:
        print(key, value, listOfElement)
        exit()
