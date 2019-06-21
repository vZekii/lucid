# the main file for now

import math
import string
import sys
from collections import namedtuple
import tkinter as tk  # May have to change this later to detect if tkinter is available

MenuItem = namedtuple('MenuItem', ['label', 'command'])


class PkError(Exception):
    """Base class for all exceptions"""
    pass


# Initialize a "controlling window"
_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    """Class to manage window related actions """

    def __init__(self, title='pk Window', width=500, height=500, autodraw=True):
        self.master = tk.Toplevel(_master)
        self.master.title(title)
        self.master.resizable(0, 0)
        tk.Canvas.__init__(self, self.master, width=width, height=height, highlightthickness=0)

        # display the canvas on the window
        self.pack()
        if autodraw:
            self.autodraw = True

        # management of the "X" button (closing)
        self.master.protocol('WM_DELETE_WINDOW', self._on_close)
        self.master.bind('<Destroy>', self._on_close)  # hopefully fix closing

        # start the event handler
        self.EventHandler = EventHandler(self)

        # set up default menu
        self.menu = Menu(self)
        self.master.config(menu=self.menu)

    def on_close(self):
        """Stub to manage the closing of the window - should be modifiable by the user"""
        pass

    def _on_close(self, *args):
        """runs the user-defined close function, then closes then window"""
        self.on_close()
        self.master.destroy()
        sys.exit()  # Actually closes the window now

    @property
    def bg(self):
        return self.cget('bg')

    @bg.setter
    def bg(self, colour):
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
            raise PkError(f'Key not found in bindings dir: {key}')

    def get_mouse(self):
        """Returns the current cursor position based on the window
        :return: (x, y) position of mouse
        :rtype: tuple
        """
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        return x, y

    # TODO look at making a Coords and Bbox named tuple for ease


