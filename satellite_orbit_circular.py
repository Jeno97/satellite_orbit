# script to plot the orbit of a satellite around Earth
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation 

G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m
h = 4.2e5 # orbit of satellite above Earth

r = R_E + h # total distance to Earth's centre

# calculate velocity
v_s = np.sqrt((G*M_E)/r)

# calculate angular velocity
w_s = v_s / r

# calculate position for plot
t_pos = np.linspace(0, (2*np.pi/w_s), 100)

# calculate angle at time t
theta_s = w_s * t_pos

# satellite position at time t
x_s = r*np.cos(theta_s)
y_s = r*np.sin(theta_s)

# define plot
fig, ax = plt.subplots()
ax.set_aspect('equal')

# moving satellite object
satellite, = ax.plot([], [], 'ro')

# animation
def update(i):
	satellite.set_data(x_s[i], y_s[i])
	return satellite,

# plot positions
earth = patches.Circle((0, 0), R_E, color = 'dodgerblue', alpha = 0.3)
ax.add_patch(earth)
ax.plot(x_s,y_s,'gray',linestyle='--')
ani = FuncAnimation(fig, update, frames=len(x_s), interval=30)
plt.show()