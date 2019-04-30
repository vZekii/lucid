import tkinter as tk
import math

_master = tk.Tk()
_master.withdraw()  # Hide it for background control


class Window(tk.Canvas):
    def __init__(self, width=500, height=500):
        self.master = tk.Toplevel(_master)
        self.master.bind('<Destroy>', self.on_close)
        self.master.configure(cursor="dotbox green")
        self.master.resizable(0, 0)
        tk.Canvas.__init__(self, self.master, width=width, height=height)
        self.pack()
        self.autoflush = True
        self.master.protocol('WM_DELETE_WINDOW', self.on_close)
        self.open = True

    def autoflush(func):
        def wrapper_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            if args[0].autoflush:
                args[0].update()
            return value
        return wrapper_decorator

    @autoflush
    def on_close(self):
        self.master.destroy()

    @autoflush
    def set_bg(self, colour):
        self.config(bg=colour)

    def is_open(self):
        return self.open


class Object:
    def __init__(self, window, x, y, width, height):
        self.window = window
        self.id = None  # assigned on creation

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.points = self.generate_points()

        self.options = {'outline': 'black',
                        'smooth': 'false'}

        self.rotation = 0  # recorded in degrees
        self.precision = 4  # number of points that make up the shape

    def generate_points(self):
        # Converts xywh to (x1 y1) (x2 y2) ... (tk format)
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

    def _draw(self): return 0  # stub to be overridden by child classes

    def draw(self):
        self.id = self._draw()
        _master.update()

    def draw_points(self):
        # debug function that shows points of object as red and border box as green
        tk.Canvas.create_rectangle(self.window, self.x, self.y,
                                   self.x + self.width, self.y + self.height, outline='green', width='2')
        for x, y in self.points:
            tk.Canvas.create_line(self.window, x, y, x+1, y+1, width='5', fill='red')

    def check_collision(self, object2):
        pass


class Rectangle(Object):
    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)

    def _draw(self): return tk.Canvas.create_polygon(self.window, self.points, self.options)


class Oval(Object):
    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)
        self.options['smooth'] = True
        self.precision = 20
        self.rotate(0)

    def _draw(self):
        return tk.Canvas.create_polygon(self.window, self.points, self.options)
        # Since this is identical to rectangle and probs most others, wont need this to be repeated later


if __name__ == '__main__':
    window = Window()
    rect1 = Rectangle(window, 10, 10, 200, 100)
    rect1.draw()
    rect1.draw_points()
    print(rect1.precision)
    oval1 = Oval(window, 210, 10, 200, 100)
    oval1.draw()
    oval1.draw_points()
    oval2 = Oval(window, 10, 110, 400, 100)
    oval2.draw()
    oval2.draw_points()
    sphere = Oval(window, 10, 210, 200, 200)
    sphere.draw()
    sphere.draw_points()
    while True:
        window.update()