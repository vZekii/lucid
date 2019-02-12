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
    def __init__(self, window):
        self.window = window
        self.id = None
        self.bbox_id = None

    def _draw(self):
        pass # override this

    def draw(self, bbox=False):
        # draw the shape
        self.id = self._draw()
        if bbox:
            self.bbox_id = self.get_bbox()

        _master.update()

    def draw_bbox(self, value):
        if isinstance(value, bool):
            self.bbox = value

    def get_bbox(self):
        pass # override


class BBox(Object):
    # Bounding box for box-shaped objects
    def __init__(self, window, x, y, width, height):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.cx = self.x + (self.width / 2)
        self.cy = self.y + (self.height / 2)
        Object.__init__(self, window)

    def get_bbox(self):
        return tk.Canvas.create_rectangle(self.window, self.x, self.y, self.width, self.height, outline='green', width='2')


class Line(BBox):
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    def _draw(self):
        # tk uses x1 y1 x2 y2 notation, which is pretty gross
        return tk.Canvas.create_line(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Rectangle(BBox):
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    def _draw(self):
        return tk.Canvas.create_rectangle(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Circle(BBox):
    def __init__(self, window, x, y, radius):
        BBox.__init__(self, window, float(x) - radius, float(y) - radius, float(x) + radius, float(y) + radius)

    def _draw(self):
        return tk.Canvas.create_oval(self.window, self.x, self.y, self.width, self.height)


class Oval(BBox):
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    def _draw(self):
        return tk.Canvas.create_oval(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


if __name__ == '__main__':
    window = Window()
    #window.setBg('red')
    myline = Line(window, 100, 100, 100, 0)
    myline.draw(bbox=True)
    mycircle = Circle(window, 100, 100, 50)
    mycircle.draw(bbox=True)
    myrect = Rectangle(window, 0, 0, 200, 200)
    myrect.draw()
    myoval = Oval(window, 0, 50, 200, 100)
    myoval.draw()

    while True:
        window.move(myoval.id, 1, 1)
        window.move(mycircle.id, 1, 1)
        window.update_idletasks()
        window.update()
        window.after(10)
