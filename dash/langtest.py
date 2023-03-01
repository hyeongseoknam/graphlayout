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
inc = float(2)*math.pi / float(childs)

print(inc, np.arange(-math.pi, math.pi, inc))
for t in np.arange(-math.pi, math.pi, inc):
    x = r * math.cos(t) + centerx
    y = r * math.sin(t) + centery
    plt.gca().add_patch(plt.Circle((x, y), circlrR, color='r'))
    print(x,y)
plt.axis('equal')

plt.show()