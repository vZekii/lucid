import functools
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
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            value = func(*args, **kwargs)
            if args[0].autoflush:
                args[0].update()
            return value
        return wrapper_decorator

    @autoflush
    def on_close(self, *args):
        self.master.destroy()

    @autoflush
    def set_bg(self, colour):

        self.config(bg=colour)

    def is_open(self):
        return self.open


class Object:
    def __init__(self, window, x, y, width, height):
        self.window = window
        self.id = None

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.points = self.generate_points()

        self.rotation = 0
        self.size = 1

    def generate_points(self):
        return [(self.x, self.y),
               (self.x + self.width, self.y),
               (self.x + self.width, self.y + self.height),
               (self.x, self.y + self.height)]

    def scale(self, new_scale):
        self.size = new_scale
        self.x += (self.width - (self.width * new_scale))
        self.y += (self.height - (self.height * new_scale))
        self.width *= new_scale
        self.height *= new_scale

    def rotate(self, angle, steps=4):
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
        for i in range(steps):
            # Calculate the angle for this step
            # 360 degrees == 2 pi radians
            theta = (math.pi * 2) * (float(i) / steps)

            x1 = a * math.cos(theta)
            y1 = b * math.sin(theta)

            # rotate x, y
            x = (x1 * math.cos(rotation)) + (y1 * math.sin(rotation))
            y = (y1 * math.cos(rotation)) - (x1 * math.sin(rotation))

            point_list.append(round(x + xc))
            point_list.append(round(y + yc))

        self.window.coords(self.id, *point_list)

    def _draw(self):
        return 0

    def draw(self):
        self.id = self._draw()
        _master.update()


class Box(Object):
    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)

    def _draw(self):
        return tk.Canvas.create_polygon(self.window, self.points, {'outline': 'red'})


class Oval(Object):
    def __init__(self, window, x, y, width, height):
        Object.__init__(self, window, x, y, width, height)

    def _draw(self):
        return tk.Canvas.create_polygon(self.window, self.points, {'smooth': 'true'})


def rgb(r, g, b):
    color = (r, g, b)
    for c in color:
        if not 0 <= c <= 255:
            raise ValueError(f'rgb {c} not within 0-255')

    return f'#{r:02x}{g:02x}{b:02x}'


if __name__ == '__main__':
    window = Window()
    window.set_bg(rgb(255, 126, 60))
    oval = Oval(window, 50, 50, 100, 50)
    oval.draw()
    print(oval)
    oval2 = Oval(window, 50, 100, 100, 50)
    oval2.draw()
    oval2.rotate(0, steps=20)
    oval3 = tk.Canvas.create_oval(window, 50, 150, 150, 200)
    while True:
        window.update()
        window.update_idletasks()
        window.after(1000)
        oval.rotate(0, steps=20)