class Menu(tk.Menu):
    current_menu = ''

    def __init__(self, master):
        tk.Menu.__init__(self, master)

        self.submenus = {}
        self.add_cascade(label='Quit', command=master.quit)

        self.current_menu = self

    def add_submenu(self, name, menulist):
        submenu = self._create_submenu()
        for item in menulist:
            if isinstance(item, MenuItem):
                submenu.add_command(label=item.label, command=item.command)
            else:
                submenu.add_separator()
        self.submenus[name] = submenu
        self.add_cascade(label=name, menu=submenu)

    def _create_submenu(self):
        return tk.Menu(self.current_menu, tearoff=0)


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

            # TODO add scroll wheel functionality

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
    def __init__(self, window, x, y, width, height, options=None):
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

        self.propeties = {
            'x': x,
            'y': y,
            'cx': x + (width / 2),
            'cy': y + (height / 2),
            'width': width,
            'height': height,
        }

        self.options = {
            'fill': '',  # Empty string is transparent
            'outline': 'black',
            'width': 1,  # this is outline thickness
            'smooth': False,
        }

        self.rotation = 0  # recorded in degrees
        self.precision = 4  # number of points that make up the shape

        if options: self.options.update(options)

        # Coordinates for all points of the shape
        self.points = self.generate_points()

        if window.autodraw: self.draw()

    def _updatecenter(self):
        self.propeties['cx'] = self.x + (self.width / 2)
        self.propeties['cy'] = self.y + (self.height / 2)

    # This is how the option setting would work
    def _optionset(self, opt, val):
        self.options[opt] = val
        if self.id:  # only change it immediately if the object is drawn
            self.window.itemconfigure(self.id, {opt: val})

    def _propertyset(self):
        if self.id:
            self.points = self.generate_points()
            self.rotate_to(
                self.rotation)  # allows the shape to keep rotation - this causes the center point to change however (is this a bug?)
            if not self.rotation:
                self._updatecenter()  # only lets the center point change when rotation is 0
            self.window.coords(self.id, self.convert_points_line())

    @property
    def fill(self):
        return self.options['fill']

    @fill.setter
    def fill(self, value):
        self._optionset('fill', value)

    @property
    def outline(self):
        return self.options['outline']

    @outline.setter
    def outline(self, value):
        self._optionset('outline', value)

    @property
    def thickness(self):
        return self.options['width']

    @thickness.setter
    def thickness(self, value):
        self._optionset('width', value)

    @property
    def x(self):
        return self.propeties['x']

    @x.setter
    def x(self, value):
        self.propeties['x'] = value
        self._propertyset()

    @property
    def y(self):
        return self.propeties['y']

    @y.setter
    def y(self, value):
        self.propeties['y'] = value
        self._propertyset()

    @property
    def cx(self):
        return self.propeties['cx']

    @property
    def cy(self):
        return self.propeties['cy']

    @property
    def width(self):
        return self.propeties['width']

    @width.setter
    def width(self, value):
        self.propeties['width'] = value
        self._propertyset()

    @property
    def height(self):
        return self.propeties['height']

    @height.setter
    def height(self, value):
        self.propeties['height'] = value
        self._propertyset()

    def generate_points(self):
        # Converts xywh to (x1 y1) (x2 y2) ... (tk polygon format)
        default = [(self.x, self.y),
                   (self.x + self.width, self.y),
                   (self.x + self.width, self.y + self.height),
                   (self.x, self.y + self.height)]

        if self.precision != 4:
            return self.generate_curve_points()
        else:
            return default

    def convert_points(self):
        # converts points from x1 y1 x2 y2 to (x1, y1) (x2, y2) ...
        self.points = [(self.points[i], self.points[i + 1]) for i in range(0, len(self.points), 2)]

    def convert_points_line(self):
        """ converts points from (x1, y1) (x2, y2) to x1 y1 x2 y2 """
        out = []
        for point in self.points:
            out.append(point[0]);
            out.append(point[1])
        return out

    def generate_curve_points(self):
        """ function to generate circles and ovals from a bbox"""

        # major and minor axes
        a = self.width / 2
        b = self.height / 2

        point_list = []

        for i in range(self.precision):
            theta = (math.pi * 2) * (float(i) / self.precision)

            x = a * math.cos(theta)
            y = b * math.sin(theta)

            point_list.append(round(x + self.cx))
            point_list.append(round(y + self.cy))

        return point_list

    def _rotate(self):
        """internal command to control rotations - shared by rotate and rotate_to

            made with help from: https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d"""

        # make it so the current object rotation is within 0-360 degrees
        if self.rotation >= 360:
            self.rotation %= 360
        elif self.rotation < 0:
            self.rotation += 360

        # Convert the angle into radians? for math stuff
        theta = self.rotation * math.pi / 180.0  # fixed bug where self.rotation was being used instead of angle

        new_points = []
        self.points = self.generate_points()  # Resets the object back to default, to allow more precise rotates
        self.convert_points()

        for (px, py) in self.points:
            # move object point back to origin
            px -= self.cx
            py -= self.cy

            # rotate point
            x = (px * math.cos(theta)) - (py * math.sin(theta))
            y = (py * math.cos(theta)) + (px * math.sin(theta))

            new_points.append(x + self.cx)
            new_points.append(y + self.cy)

        self.points = new_points

        if self.id is not None:
            self.window.coords(self.id, self.points)

        self.convert_points()

    def rotate_to(self, angle):
        """Rotates the object to the defined angle"""
        self.rotation = angle

        self._rotate()

    def rotate(self, angle):
        """Rotates the object (from its center) by the amount of degrees (angle) specified """
        self.rotation += angle

        self._rotate()

    # basic polygon drawing - overridden in non-poly objects
    def _draw(self):
        return Window.create_polygon(self.window, self.points, self.options)

    def draw(self):
        """Draws the shape to the current window - nothing happens if it is already drawn"""
        if not self.is_drawn:
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
                                width=2, tag=self.debug_tag)
        for x, y in self.points:
            Window.create_line(self.window, x, y, x + 1, y + 1, width=5, fill='red', tag=self.debug_tag)

    @property
    def is_drawn(self):
        if self.id:
            return True
        else:
            return False

    # function to move the object
    def move(self, x, y):
        if self.is_drawn:
            self.x += x
            self.y += y
            if self.debug_tag:
                self.window.move(self.debug_tag, x, y)
            self.window.move(self.id, x, y)
        else:
            raise PkError('Object not currently drawn')

    def __repr__(self):
        return "Object {}".format(self.__class__)

    def collideswith(self, obj2):
        if Object in obj2.__class__.__mro__:
            check = not ((obj2.x > (self.x + self.width) or (obj2.x + obj2.width) < self.x) or (
                        obj2.y < (self.y + self.height)) or ((obj2.y + obj2.height) > self.y))

            return check
        else:
            raise PkError(obj2.__class__, 'is not a pk.Object')


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

    def __init__(self, window, x, y, radius, **options):
        if options:
            options.update({'smooth': True})
        else:
            options = {'smooth': True}
        Object.__init__(self, window, float(x) - radius, float(y) - radius, radius * 2, radius * 2, options=options)
        self.precision = 30  # Makes the circle more rounded
        self.rotate(0)
        # TODO make this more efficient


class Oval(Object):
    """Creates an oval based on a defined box, which starts at (x,y) and is width long and height high"""

    def __init__(self, window, x, y, width, height, **options):
        if options:
            options.update({'smooth': True})
        else:
            options = {'smooth': True}
        Object.__init__(self, window, x, y, width, height, options=options)
        self.precision = 20
        self.rotate(0)


class Text(Object):
    """Creates a text object, centered on (x,y)"""

    def __init__(self, window, x, y, text):
        self.text = text
        Object.__init__(self, window, x, y, width=0, height=0)

    def _draw(self):
        return self.window.create_text(self.x, self.y, text=self.text)

    def change_text(self, text=''):
        if not text:
            self.text = text  # fixed bug where "text = self.text" was wrong way around
        self.window.itemconfigure(self.id, text=text)


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
