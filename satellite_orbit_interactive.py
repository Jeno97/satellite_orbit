# script to plot the interactive orbit of a satellite around Earth
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m
h = 4.2e5 # orbit height of satellite above Earth
i = np.radians(45) # define orbital inclination

# eccentricty
e = 0.6

# use perigee radius as it is fixed
r_p = R_E + h

if e == 1.0:
    a = np.inf # need this as it would break otherwise
else:
    a = r_p / (1-e)

# calculate apogee distance
r_ap = a* (1 + e)

# semi minor axis
b = a * np.sqrt(1 - e**2)

# calculate true anomaly (measured from centre of Earth to satellite)
true_anomaly = np.linspace(0, 2*np.pi, 100) # nu

r_s = (a*(1-e**2))/(1+e*np.cos(true_anomaly)) # polar coords

x_s = r_s*np.cos(true_anomaly) # translate to cartesian
y_s = r_s*np.sin(true_anomaly)

# vis-viva equation (conservation of mechanical energy in a gravitational field)
v_s = np.sqrt((G*M_E)*((2/r_s) - (1/a)))

# calculate flight path angle (because of ellipse etc., radial vector is not perpendicular to velocity always)
phi = np.arctan2(e*np.sin(true_anomaly),1+e*np.cos(true_anomaly))

# calculate total angle
total_angle = true_anomaly + np.pi/2 - phi

# split velocity into components
v_x = v_s * np.cos(total_angle)
v_y = v_s * np.sin(total_angle)

# define plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 7))
ax1.set_aspect('equal')
plt.subplots_adjust(bottom=0.3)

# moving satellite object
satellite, = ax1.plot([], [], 'ko')

# define radial vector to satellite
radial_line, = ax1.plot([], [], color = 'red', linestyle = '-', alpha=0.6, label = "Radial Vector (r)")

# velocity vector and components using quiver
v_vector = ax1.quiver([0], [0], [0], [0], color='red', angles='xy', scale_units='xy', scale=1, label="Velocity Vector")
v_x_component = ax1.quiver([0], [0], [0], [0], color='green', angles='xy', scale_units='xy', scale=1, label="v_x Component")
v_y_component = ax1.quiver([0], [0], [0], [0], color='royalblue', angles='xy', scale_units='xy', scale=1, label="v_y Component")

