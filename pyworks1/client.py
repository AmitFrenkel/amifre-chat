from database import Database
from home_window import HomeWindow
from loading_screen import LoadingScreen
import ctypes
import varibles
import socket
import select
import time
import tkinter.messagebox

# The main function of the project.
def main(ip):
    varibles.logout = False
    print(ip)
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
    timer = 0
    addr = ''
    while timer < 10:
        timer += 1
        time.sleep(1)
        print(timer)
        r, w, x = select.select([client], [], [], 0.00001)
        if client in r:
            data, addr = client.recvfrom(1024)
            main(addr[0])
            break
    client.close()
    if timer == 10:
        tkinter.messagebox.showinfo('Error', 'The server is currently offline')
