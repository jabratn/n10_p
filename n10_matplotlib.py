from n10 import N10
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from math import cos, sin, radians, floor

n10 = N10('/dev/ttyUSB0') # Change to your N10 port
fig, ax = plt.subplots()
x, y, lum = [0]*360, [0]*360, [0]*360
sc = ax.scatter(x, y)

def update(data):
    ax.clear()
    for i in data:
        print(i[0], i[1], i[2])
        deg = floor(i[0])
        x[deg] = cos(radians(i[0])) * i[1]
        y[deg] = sin(radians(i[0])) * -i[1]
        lum[deg] = i[2] / 255.0
    ax.scatter(x, y, alpha=lum)
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width*fig.dpi, bbox.height*fig.dpi
    ar = width/height
    dmax = max(*x, *y)*1.1
    dmin = min(*x, *y)*1.1
    ax.add_artist(Circle((0, 0), dmax*0.025 , fc='red'))
    ax.set_xlim(dmin*ar, dmax*ar)
    ax.set_ylim(dmin, dmax)
    plt.pause(0.0001)
    fig.canvas.draw()

plt.show(block=False)

n10.scan(update)

n10.shutdown()
