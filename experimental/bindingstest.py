import tkinter as tk
import functools
import string
from pprint import pprint

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
        self.EventHandler = EventHandler(self)

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

    def bind_key(self, key, func):
        if key in self.EventHandler.bindings.keys():
            self.EventHandler.bindings[key] = func
            # TODO somehow get arguments without lambda
        else:
            raise Exception(f'Key not in bindings dir: {key}')

    def get_mouse(self):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()
        return x, y

    # TODO look at making a Coords and Bbox named tuple for ease


class EventHandler:
    bindings = {}

    def __init__(self, window):
        self.initialize_bindings()
        window.bind_all('<Key>', self.new_event)
        for i in range(1, 4):
            window.bind_all(f'<Button-{i}>', self.new_event)  # Mouse click
            window.bind_all(f'<B{i}-Motion>', self.new_event)
            # window.bind_all(f'<Double-Button-{i}>', self.new_event)
            # window.bind_all(f'<Triple-Button-{i}>', self.new_event)
            window.bind_all(f'<ButtonRelease-{i}>', self.new_event)

        self.latest = False

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
        pprint(self.bindings)

    def new_event(self, event):
        print(event)
        try:
            self.bindings[event.keysym](event)
            self.latest = event
        except KeyError:
            Exception('Key not in bindings dir')

    def get(self): return self.latest


class Event:
    def __init__(self, sym):
        print(sym)
        self.func = None

    def __call__(self, event):
        try:
            self.func(event)
        except TypeError:
            pass
        finally:
            print(f'key: {event.keysym}, state: {event.state}, coords: {event.x, event.y}')


def jeff(e):
    print('ya ye working')
    print(window.get_mouse())


if __name__ == '__main__':
    window = Window()
    while True:
        e = window.EventHandler.get()
        window.bind_key('a', jeff)
        window.bind_key('Up', jeff)
        #window.bind_key('jefffffffff', jeff)
        window.update()