# the main file for now

import tkinter as tk  # May have to change this later to detect if tkinter is available
import math

# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    """Class to manage window related actions

    """

    def __init__(self, width=500, height=500):
        self.master = tk.Toplevel(_master)
        self.master.bind('<Destroy>', self.on_close)  # hopefully fix closing
        self.master.resizable(0, 0)
        tk.Canvas.__init__(self, self.master, width=width, height=height)

        # display the canvas on the window
        self.pack()
        self.autoflush = True

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)

        # TODO Implement ability to change window name

    def autoflush(func):
        # a decorator that refreshes the window once the decorated function is run - if autoflush is true
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
    # ^^^ I'm assuming its to do with the refresh rate of the monitor
    # TODO make a better move function
    # TODO maybe implement a transformation class (rotation, sizing)
    def __init__(self, window, x, y, width, height):
        """
        :param window: window to bind the object to
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
        self.window = window
        self.id = None  # assigned on creation

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Coordinates for all points of the shape
        self.points = self.generate_points()

        # options for customisation
        self.options = {'outline': 'black',
                        'fill': '',  # Empty string is transparent
                        'smooth': 'false'}

        self.rotation = 0  # recorded in degrees
        self.precision = 4  # number of points that make up the shape

    def generate_points(self):
        # Converts xywh to (x1 y1) (x2 y2) ... (tk polygon format)
        return [(self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)]

    def convert_points(self):
        # converts points from x1 y1 x2 y2 to (x1, y1) (x2, y2) ...
        self.points = [(self.points[i], self.points[i + 1]) for i in range(0, len(self.points), 2)]

    def rotate(self, angle):
        self.rotation += angle
        if self.rotation >= 360: self.rotation -= 360
        rotation = self.rotation * math.pi / 180.0

        # major and minor axes
        a = self.width / 2
        b = self.height / 2

        # center
        xc = self.x + a
        yc = self.y + b

        point_list = []

        # create the oval as a list of points
        for i in range(self.precision):
            # Calculate the angle for this step
            # 360 degrees == 2 pi radians
            theta = (math.pi * 2) * (float(i) / self.precision)

            x1 = a * math.cos(theta)
            y1 = b * math.sin(theta)

            # rotate x, y
            x = (x1 * math.cos(rotation)) + (y1 * math.sin(rotation))
            y = (y1 * math.cos(rotation)) - (x1 * math.sin(rotation))

            point_list.append(round(x + xc))
            point_list.append(round(y + yc))

        self.points = point_list

        if self.id is not None:
            self.window.coords(self.id, *self.points)

        self.convert_points()

    # a stub for drawing - different for different shapes
    def _draw(self): return 0  # overridden

    def draw(self):
        """Draws the shape to the current window
        """
        self.id = self._draw()
        _master.update()

    def draw_points(self):
        # debug function that shows points of object as red and border box as green
        tk.Canvas.create_rectangle(self.window, self.x, self.y,
                                   self.x + self.width, self.y + self.height, outline='green', width='2')
        for x, y in self.points:
            tk.Canvas.create_line(self.window, x, y, x+1, y+1, width='5', fill='red')


class Line(Object):
    """Creates a straight line that starts from (x,y) and ends at width and height

    (thinking about this, what kind of line has width and height....)
    """

    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)

    def _draw(self):
        # tk uses x1 y1 x2 y2 notation, which is pretty gross
        # TODO probably use x1 y1 x2 y2 because it makes more sense (apparently)....
        return Window.create_line(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Rectangle(Object):
    """Creates a rectangle that starts from (x,y) and is width long and height high"""

    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)

    def _draw(self): return Window.create_polygon(self.window, self.points, self.options)


class Circle(Object):
    """Creates a circle using (x,y) as the center point, that spreads radius outwards"""
    # TODO maybe make it also availble to put in bounding box?
    # TODO make a functiom that returns a bbox from a center point

    def __init__(self, window, x, y, radius):
        Object.__init__(self, window, float(x) - radius, float(y) - radius, radius*2, radius*2)
        self.options['smooth'] = True
        self.precision = 30  # Makes the circle more rounded
        self.rotate(0)
        # TODO make this more efficient

    def _draw(self): return Window.create_polygon(self.window, self.points, self.options)


class Oval(Object):
    """Creates an oval based on a defined box, which starts at (x,y) and is width long and height high"""

    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)
        self.options['smooth'] = True
        self.precision = 20
        self.rotate(0)

    def _draw(self):
        # TODO Fix the redundancy of the polygon draw statements, without affecting text and entry
        return Window.create_polygon(self.window, self.points, self.options)


class Text(Object):
    """Creates a text object, centered on (x,y)"""
    def __init__(self, window, x, y, text):
        self.text = text
        Object.__init__(self, window, x, y, width=0, height=0)

    def _draw(self):
        return self.window.create_text(self.x, self.y, text=self.text)


class Entry(Object):
    """Creates an entry box, which text and numbers can be entered into"""
    def __init__(self, window, x, y, width, placeholder=''):
        self.text = tk.StringVar(_master)
        self.text.set(placeholder)
        Object.__init__(self, window, x, y, width, height=0)
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
    myline = Line(window, 250, 250, 100, 0)
    myline.draw()
    mycircle = Circle(window, 250, 250, 200)
    mycircle.draw()
    #mycircle.draw_points()
    myrect = Rectangle(window, 0, 0, 200, 200)
    #myrect.draw()
    myoval = Oval(window, 0, 50, 200, 100)
    myoval.draw()
    myoval.draw_points()
    mytext = Text(window, 50, 50, 'YEET')
    mytext.draw()
    myentry = Entry(window, 100, 100, 20)
    myentry.draw()

    while True:
        # window.move(myoval.id, 1, 1)
        # window.move(mycircle.id, 1, 1)
        window.update_idletasks()
        window.update()
        window.after(15)
