#!/usr/bin/python
import uinput
import subprocess as sp
import re
from math import *

def get_synclient_settings():
    p = sp.Popen(['synclient', '-l'], stdout=sp.PIPE)
    stdout, _ = p.communicate()
    lines = stdout.splitlines()
    assert lines[0] == 'Parameter settings:'
    return dict(re.match(r'^\s*(\w+)\s*=\s*([0-9.]+)\s*', line).groups()
        for line in lines[1:])

def main():
    settings = get_synclient_settings()
    left = int(settings['LeftEdge'])
    right = int(settings['RightEdge'])
    top = int(settings['TopEdge'])
    bottom = int(settings['BottomEdge'])

    events = (
        uinput.ABS_X + (left, right, 0, 0),
        uinput.ABS_Y + (top, bottom, 0, 0),
        uinput.BTN_JOYSTICK,
        uinput.BTN_THUMB,
        )

    centerx = (left+right)/2
    centery = (top+bottom)/2
    max_ofs_x = right - centerx
    max_ofs_y = bottom - centery

    device = uinput.Device(events)

    monitor = sp.Popen(['synclient', '-m', '30'],
        stdout=sp.PIPE, stderr=sp.STDOUT)

    header_line = '    time     x    y   z f  w  l r u d m     multi  gl gm gr gdx gdy\n'

    for line in iter(monitor.stdout.readline, ''):
        if line == header_line:
            continue

        x = int(line[10:14])
        y = int(line[15:19])
        lbtn = int(line[30])
        rbtn = int(line[32])

        dx = (x - centerx) / float(max_ofs_x)
        dy = (y - centery) / float(max_ofs_y)

        dx0 = copysign(pow(abs(dx), 2), dx)
        dy0 = copysign(pow(abs(dy), 2), dy)

        x0 = int(dx0 * max_ofs_x + centerx)
        y0 = int(dy0 * max_ofs_y + centery)

        # syn=False to emit an "atomic" (x, y)+btns event.
        device.emit(uinput.ABS_X, x0, syn=False)
        device.emit(uinput.ABS_Y, y0, syn=False)
        device.emit(uinput.BTN_JOYSTICK, lbtn, syn=False)
        device.emit(uinput.BTN_THUMB, rbtn)


if __name__ == "__main__":
    main()
