import lucid

win = lucid.Window()

filemenu = [lucid.MenuItem('New', None),
            lucid.MenuItem('Open', None),
            None,
            lucid.MenuItem('Save', None)]

win.menu.add_submenu('File', filemenu)
win.bg = lucid.rgb(200, 20, 90)

rotation_display = lucid.Text(win, 250, 100, "0")

# rot_rect = pk.Oval(win, 100, 200, 200, 100)
rot_rect = lucid.Circle(win, 200, 200, 100)
other = lucid.Rectangle(win, 0, 0, 100, 50)

if rot_rect.collideswith(other):
    print('uh oh')

rot_rect.thickness = 5
rot_rect.outline = lucid.rgb(125, 125, 0)
rot_rect.fill = lucid.rgb(100, 0, 200)

print(lucid.Rectangle)


if rot_rect.is_drawn:
    print('ye')


def inc(e=None):
    rot_rect.width += 1
    rotation_display.change_text(str(rot_rect.rotation))
    rot_rect.x -= 1


def dec(e=None):
    rot_rect.rotate(1)
    rotation_display.change_text(str(rot_rect.rotation))


def points(e=None):
    rot_rect.draw_points()


up_button = lucid.Button(win, 200, 150, 'rot up', command=inc)
down_button = lucid.Button(win, 300, 150, 'rot down', command=dec)

win.bind_key('a', dec)
win.bind_key('z', inc)
win.bind_key('w', points)

while True:
    if rot_rect.collideswith(other):
        print('they colliding')

    win.update()