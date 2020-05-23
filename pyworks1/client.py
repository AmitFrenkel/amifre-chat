from database import Database
from home_window import HomeWindow
from loading_screen import LoadingScreen
import ctypes
import varibles
import socket


# The main function of the project.
def main(ip):
    varibles.logout = False
    d = Database(ip)
    varibles.Host = str(ip)
    HomeWindow(d.get_my_database(), d.get_my_cursor())
    if varibles.logout:
        main(ip)


if __name__ == '__main__':
    # replacing the python icon in the task bar with tkinter icon
    myappid = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    LoadingScreen()
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 37020))
    data, addr = client.recvfrom(1024)
    client.close()
    main(addr[0])
