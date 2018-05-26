import pyodbc
import sys
from log import log
from mysql import connector

create_if_not_exists_query = \
    ("CREATE TABLE IF NOT EXISTS `Chats` ("
     "ChatID varchar(250) PRIMARY KEY,"
     "RegID varchar(250))")

insert_query = """INSERT INTO Chats (ChatID,RegID) VALUES (?,?)"""
exists_query = """"SELECT ChatID FROM RegIDs WHERE ChatID = ? AND RegID = ?"""

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
                self.db = connector.connect(connection_string_mysql_win)
            else:
                self.db = pyodbc.connect(connection_string_mysql_linux)

            self.cursor = None

            self.check_for_table()

        except pyodbc.Error as e:
            log('RegisterDB.__init__()', 'failed to open db')
            raise

    def check_for_table(self):
        self.cursor = self.db.cursor()

        try:
            self.cursor.execute(create_if_not_exists_query)
        except (pyodbc.DataError, pyodbc.ProgrammingError):
            log("insert()", "Truncated string or ProgrammingError")
            raise

        # Close the cursor
        self.cursor.close()

        # Commit the transaction
        self.db.commit()

    def insert(self, chatid, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.insert()", "Inserting into table: "
            + str(chatid) + " " + str(uuid))

        values = (chatid, uuid)

        try:
            self.cursor.execute(insert_query, values)
        except (pyodbc.DataError, pyodbc.IntegrityError) as d:
            log("RegisterDB.insert()", "Statement error")
            pass

        self.cursor.close()
        self.db.commit()

    def exists(self, chatid, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.exists()", "Checking if exists in table: "
            + str(chatid) + " " + str(uuid))

        values = (chatid, uuid)

        try:
            self.cursor.execute(exists_query, values)

            if self.cursor.fetchone():
                return True

        except pyodbc.DataError as d:
            log("RegisterDB.insert()", "Truncating string error")

        self.cursor.close()

        return False


if __name__ == "__main__":
    b = RegisterDB()
    b.insert('yes', 'no')

    print(str(b.exists('yes', 'no', )))
