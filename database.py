import pyodbc
import sys
from log import log
from mysql import connector

create_if_not_exists_query = \
    ("CREATE TABLE IF NOT EXISTS `Chats` ("
     "ChatID varchar(250) PRIMARY KEY,"
     "RegID varchar(250))")

insert_query = """INSERT INTO Chats (ChatID,RegID) VALUES (%s,%s)"""
exists_query = """SELECT 1 FROM RegIDs WHERE RegID=%s"""
user_exists_query = """SELECT 1 FROM Chats WHERE ChatID=%s"""
clashes_query = """SELECT 1 FROM Chats WHERE ChatID=%s AND RegID=%s"""

# warnings enable and disable
disable_warnings_query = "SET sql_notes = 0;"
enable_warnings_query = "SET sql_notes = 1;"

# MySQL connection string
connection_string_mysql_linux = ("DRIVER={MySQL ODBC 8.0 Driver};"
                                 "SERVER=127.0.0.1;"
                                 "DATABASE=test;"
                                 "PORT=3306;"
                                 "USER=test;PASSWORD=Test123Test!*;"
                                 "OPTION=3;")

connection_string_mysql_win = {
    'user': 'test',
    'password': 'Test123Test!*',
    'host': '127.0.0.1',
    'database': 'test',
    'raise_on_warnings': True,
    'use_pure': False,
}


def is_windows():
    return sys.platform.startswith('win')


def connection_string():
    if is_windows():
        return connection_string_mysql_win
    else:
        return connection_string_mysql_linux


class RegisterDB:

    def __init__(self):
        try:

            if is_windows():
                self.db = connector.connect(**connection_string_mysql_win)
            else:
                self.db = pyodbc.connect(connection_string_mysql_linux)

            self.cursor = None

            self.check_for_table()

        except pyodbc.Error as e:
            log('RegisterDB.__init__()', 'failed to open db')
            raise

    def check_for_table(self):
        self.cursor = self.db.cursor()

        # disable warnings
        self.cursor.execute(disable_warnings_query)

        try:
            self.cursor.execute(create_if_not_exists_query)
        except (pyodbc.DataError, pyodbc.ProgrammingError):
            log("insert()", "Truncated string or ProgrammingError")
            raise

        # Re-enable warnings
        self.cursor.execute(enable_warnings_query)

        # Close the cursor
        self.cursor.close()

        # Commit the transaction
        self.db.commit()

    def insert(self, chatid, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.insert()", "Inserting into table: "
            + str(chatid) + " " + str(uuid))

        values = (str(chatid), str(uuid),)

        try:
            self.cursor.execute(insert_query, values)
        except (pyodbc.DataError, pyodbc.IntegrityError) as d:
            log("RegisterDB.insert()", "Statement error")
            pass
        except:
            pass

        self.cursor.close()
        self.db.commit()

    def exists(self, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.exists()", "Checking if exists RegIDs in table: " + str(uuid))

        values = (str(uuid),)

        try:
            self.cursor.execute(exists_query, values)

            if self.cursor.fetchone():
                return True

        except pyodbc.DataError as d:
            log("RegisterDB.exists()", "Truncating string error")

        self.cursor.close()

        return False

    def user_exists(self, chatid):
        self.cursor = self.db.cursor()

        log("RegisterDB.user_exists()", "Checking if exists Chats in table: " + str(chatid))

        values = (str(chatid),)

        try:
            self.cursor.execute(user_exists_query, values)

            if self.cursor.fetchone():
                log("RegisterDB.user_exists()", "User exists")
                return True

        except pyodbc.DataError as d:
            log("RegisterDB.user_exists()", "Data error")

        self.cursor.close()

        return False

    def clashes(self, chatid, regid):
        self.cursor = self.db.cursor()

        log("RegisterDB.clashes()", "Checking if exists RegIDs in Chats table: "
            + str(chatid) + " " + str(regid))

        values = (str(chatid), str(regid), )

        try:
            self.cursor.execute(clashes_query, values)

            if self.cursor.fetchone():
                return True

        except pyodbc.DataError as d:
            log("RegisterDB.clashes()", "Data error")

        self.cursor.close()

        return False


if __name__ == "__main__":
    b = RegisterDB()
    b.insert('yes', 'no')

    print(str(b.user_exists('yes')))
