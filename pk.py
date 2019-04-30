# the main file for now

import math
import string
import tkinter as tk  # May have to change this later to detect if tkinter is available

# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    """Class to manage window related actions """

    def __init__(self, title='pk Window', width=500, height=500):
        self.master = tk.Toplevel(_master)
        self.master.title(title)
        self.master.resizable(0, 0)
        tk.Canvas.__init__(self, self.master, width=width, height=height, highlightthickness=0)

        # display the canvas on the window
        self.pack()
        self.autoflush = True

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self._on_close)
        self.master.bind('<Destroy>', self._on_close)  # hopefully fix closing

        # start the event handler
        self.EventHandler = EventHandler(self)

    def autoflush(func):
        # a decorator that refreshes the window once the decorated function is run - if autoflush is true
        def wrapper_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            if args[0].autoflush:
                args[0].update()
            return value

        return wrapper_decorator

        # TODO either fix or change this

    def on_close(self):
        """Stub to manage the closing of the window - should be modifiable by the user"""
        pass

    @autoflush
    def _on_close(self, *args):
        """runs the user-defined close function, then closes then window"""
        self.on_close()
        self.master.destroy()
        # TODO check if window is destroyed and assert an error if so

    @autoflush
    def set_bg(self, colour):
        """Changes the background colour to the colour specified

        :param colour: The colour to be changed to - accepts all tkinter colours, hex, and conversions from rgb
        :type colour: string
        """
        self.config(bg=colour)

    def bind_key(self, key, func):
        if key in self.EventHandler.bindings.keys():
            self.EventHandler.bindings[key] = func
            # TODO somehow get arguments without lambda
        else:
            raise Exception(f'Key not in bindings dir: {key}')

    def get_mouse(self):
        """Returns the current cursor position based on the window
        :return: (x, y) position of mouse
        :rtype: tuple
        """
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        return x, y

    # TODO look at making a Coords and Bbox named tuple for ease


class EventHandler:
    """Class to manage both key and mouse events"""
    bindings = {}  # Dictionary to store all bindings

    def __init__(self, window):
        self.latest = False  # Stores the latest event

        self.initialize_bindings()
        window.bind_all('<Key>', self.new_event)

        for i in range(1, 4):
            window.bind_all(f'<Button-{i}>', self.new_event)  # Mouse click
            window.bind_all(f'<B{i}-Motion>', self.new_event)  # Mouse motion with button held down
            window.bind_all(f'<ButtonRelease-{i}>', self.new_event)  # Mouse release

            # window.bind_all(f'<Double-Button-{i}>', self.new_event)
            # window.bind_all(f'<Triple-Button-{i}>', self.new_event)

    def initialize_bindings(self):
        for char in string.ascii_letters:  # includes upper and lower
            self.bindings[char] = Event(char)
        for sym in string.punctuation:
            self.bindings[sym] = Event(sym)
        for num in range(0, 10):  # 0~9
            self.bindings[str(num)] = Event(num)
        for arrow in ['Up', 'Down', 'Left', 'Right']:  # Arrow keys
            self.bindings[arrow] = Event(arrow)
        for key in ['space', 'BackSpace', 'Return', 'Shift_L', 'Shift_R']:
            self.bindings[key] = Event(key)

        # TODO get a better way to do this

    def new_event(self, event):
        try:
            self.bindings[event.keysym](event)
            self.latest = event
        except KeyError:
            Exception('Key not in bindings dir')

    def get(self):
        return self.latest


class Event:
    """Class to manage an event happening"""

    def __init__(self, sym):
        self.func = None

    def __call__(self, event):
        try:
            self.func(event)
        except TypeError:
            pass
        # finally:
        #     print(f'key: {event.keysym}, state: {event.state}, coords: {event.x, event.y}')

    # TODO check redundancy with the handler


class Object:
    """Class to manage base level attributes and commands of all objects """

    # TODO fix weird glitch where some parts of the shape don't draw if updated too quickly (about 40+ fps)
    # ^^^ I'm assuming its to do with the refresh rate of the monitor
    #  TODO implement sizing (maybe)
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
        self.debug_tag = None  # assigned to objects related to debugging
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Coordinates for all points of the shape
        self.points = self.generate_points()

        # options for customisation
        self.options = {'outline': 'black',
                        'fill': '',  # Empty string is transparent
                        'smooth': False}

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
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
        rotation = self.rotation * math.pi / 180.0

        # major and minor axes
        a = self.width / 2
        b = self.height / 2

        # center
        xc = self.x + a
        yc = self.y + b

        point_list = []

        # create the object as a list of points
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

    # basic polygon drawing - overridden in non-poly objects
    def _draw(self):
        return Window.create_polygon(self.window, self.points, self.options)

    def draw(self):
        """Draws the shape to the current window """
        if self.id is None:
            self.id = self._draw()
            _master.update()

    def undraw(self):
        """Hides the object for drawing later """
        self.window.delete(self.id)
        if self.debug_tag:
            self.window.delete(self.debug_tag)
        self.id = None
        self.debug_tag = None  # Reset the object's id and tag as it no longer exists in the window
        _master.update()

    def draw_points(self):
        if self.debug_tag is None:
            self.debug_tag = f'{self.id}_debug'  # create a debug tag if it doesn't exist yet

        # debug function that shows points of object as red and border box as green
        Window.create_rectangle(self.window, self.x, self.y, self.x + self.width, self.y + self.height, outline='green',
                                width='2', tag=self.debug_tag)
        for x, y in self.points:
            Window.create_line(self.window, x, y, x + 1, y + 1, width='5', fill='red', tag=self.debug_tag)

    # function to move the object
    def move(self, x, y):
        if self.id:  # TODO change this to an is_drawn function or something
            self.x += x
            self.y += y
            if self.debug_tag:
                self.window.move(self.debug_tag, x, y)
            self.window.move(self.id, x, y)
        else:
            raise Exception('Object not currently drawn')  # TODO make some custom exceptions