# text with velocity and distance
telemetry_text = ax1.text(0.05, 0.95, "", transform=ax1.transAxes, fontsize=10, 
                         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# plot statics
earth = patches.Circle((0, 0), R_E, color = 'dodgerblue', alpha = 0.3)
ax1.add_patch(earth)
ax1.legend(loc="upper right")

# add a slider
ax_ecc = plt.axes([0.2, 0.05, 0.6, 0.03])
ecc_slider = Slider(ax_ecc, 'Eccentricity', 0.0, 0.99, valinit=e, valstep=0.01)

orbit_line, = ax1.plot(x_s, y_s, 'gray', linestyle='--')

# plotting ground track
# translate to 3D coords using orbital inclination
X = x_s
Y = y_s * np.cos(i)
Z = y_s * np.sin(i)

# calculate Eccentric anomaly from true anomaly
E = 2*np.arctan(np.sqrt((1-e)/(1+e))*np.tan(true_anomaly/2))

# mean orbital motion (averaged over ellipse)
n = np.sqrt((G*M_E)/a**3)

# calculate mean anomaly
M = E - e*np.sin(E)

# calculate the time array (time at each angle)
t = M/n

# how much has Earth rotated?
w_E = 7.2921e-5 # rad/s

E_rot = w_E*t # array of angle Earth has rotated at each satellite instance

# we rotate the satellite position westwards to simulate Earth rotating eastwards
X_new = X*np.cos(E_rot) + Y*np.sin(E_rot)
Y_new = -X*np.sin(E_rot) + Y*np.cos(E_rot)
Z_new = Z

# convert to Latitude and Longitude
lat = np.arcsin(Z_new/r_s) * (180/np.pi)
lon = np.arctan2(Y_new, X_new) * (180/np.pi)

# plotting
# add plot of Earth
try:
    img = plt.imread('images/Earthmap1000x500.jpg')
    ax2.imshow(img, extent=[-180, 180, -90, 90], aspect='auto', alpha=0.8)
except FileNotFoundError:
    ax2.grid(True, linestyle=':', alpha=0.8) 

ax2.set_xlim([-180, 180])
ax2.set_ylim([-90, 90])
gt = ax2.scatter(lon, lat, color='black', s=1)

satellite_gt, = ax2.plot([], [], 'ko') # ground track

# add inclination slider
ax_inc = plt.axes([0.2, 0.1, 0.6, 0.03]) # Placed slightly above the ecc slider
inc_slider = Slider(ax_inc, 'Inclination (°)', 0.0, 90.0, valinit=45.0, valstep=1.0)

# add height slider
ax_h = plt.axes([0.2, 0.15, 0.6, 0.03]) # Placed slightly above the ecc slider
h_slider = Slider(ax_h, 'Satellite Height (km)', 0.0, 36000, valinit=420, valstep=1.0) # Geostationary orbit is 3.6e7 m

# what to do when eccentricity slider is changed
def update_slider(val):

    # when e is changed update it and all arrays that depend on it
    new_e = ecc_slider.val

    # when i changed update it and all arrays that depend on it
    new_i_deg = inc_slider.val

    # when h changed update it and all arrays that depend on it
    new_h_km = h_slider.val

    global r_s, x_s, y_s, v_s, v_x, v_y, a, b, lat, lon, X, Y, Z, i, r_p, h, r_ap

    r_p = R_E + new_h_km*1000

    if new_e == 1.0:
        a = np.inf # need this as it would break otherwise
    else:
        a = r_p / (1-new_e)

    # calculate apogee distance
    r_ap = a* (1 + new_e)

    # update all values
    r_s = (a*(1-new_e**2))/(1+new_e*np.cos(true_anomaly)) # polar coords

    x_s = r_s*np.cos(true_anomaly) # translate to cartesian
    y_s = r_s*np.sin(true_anomaly)

    # vis-viva equation (conservation of mechanical energy in a gravitational field)
    v_s = np.sqrt((G*M_E)*((2/r_s) - (1/a)))

    # calculate flight path angle (because of ellipse etc., radial vector is not perpendicular to velocity always)
    phi = np.arctan2(new_e*np.sin(true_anomaly),1+new_e*np.cos(true_anomaly))

    # calculate total angle
    total_angle = true_anomaly + np.pi/2 - phi

    # split velocity into components
    v_x = v_s * np.cos(total_angle)
    v_y = v_s * np.sin(total_angle)

    # update limits
    ax1.set_xlim([-r_ap * 1.2, r_p * 1.5])
    ax1.set_ylim([-r_ap * 0.8, r_ap * 0.8])

    orbit_line.set_data(x_s, y_s)

    # update ground track plot
    new_i = np.radians(new_i_deg)

    X = x_s
    Y = y_s * np.cos(new_i)
    Z = y_s * np.sin(new_i)

    # calculate Eccentric anomaly from true anomaly
    E = 2*np.arctan(np.sqrt((1-new_e)/(1+new_e))*np.tan(true_anomaly/2))
    E = np.unwrap(E)

    # mean orbital motion (averaged over ellipse)
    n = np.sqrt((G*M_E)/a**3)

    # calculate mean anomaly
    M = E - new_e*np.sin(E)

    # calculate the time array (time at each angle)
    t = M/n

    # how much has Earth rotated?
    w_E = 7.2921e-5 # rad/s

    E_rot = w_E*t # array of angle Earth has rotated at each satellite instance

    # we rotate the satellite position westwards to simulate Earth rotating eastwards
    X_new = X*np.cos(E_rot) + Y*np.sin(E_rot)
    Y_new = -X*np.sin(E_rot) + Y*np.cos(E_rot)
    Z_new = Z

    # convert to Latitude and Longitude
    lat = np.arcsin(Z_new/r_s) * (180/np.pi)
    lon = np.arctan2(Y_new, X_new) * (180/np.pi)

    gt.set_offsets(np.c_[lon, lat])

    # Force clear the blit background cache completely
    if hasattr(ani, '_blit_cache'):
        ani._blit_cache.clear()

    fig.canvas.draw_idle() # smoothly updates frame

# animation
def update(i):
    satellite.set_data([x_s[i]], [y_s[i]])
    radial_line.set_data([0, x_s[i]],[0, y_s[i]])

    # set text to display current distance, speed and acceleration
    r_s_km = r_s[i] / 1000
    v_s_km_s = v_s[i] / 1000
    telemetry_text.set_text(f"Distance: {r_s_km:,.0f} km\nVelocity: {v_s_km_s:.2f} km/s")

    # Getting velocity vectors
    # Dynamic Arrow Math: Normalize components to a clear length (30% of Earth's Radius)
    speed = np.sqrt(v_x[i]**2 + v_y[i]**2)
    u_dir = v_x[i] / speed
    v_dir = v_y[i] / speed
    arrow_length = R_E * 0.6

    # Target dynamic components
    u_val = u_dir * arrow_length
    v_val = v_dir * arrow_length

    v_vector.set_offsets([x_s[i], y_s[i]])
    v_x_component.set_offsets([x_s[i], y_s[i]])
    v_y_component.set_offsets([x_s[i], y_s[i]])

    v_vector.set_UVC(u_val, v_val)
    v_x_component.set_UVC(u_val, 0)
    v_y_component.set_UVC(0, v_val)

    # update satellite ground track
    satellite_gt.set_data([lon[i]], [lat[i]])

    return satellite, radial_line, telemetry_text, v_vector, v_x_component, v_y_component, satellite_gt

# Set initial framing bounds before animation starts
ax1.set_xlim([-r_ap * 1.2, r_p * 1.5])
ax1.set_ylim([-r_ap * 0.8, r_ap * 0.8])

# plot positions animation
ani = FuncAnimation(fig, update, frames=len(x_s), interval=30, blit=True)
ecc_slider.on_changed(update_slider) # calls update_slider once changed
inc_slider.on_changed(update_slider) # calls update_slider once changed
h_slider.on_changed(update_slider) # calls update_slider once changed
plt.show()