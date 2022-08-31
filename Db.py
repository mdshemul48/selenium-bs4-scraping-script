import mysql.connector


class DB:
    def __init__(self, host, username, password, database) -> None:
        self.db = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )

    def table(self, tableName):
        self.tableName = tableName
        return self

    def insert(self, tableData: dict):
        myCursor = self.db.cursor()

        keys = list(tableData.keys())
        values = list(tableData.values())
        sqlKeys = ", ".join(keys)
        sqlValueSet = ", ".join(["%s" for _ in range(len(keys))])

        sql = f"INSERT INTO {self.tableName} ({sqlKeys}) VALUES ({sqlValueSet})"

        myCursor.execute(sql, values)

        self.db.commit()
        myCursor.close()
        return myCursor.lastrowid


if __name__ == "__main__":
    db = DB("127.0.0.1", "root", "", "radius-circle")
    print(db.table("nas").insert({
        "nasname": "192.168.0.1",
        "shortname": "thisIs",
        "type": "others"
    }))
