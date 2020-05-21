from database import Database
from home_window import HomeWindow
from loading_screen import LoadingScreen
import ctypes
import varibles


# The main function of the project.
def main():
    varibles.logout = False
    d = Database()
    HomeWindow(d.get_my_database(), d.get_my_cursor())
    if varibles.logout:
        main()


if __name__ == '__main__':
    # replacing the python icon in the task bar with tkinter icon
    myappid = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    LoadingScreen()
    main()
