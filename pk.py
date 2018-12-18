# the main file for now

import tkinter as tk  # May have to change this later to detect if tkinter is available

import sys

# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it as it is used more


class Window(tk.Canvas):
    # Class to manage the main window

    def __init__(self):
        self.master = tk.Toplevel(_master)
        tk.Canvas.__init__(self, self.master, width=500, height=500)

        # display the canvas on the window
        self.pack()

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)

    # stub to manage the window closing - should be modifiable by the user
    def on_close(self):
        self.master.destroy()
        sys.exit()  # extra precaution


if __name__ == '__main__':
    window = Window()

    while True:
        window.update()
