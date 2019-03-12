# the main file for now

import functools
import tkinter as tk  # May have to change this later to detect if tkinter is available

# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    """Class to manage window related actions

    """

    def __init__(self):
        self.master = tk.Toplevel(_master)
        self.master.bind('<Destroy>', self.on_close)  # hopefully fix closing
        tk.Canvas.__init__(self, self.master, width=500, height=500)

        # display the canvas on the window
        self.pack()
        self.autoflush = True

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)

        # TODO Implement ability to change window name

    def autoflush(func):
        # a decorator that refreshes the window once the decorated function is run - if autoflush is true
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            if args[0].autoflush:
                args[0].update()
            return value

        return wrapper_decorator

    @autoflush
    def on_close(self, *args):
        """Stub to manage the closing of the window

        Should be modifiable by the user
        """
        self.master.destroy()
        # TODO check if window is destroyed and assert an error if so

    @autoflush
    def set_bg(self, colour):
        """Changes the background colour to the colour specified

        :param colour: The colour to be changed to - accepts all tkinter colours
        :type colour: string
        """
        self.config(bg=colour)
        # TODO implement rgb colours / class


class Object:
    """Class to manage base level attributes and commands of all objects

    """

    # TODO fix weird glitch where some parts of the shape don't draw if updated too quickly (about 40+ fps)
    # TODO make a better move function
    # TODO maybe implement a transformation class (rotation, sizing)
    # noinspection PyShadowingNames
    def __init__(self, window):
        """
        :param window: window to bind the object to
        :type window: pk.Window
        """
        self.window = window
        self.id = None
        self.bbox_id = None

    # a stub for drawing - different for different shapes
    def _draw(self):
        pass  # overridden

    def draw(self, bbox=False):
        """Draws the shape to the current window

        :param bbox: Whether to draw the bounding box or not
        :type bbox: bool
        """
        self.id = self._draw()
        if bbox:
            self.bbox_id = self.get_bbox()

        _master.update()

    # stub for getting the bbox - defined in BBox
    def get_bbox(self):
        pass  # overridden


# noinspection PyCallByClass
class BBox(Object):
    """A bounding box class that provides methods and management of box shaped objects"""

    # TODO Add collision
    # noinspection PyShadowingNames
    def __init__(self, window, x, y, width, height):
        """

        :param window: The window the object is bound to
        :type window: pk.Window
        :param x: x coordinate of the object (from the top left corner)
        :type x: int/float
        :param y: y coordinate of the object (from the top left corner)
        :type y: int/float
        :param width: width of the object
        :type width: int/float
        :param height: height of the object
        :type height: int/float
        """
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.cx = self.x + (self.width / 2)
        self.cy = self.y + (self.height / 2)
        Object.__init__(self, window)

    # noinspection PyCallByClass
    def get_bbox(self):
        """Returns the bounding box of the object in green

        :return: Bounding box id
        :rtype: int
        """
        return tk.Canvas.create_rectangle(self.window, self.x, self.y, self.width, self.height, outline='green',
                                          width='2')


class Line(BBox):
    """Creates a straight line that starts from (x,y) and ends at width and height

    (thinking about this, what kind of line has width and height....)
    """

    # noinspection PyShadowingNames
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    # noinspection PyCallByClass
    def _draw(self):
        # tk uses x1 y1 x2 y2 notation, which is pretty gross
        # TODO probably use x1 y1 x2 y2 because it makes more sense (apparently)....
        return tk.Canvas.create_line(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Rectangle(BBox):
    """Creates a rectangle that starts from (x,y) and is width long and height high"""

    # noinspection PyShadowingNames
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    # noinspection PyCallByClass
    def _draw(self):
        return tk.Canvas.create_rectangle(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Circle(BBox):
    """Creates a circle using (x,y) as the center point, that spreads radius outwards"""

    # noinspection PyShadowingNames
    def __init__(self, window, x, y, radius):
        BBox.__init__(self, window, float(x) - radius, float(y) - radius, float(x) + radius, float(y) + radius)

    # noinspection PyCallByClass
    def _draw(self):
        # noinspection PyCallByClass
        return tk.Canvas.create_oval(self.window, self.x, self.y, self.width, self.height)


class Oval(BBox):
    """Creates an oval based on a defined box, which starts at (x,y) and is width long and height high"""

    # noinspection PyShadowingNames
    def __init__(self, window, x, y, width, height):
        BBox.__init__(self, window, x, y, width, height)

    # noinspection PyCallByClass
    def _draw(self):
        return tk.Canvas.create_oval(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Text(Object):
    """Creates a text object, centered on (x,y)"""
    def __init__(self, window, x, y, text):
        self.x, self.y = x, y
        self.text = text
        Object.__init__(self, window)

    def _draw(self):
        return self.window.create_text(self.x, self.y, text=self.text)


class Entry(Object):
    """Creates an entry box, which text and numbers can be entered into"""
    def __init__(self, window, x, y, width, placeholder=''):
        self.x, self.y = x, y
        self.width = width
        self.text = tk.StringVar(_master)
        self.text.set(placeholder)
        Object.__init__(self, window)
        self.entry = None

    def _draw(self):
        frame = tk.Frame(self.window.master)
        self.entry = tk.Entry(frame, width=self.width, textvariable=self.text)
        self.entry.pack()
        return self.window.create_window(self.x, self.y, window=frame)

# TODO Implement Images
# TODO Implement events (key handling, mouse handling, etc)
# TODO Implement buttons and entries (embedded widgets)
# TODO Implement Menubars (File, Edit, etc)


# This is for testing
if __name__ == '__main__':
    window = Window()
    # window.set_bg('red')
    # noinspection SpellCheckingInspection
    myline = Line(window, 100, 100, 100, 0)
    myline.draw(bbox=True)
    mycircle = Circle(window, 100, 100, 50)
    mycircle.draw(bbox=True)
    myrect = Rectangle(window, 0, 0, 200, 200)
    myrect.draw()
    myoval = Oval(window, 0, 50, 200, 100)
    myoval.draw()
    mytext = Text(window, 50, 50, 'YEET')
    mytext.draw()
    myentry = Entry(window, 100, 100, 20)
    myentry.draw()

    while True:
        window.move(myoval.id, 1, 1)
        window.move(mycircle.id, 1, 1)
        window.update_idletasks()
        window.update()
        window.after(15)
