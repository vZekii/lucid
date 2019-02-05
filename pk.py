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

    # sets the background colour of the window
    @autoflush
    def setBg(self, colour):
        self.config(bg=colour)


class Object:
    def __init__(self):
        self.id = None

    def draw(self):
        # add it to window items
        self.id = self._draw()
        _master.update()

    def _draw(self):
        pass # override this


class Line(Object):
    def __init__(self, window, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.window = window
        Object.__init__(self)

    def _draw(self):
        # draw line
        # tk uses x1 y1 x2 y2 notation, which is pretty gross
        return tk.Canvas.create_line(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Rectangle(Object):
    def __init__(self, window, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.window = window
        Object.__init__(self)

    def _draw(self):
        return tk.Canvas.create_rectangle(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Circle(Object):
    def __init__(self, window, x, y, radius):
        self.x1 = float(x) - radius
        self.y1 = float(y) - radius
        self.x2 = float(x) + radius
        self.y2 = float(y) + radius
        self.window = window
        Object.__init__(self)

    def _draw(self):
        return tk.Canvas.create_oval(self.window, self.x1, self.y1, self.x2, self.y2)


class Oval(Object):
    def __init__(self, window, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.window = window
        # TODO redefining all the attributes for BBox related objects is redundant - make a BBox class
        Object.__init__(self)

    def _draw(self):
        return tk.Canvas.create_oval(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


if __name__ == '__main__':
    window = Window()
    window.setBg('red')
    myline = Line(window, 100, 100, 100, 0)
    myline.draw()
    mycircle = Circle(window, 100, 100, 100)
    mycircle.draw()
    myrect = Rectangle(window, 0, 0, 200, 200)
    myrect.draw()
    myoval = Oval(window, 0, 50, 200, 100)
    myoval.draw()

    while True:
        window.update()
