import threading
from database import Database


#  The following class inherit from the threading and checks if the user is manager.
class ManagerThread(threading.Thread):
    def __init__(self, name):
        super(ManagerThread, self).__init__()
        self.__d = Database()
        self.__name = name

    def run(self):
        self.__d.get_my_cursor().execute("UPDATE users SET admin='True' WHERE name=%s ", (self.__name,))
        self.__d.get_my_database().commit()
