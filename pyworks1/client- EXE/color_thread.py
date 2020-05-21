import threading
from database import Database


# The following classes validating that the main chat and private chats colors are matching to the colors that
# registered in the database.


class ColorThread(threading.Thread):
    def __init__(self, window, label1, label2, label3, button1, button2, button3, button4, label4, user):
        super(ColorThread, self).__init__()
        self.daemon = True
        self.__d = Database()
        self.__user = user
        self.__window = window
        self.__label1 = label1
        self.__label2 = label2
        self.__label3 = label3
        self.__button1 = button1
        self.__button2 = button2
        self.__button3 = button3
        self.__button4 = button4
        self.__label4 = label4

    def run(self):
        while True:
            try:
                self.__button1.config(bg=self.color('input_background_color'), fg=self.color('input_font_color'))
                self.__button2.config(bg=self.color('input_background_color'), fg=self.color('input_font_color'))
                self.__window.config(bg=self.color('text_background_color'))
                self.__label1.config(fg=self.color('text_font_color'), bg=self.color('text_background_color'))
                self.__button3.config(bg=self.color('input_background_color'), fg=self.color('input_font_color'))
                self.__label2.config(bg=self.color('text_background_color'))
                self.__label3.config(bg=self.color('text_background_color'))
                self.__label4.config(bg=self.color('text_background_color'))
                self.__button4.config(bg=self.color('input_background_color'), fg=self.color('input_font_color'))
            except:
                pass

    def color(self, color):
        self.__d.get_my_cursor().execute("SELECT " + color + " FROM users WHERE name=%s ", (self.__user,))
        return self.__d.get_my_cursor().fetchone()[0]


class ColorThreadPrivate(threading.Thread):
    def __init__(self, window, txt, entry, client_name):
        super(ColorThreadPrivate, self).__init__()
        self.__d = Database()
        self.__user = client_name
        self.__window = window
        self.__txt = txt
        self.__entry = entry
        self.__client_name = client_name

    def run(self):
        while True:
            try:
                self.__window.config(bg=self.color('root_background_color'))
                self.__txt.config(fg=self.color('text_font_color'), bg=self.color('text_background_color'))
                self.__entry.config(bg=self.color('input_background_color'), fg=self.color('input_font_color'))
            except:
                pass

    def color(self, color):
        self.__d.get_my_cursor().execute("SELECT " + color + " FROM users WHERE name=%s ", (self.__user,))
        return self.__d.get_my_cursor().fetchone()[0]
