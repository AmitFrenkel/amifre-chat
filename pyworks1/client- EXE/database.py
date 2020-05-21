import mysql.connector


# The following class creates connection between the user and the database.
class Database:
    def __init__(self):
        self.__my_database = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='am1103',
            database='dbchat'
        )
        self.__my_database.autocommit = True
        self.__my_cursor = self.__my_database.cursor()

    # This are the accessors of the class:
    def get_my_database(self):
        return self.__my_database

    def get_my_cursor(self):
        return self.__my_cursor
