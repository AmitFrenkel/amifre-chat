from tkinter import *
from chat import Chat
from Notification import Notification
from varibles import *


# The following class creates a login page.
class Login:
    # THe constructor function of the class.
    def __init__(self, home_window, my_database, my_cursor):
        self.__start = home_window
        self.__start.withdraw()
        self.__my_database = my_database
        self.__my_cursor = my_cursor
        self.__client_name = ''
        self.__window = self.create_window()
        self.__name, self.__password, self.__password_button = self.create_window_objects()
        self.__window.protocol("WM_DELETE_WINDOW", self.alt_f4)
        self.__window.mainloop()

    # The following function creates the login window objects.
    def create_window_objects(self):
        title = Label(self.__window, text='Login', bg='#025E73', fg='orange', font=('Segoe UI', 25))
        title.place(x=150, y=20)
        vcmd = (self.__window.register(validate), '%S')
        member_name = self.username(vcmd)
        password, show_password = self.user_password(vcmd)
        submit_button = Button(self.__window, text='Submit', width=20, bg='green', bd=7, fg='#fbf168', relief=GROOVE,
                               font=('Segoe UI', 10), cursor='hand2', command=lambda: self.start_chat())
        submit_button.place(x=120, y=300)
        return member_name, password, show_password

    # The following function creates the password field.
    def user_password(self, vcmd):
        member_password = Label(self.__window, text='Password', bg='#025E73', fg='orange', font=('Segoe UI', 12))
        member_password.place(x=20, y=140)
        password = Entry(self.__window, width=25, bg='green', fg='orange', show='*',
                         font=('Segoe UI', 12), insertbackground='orange', validate='key', validatecommand=vcmd)
        password.place(x=140, y=140)
        show_password = Button(self.__window, text='Show Password', width=15, bg='green', bd=7, fg='#fbf168',
                               relief=GROOVE, font=('Segoe UI', 8), cursor='hand2',
                               command=lambda: self.show_password())
        show_password.place(x=175, y=180)
        return password, show_password

    # The following function creates the username field.
    def username(self, vcmd):
        l1 = Label(self.__window, text='Member Name', bg='#025E73', fg='orange', font=('Segoe UI', 12))
        l1.place(x=20, y=100)
        member_name = Entry(self.__window, width=25, bg='green', fg='orange',
                            font=('Segoe UI', 12), insertbackground='orange', validate='key', validatecommand=vcmd)
        member_name.place(x=140, y=100)
        return member_name

    # The following function creates the tkinter window itself.
    def create_window(self):
        window = Tk()
        window.geometry(str(round(window.winfo_screenwidth() / 3.78)) + 'x' + str(
            round(window.winfo_screenheight() / 1.65)))
        window.config(bg='#025E73')
        window.title('Sign In')
        window.iconbitmap('icon.ico')
        window.bind('<Return>', lambda x: self.start_chat())
        window.resizable(height=False, width=False)
        return window

    # The following function makes the show password button works.
    def show_password(self):
        if self.__password_button['text'] == 'Show Password':
            self.__password.config(show='')
            self.__password_button.config(text='Hide Password')
        else:
            self.__password.config(show='*')
            self.__password_button.config(text='Show Password')

    # The following function checks that the username and the password are existing the chat database
    # and not already that user is not already connected.
    def start_chat(self):
        self.__client_name = self.__name.get().strip('\n').strip(' ')
        client_pass = self.__password.get().strip('\n').strip(' ')
        self.__my_cursor.execute("SELECT * FROM users WHERE name=%s AND Password=%s",
                                 (self.__client_name, client_pass))
        msg = self.__my_cursor.fetchone()
        if client_pass is not None and self.__client_name is not None:
            if not msg:
                Notification('the user doesn\'t exist').start()
                return
            self.__my_cursor.execute("SELECT connected FROM users WHERE name=%s AND Password=%s",
                                     (self.__client_name, client_pass))
            msg = self.__my_cursor.fetchone()
            if msg[0] == 'True':
                Notification('the user already connected to the chat').start()
                return
            else:
                sqlf = "UPDATE users SET connected='True' WHERE name=%s AND Password=%s"
                self.__my_cursor.execute(sqlf, (self.__client_name, client_pass))
                self.__my_database.commit()
                name_len = len(self.__client_name)
                self.__client_name = str(name_len) + self.__client_name
            try:
                Chat(Host, Port, self.__client_name, self.__window, self.__start)
            except:
                Notification('The server is currently unavailable').start()
                sql = "UPDATE users SET connected='False' WHERE name=%s "
                self.__my_cursor.execute(sql, (self.__client_name[1:],))
                self.__my_database.commit()

    # The following function destroy the window.
    def alt_f4(self):
        self.__start.deiconify()
        self.__window.destroy()


#  The following function checks that the is validated.
def validate(char):
    try:
        if char.isalpha() or char.isdigit() or ord(char) == 8:
            return True
        else:
            return False
    except:
        return False
