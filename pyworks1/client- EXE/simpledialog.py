from tkinter import simpledialog


# The following class inherit from the simpledialog widget of tkinter and creates the window with the app's icon.
class StringDialog(simpledialog._QueryString):
    def body(self, main):
        super().body(main)
        self.iconbitmap('icon.ico')


# The following function creates a simpledialog window and returns the input.
def ask_string(title, prompt, **kargs):
    d = StringDialog(title, prompt, **kargs)
    return d.result
