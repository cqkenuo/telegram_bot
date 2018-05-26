from database import connection_string, pyodbc, log, connector, is_windows
from random import SystemRandom
import hashlib


MAX_RAN_GEN = 9999999

insert_query = """INSERT INTO RegIDs (RegID) VALUES (%s)"""

create_if_not_exists_query = ("CREATE TABLE IF NOT EXISTS `RegIDs` ("
                              "ID INT AUTO_INCREMENT PRIMARY KEY,"
                              "RegID varchar(250),"
                              "taken bit DEFAULT 0 NOT NULL )")


def generate(count):

    cryptogen = SystemRandom()
    hash = None

    database = None
    if is_windows():
        database = connector.connect(**connection_string())
    else:
        database = pyodbc.connect(connection_string())

    # check_for_table(database)

    cursor = database.cursor()

    randValues = [[cryptogen.randrange(MAX_RAN_GEN) for j in range(2)] for i in range(count)]

    for x in range(0, count):
        hash = hashlib.sha512(str(str(randValues[x][0]) + str(randValues[x][0])).encode('utf-8'))
        cursor.execute(insert_query, (hash.hexdigest()))

    cursor.close()
    database.commit()


def check_for_table(database):
    cursor = database.cursor()

    try:
        cursor.execute(create_if_not_exists_query)
    except (pyodbc.DataError, pyodbc.ProgrammingError):
        log("insert()", "Truncated string or ProgrammingError")
        raise

    cursor.close()
    database.commit()


# Entry point
if __name__ == "__main__":
    generate(2000)
