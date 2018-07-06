# import pyodbc
import sys

from log import log, config
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

# # MySQL connection string
# connection_string_mysql_linux = ("DRIVER={MySQL ODBC 5.1 Driver};"
#                                  + "SERVER=" + config['db_host'] + ";"
#                                  + "DATABASE=" + config['db_name'] + ";"
#                                  + "PORT=" + config['db_port'] + ";"
#                                  + "USER=" + config['db_user'] + ";"
#                                  + "PASSWORD=" + config['db_pass'] + ";"
#                                  + "OPTION=3;")

connection_string_mysql = {
    'user': config['db_user'],
    'password': config['db_pass'],
    'host': config['db_host'],
    'database': config['db_name'],
    'raise_on_warnings': True,
    'use_pure': False,
}


def is_windows():
    return sys.platform.startswith('win')


class RegisterDB:

    def __init__(self):
        try:

            self.db = connector.connect(**connection_string_mysql)

            self.cursor = None
            self.check_for_table()

        except connector.Error as e:
            log('RegisterDB.__init__()', 'failed to open db', True)
            raise

    def check_for_table(self):
        self.cursor = self.db.cursor()

        # disable warnings
        self.cursor.execute(disable_warnings_query)

        try:
            self.cursor.execute(create_if_not_exists_query)
        except connector.Error:
            log("insert()", "Truncated string or ProgrammingError", True)
            raise

        # Re-enable warnings
        self.cursor.execute(enable_warnings_query)

        # Close the cursor
        self.cursor.close()

        # Commit the transaction
        self.db.commit()

    def insert(self, chatid, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.insert()", "Inserting user into table")
        #     + str(chatid) + " " + str(uuid))

        values = (str(chatid), str(uuid),)

        try:
            self.cursor.execute(insert_query, values)
        except connector.Error as d:
            log("RegisterDB.insert()", "Statement error", True)
            pass
        except:
            pass

        self.cursor.close()
        self.db.commit()

    def exists(self, uuid):
        self.cursor = self.db.cursor()

        log("RegisterDB.exists()", "Checking if user exists RegIDs in table")  #: " + str(uuid))

        values = (str(uuid),)

        try:
            self.cursor.execute(exists_query, values)

            if self.cursor.fetchone():
                return True

        except connector.Error as d:
            log("RegisterDB.exists()", "Truncating string error", True)

        self.cursor.close()
        self.db.commit()

        return False

    def user_exists(self, chatid):
        self.cursor = self.db.cursor()

        # private information in the log
        # log("RegisterDB.user_exists()", "Checking if exists Chats in table: " + str(chatid))

        values = (str(chatid),)

        try:
            self.cursor.execute(user_exists_query, values)

            if self.cursor.fetchone():
                log("RegisterDB.user_exists()", "User exists")
                return True

        except connector.Error as d:
            log("RegisterDB.user_exists()", "Data error", True)
        except:
            log('RegisterDB.user_exists()', 'Unspecified exception caught', True)
            pass

        self.cursor.close()
        self.db.commit()

        return False

    def clashes(self, chatid, regid):
        self.cursor = self.db.cursor()

        log("RegisterDB.clashes()", "Checking if exists RegIDs in Chats table")

        values = (str(chatid), str(regid),)

        try:
            self.cursor.execute(clashes_query, values)

            if self.cursor.fetchone():
                return True

        except connector.Error as d:
            log("RegisterDB.clashes()", "Data error", True)

        self.cursor.close()
        self.db.commit()
        return False


if __name__ == "__main__":
    b = RegisterDB()
    b.insert('yes', 'no')

    print(str(b.user_exists('yes')))
