import mysql.connector


# The following class creates connection between the user and the database.
class Database:
    def __init__(self, ip):
        self.__my_database = mysql.connector.connect(
            host=ip,
            user='root',
            password='root',
            database='dbchat'
        )
        self.__my_database.autocommit = True
        self.__my_cursor = self.__my_database.cursor()

    # These are the accessors of the class:
    def get_my_database(self):
        return self.__my_database

    def get_my_cursor(self):
        return self.__my_cursor
