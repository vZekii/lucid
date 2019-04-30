import tkinter as tk
from random import randint

print(tk.TkVersion)

window = tk.Tk('Tests')

os = window.tk.call('tk', 'windowingsystem')
print(os)

mylabel = tk.Label(window, text='name jeff')
mylabel.pack()

def xd():
    move('random')


def move(e):
    x = randint(0, 1366)
    y = randint(0, 768)
    window.tk.call('event', 'generate', '.', '<Motion>', '-x', x, '-y', y, '-warp', '1')
    window.update()
    window.after(1000, xd)


print(window.tk.call('event', 'info'))
window.bind('<1>', move)

window.mainloop()