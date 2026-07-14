# script to plot the orbit of a satellite around Earth
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation 

G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m
h = 4.2e5 # orbit height of satellite above Earth

# eccentricty
e = 0.6

# semi-major axis
a = (R_E+h)/(1-e)

# semi minor axis
b = a * np.sqrt(1 - e**2)

# angular velocity
n = np.sqrt((G*M_E)/a**3)

# calculate positions for plot
t_pos = np.linspace(0, (2*np.pi/n), 100)

# calculate the mean anomaly
M = n * t_pos

# need to solve for eccentric anomalies (angle from centre of ellipse to imaginary circle with radius a)
E = np.copy(M) #initial guess is mean anomaly

# use Newton-Rhapson iterative algorithm to solve for E (uses derivatives)
for _ in range(5):
	E = E - (E - e*np.sin(E) - M) / (1 - e*np.cos(E))

# satellite position at time t
x_pos = a*np.cos(E) - a*e # subtract off-centre focus distance as Earth is at centre of animation
y_pos = b*np.sin(E)

# take derivative of position to get velocity wrt angle E
v_x_E = -a*np.sin(E)
v_y_E = b*np.cos(E)
# then use Chain rule to get dE/dt and then v_x and v_y as function of time
dE_dt = n / (1 - e * np.cos(E))
v_x = v_x_E * dE_dt
v_y = v_y_E * dE_dt

# define plot
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_aspect('equal')

# moving satellite object
satellite, = ax.plot([], [], 'ko')

# define radial vector to satellite
radial_line, = ax.plot([], [], color = 'red', linestyle = '-', alpha=0.6, label = "Radial Vector (r)")

# vertical projection line
projection_line, = ax.plot(
    [],
    [],
    color="green",
    linestyle=":",
    alpha=0.5,
    label="Circle Projection")

# velocity vector and components using quiver
v_vector = ax.quiver([0], [0], [0], [0], color='red', angles='xy', scale_units='xy', scale=1, label="Velocity Vector")
v_x_component = ax.quiver([0], [0], [0], [0], color='green', angles='xy', scale_units='xy', scale=1, label="v_x Component")
v_y_component = ax.quiver([0], [0], [0], [0], color='royalblue', angles='xy', scale_units='xy', scale=1, label="v_y Component")

# vis-viva equation (conservation of mechanical energy in a gravitational field)
r_s = np.sqrt(x_pos**2 + y_pos**2)
v_s = np.sqrt((G*M_E)*((2/r_s) - (1/a)))

# text with velocity and distance
telemetry_text = ax.text(0.05, 0.95, "", transform=ax.transAxes, fontsize=10, 
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# get acceleration due to gravity
a_s = (G*M_E)/(r_s**2)
a_vector = ax.quiver([0], [0], [0], [0], color='k', angles='xy', scale_units='xy', scale=1, label="Acceleration Vector")

# auxilliary circle
aux_circle = patches.Circle(
    (-a * e, 0),
    a,
    color="green",
    fill=False,
    linestyle=":",
    alpha=0.3,
    label="Auxiliary Circle")

# plot statics
earth = patches.Circle((0, 0), R_E, color = 'dodgerblue', alpha = 0.3)
ax.add_patch(earth)
ax.add_patch(aux_circle)
ax.plot(x_pos,y_pos,'gray',linestyle='--')
ax.legend(loc="upper right")

# animation
def update(i):
    satellite.set_data([x_pos[i]], [y_pos[i]])
    radial_line.set_data([0, x_pos[i]],[0, y_pos[i]])

    x_circle = a * np.cos(E[i]) - a * e
    y_circle = a * np.sin(E[i])
    projection_line.set_data([x_pos[i], x_circle], [y_pos[i], y_circle])

    # set text to display current distance, speed and acceleration
    r_s_km = r_s[i] / 1000
    v_s_km_s = v_s[i] / 1000
    a_s_m_s = a_s[i]
    telemetry_text.set_text(f"Distance: {r_s_km:,.0f} km\nVelocity: {v_s_km_s:.2f} km/s\nAcceleration: {a_s_m_s:.2f} m/s")

    # Getting velocity vectors
    # Dynamic Arrow Math: Normalize components to a clear length (30% of Earth's Radius)
    speed = np.sqrt(v_x[i]**2 + v_y[i]**2)
    u_dir = v_x[i] / speed
    v_dir = v_y[i] / speed
    arrow_length = R_E * 0.3

    # Target dynamic components
    u_val = u_dir * arrow_length
    v_val = v_dir * arrow_length

    v_vector.set_offsets([x_pos[i], y_pos[i]])
    v_x_component.set_offsets([x_pos[i], y_pos[i]])
    v_y_component.set_offsets([x_pos[i], y_pos[i]])

    v_vector.set_UVC(u_val, v_val)
    v_x_component.set_UVC(u_val, 0)
    v_y_component.set_UVC(0, v_val)

    # getting acceleration due to gravity vector
    u_acc_dir = -x_pos[i] / r_s[i] # define unit vectors pointing towards Earth
    v_acc_dir = -y_pos[i] / r_s[i]

    a_scale = (a_s[i]/np.max(a_s)) * arrow_length # scale acceleration for visibility

    a_vector.set_offsets([x_pos[i], y_pos[i]])
    a_vector.set_UVC(u_acc_dir*a_scale, v_acc_dir*a_scale)

    return satellite, radial_line, projection_line, telemetry_text, v_vector, v_x_component, v_y_component, a_vector

# plot positions animation
ani = FuncAnimation(fig, update, frames=len(x_pos), interval=30, blit=True)
plt.show()