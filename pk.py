# the main file for now

import tkinter as tk  # May have to change this later to detect if tkinter is available

import sys
import functools
from helpers import debug  # for debugging functions

# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    # Class to manage the main window

    def __init__(self):
        self.master = tk.Toplevel(_master)
        tk.Canvas.__init__(self, self.master, width=500, height=500)

        # display the canvas on the window
        self.pack()
        self.autoflush = True

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)

    # Autoflush allows for the window to be updated automatically after a function call
    def autoflush(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            if args[0].autoflush:
                args[0].update()
            return value

        return wrapper_decorator

    # stub to manage the window closing - should be modifiable by the user
    @autoflush
    def on_close(self):
        self.master.destroy()
        # TODO check if window is destroyed and assert an error if so


if __name__ == '__main__':
    window = Window()

    while True:
        window.update()