class Line(Object):
    """Creates a straight line that starts from (x1, y1) and ends at (x2, y2) """

    def __init__(self, window, x1, y1, x2, y2):
        Object.__init__(self, window, x1, y1, x2 - x1, y2 - y1)  # convert to xywh

    def _draw(self):
        return Window.create_line(self.window, self.x, self.y, self.x + self.width, self.y + self.height)


class Rectangle(Object):
    """Creates a rectangle that starts from (x,y) and is width long and height high"""

    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)


class Circle(Object):
    """Creates a circle using (x,y) as the center point, that spreads radius outwards"""

    # TODO maybe make it also availble to put in bounding box?
    # TODO make a functiom that returns a bbox from a center point

    def __init__(self, window, x, y, radius):
        Object.__init__(self, window, float(x) - radius, float(y) - radius, radius * 2, radius * 2)
        self.options['smooth'] = True
        self.precision = 30  # Makes the circle more rounded
        self.rotate(0)
        # TODO make this more efficient


class Oval(Object):
    """Creates an oval based on a defined box, which starts at (x,y) and is width long and height high"""

    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)
        self.options['smooth'] = True
        self.precision = 20
        self.rotate(0)


class Text(Object):
    """Creates a text object, centered on (x,y)"""

    def __init__(self, window, x, y, text):
        self.text = text
        Object.__init__(self, window, x, y, width=0, height=0)

    def _draw(self):
        return self.window.create_text(self.x, self.y, text=self.text)


class Button(Object):
    """Creates a button, centered on (x,y)"""

    def __init__(self, window, x, y, text, width=0, height=0, command=None):
        self.text = tk.StringVar(_master, text)
        self.command = command
        Object.__init__(self, window, x, y, width, height)

    def _draw(self):
        if self.width and self.height:  # If custom width and height are defined
            frame = tk.Frame(self.window.master, width=self.width, height=self.height)
            frame.pack_propagate(0)
        else:
            frame = tk.Frame(self.window.master)

        self.button = tk.Button(frame, textvariable=self.text, command=self.command)
        self.button.pack(fill=tk.BOTH, expand=1)
        return self.window.create_window(self.x, self.y, window=frame)


class Entry(Object):
    """Creates an entry box, which text and numbers can be entered into"""

    def __init__(self, window, x, y, width, placeholder=''):
        self.text = tk.StringVar(_master, placeholder)
        Object.__init__(self, window, x, y, width, height=0)

    def _draw(self):
        frame = tk.Frame(self.window.master)
        self.entry = tk.Entry(frame, width=self.width, textvariable=self.text)
        self.entry.pack()
        return self.window.create_window(self.x, self.y, window=frame)


class CheckBox(Object):
    """Creates a checkbutton, which can have an on/off state, and a label"""

    def __init__(self, window, x, y, text, command=None):
        self.text = text
        self.var = tk.BooleanVar()  # var used to store checkbox state (on/off)
        self.command = command
        Object.__init__(self, window, x, y, 0, 0)

    def _draw(self):
        frame = tk.Frame(self.window.master)
        # TODO make the bg transparent
        self.button = tk.Checkbutton(frame, text=self.text, command=self.command, variable=self.var)
        self.button.pack()
        return self.window.create_window(self.x, self.y, window=frame)


class Image(Object):
    """Class to manage images

        Only works with PNG, GIF, and PGM/PPM formats currently
    """

    def __init__(self, window, x, y, filename):
        self.image = tk.PhotoImage(file=filename)
        Object.__init__(self, window, x, y, 0, 0)

    def _draw(self): return self.window.create_image(self.x, self.y, image=self.image)


def rgb(red, green, blue):
    """Helper function to convert an rgb colour to hex (so tkinter can understand it)
    :param red: amount of red
    :type red: int
    :param green: amount of green
    :type green: int
    :param blue: amount of blue
    :type blue: int
    :return: hex string
    """
    color = (red, green, blue)
    for c in color:
        if not 0 <= c <= 255:  # checks that the values fall within the range 0-255
            raise ValueError(f'Value {c} not within 0-255')

    return f'#{red:02x}{green:02x}{blue:02x}'


# TODO Implement listboxes, radiobuttons (maybe)
# TODO Implement Menubars (File, Edit, etc)


# This is for testing
if __name__ == '__main__':
    win = Window('Test window')
    win.set_bg(rgb(255, 20, 147))
    myimage1 = Image(win, 300, 300, 'testpng.png')
    myimage1.draw()
    myimage1.undraw()
    myimage1.draw()
    myline = Line(win, 400, 100, 450, 170)
    myline.draw()
    mycircle = Circle(win, 250, 250, 200)
    mycircle.draw()
    mycircle.draw_points()
    myrect = Rectangle(win, 250, 0, 100, 100)
    myrect.draw()
    myoval = Oval(win, 0, 50, 200, 100)
    myoval.draw()
    myoval.draw_points()
    myoval.undraw()
    myoval.draw()
    mytext = Text(win, 50, 50, 'YEET')
    mytext.draw()
    mybutton = Button(win, 100, 150, 'hit me until the bruh moment')
    mybutton.draw()
    myentry = Entry(win, 100, 100, 20, placeholder='Epic')
    myentry.draw()
    mycheckbox = CheckBox(win, 200, 200, 'Take my beans')
    mycheckbox.draw()

    while True:
        # myoval.move(1, 1)
        mycircle.move(1, 1)
        win.update_idletasks()
        win.update()
        win.after(15)
