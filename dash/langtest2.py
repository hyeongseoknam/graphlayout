import numpy as np
import math
import matplotlib.pyplot as plt
childs =32
circlrR = 1

r=circlrR * 2 * (childs+3) / (2*math.pi)
t= np.arange(-math.pi,math.pi, 0.1)
x=r*np.sin(t)
y=r*np.cos(t)
plt.plot(x,y)



top = 1
left = 1
width = 1
height = 1
centerx = 0
centery = 0
#r=50
margin=200
inc = float(2)*math.pi / float(7)
import random
r = 1
for t in np.arange(-3* math.pi, 3*math.pi, inc):
    circlrR = float(random.randrange(100)) / 50.0
    x = r * math.cos(t) + centerx
    y = r * math.sin(t) + centery
    
    plt.gca().add_patch(plt.Rectangle((x, y), circlrR,circlrR, color='r'))
    print("{:.0f},{:.0f}".format(x,y), circlrR)
    r += 1
plt.axis('equal')

plt.show()