import pk

win = pk.Window()
win.set_bg('red')

rotation_display = pk.Text(win, 250, 100, "0")

rot_rect = pk.Rectangle(win, 200, 200, 100, 100)


def inc(e=None):
    rot_rect.width += 1
    rotation_display.change_text(str(rot_rect.rotation))


def dec(e=None):
    rot_rect.rotate(1)
    rotation_display.change_text(str(rot_rect.rotation))

up_button = pk.Button(win, 200, 150, 'rot up', command=inc)
down_button = pk.Button(win, 300, 150, 'rot down', command=dec)


win.bind_key('a', dec)

win.mainloop()