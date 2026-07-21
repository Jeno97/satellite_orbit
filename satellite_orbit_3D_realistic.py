# script to plot the interactive orbit of a satellite around Earth
# numerical simulation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as mticker
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, CheckButtons
from PIL import Image

# constants
G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m
h = 4.2e5 # orbit height of satellite above Earth

def get_total_acceleration(r, v, enable_drag=False, B=1e-6, enable_J2=False):
    # function to get total acceleration vector

    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)
    altitude = r_mag - R_E

    # acceleration due to gravity vector
    a_grav = -(G * M_E / r_mag**3) * r

    # acceleration due to drag of atmosphere vector
    if enable_drag:
        
        safe_altitude = max(0.0, altitude) # so it doesnt cause exponential problems
        # atmospheric density
        H = 5e4 # scale height
        rho = np.exp(-(safe_altitude/H))

        a_drag = -B*rho*v_mag*v
    else:
        a_drag = np.array([0, 0, 0])    

    # acceleration due to J2 pertubation vector
    if enable_J2:

        J_2 = 1.08263e-3 * 15 # Earth oblateness (add factor to make visible)

        a_J2_factor = -(3/2)*((J_2*G*M_E*(R_E**2))/r_mag**5)

        a_J2_x = r[0]*(5*(r[2]**2/r_mag**2)-1)
        a_J2_y = r[1]*(5*(r[2]**2/r_mag**2)-1)
        a_J2_z = r[2]*(5*(r[2]**2/r_mag**2)-3)

        a_J2 = a_J2_factor * np.array([a_J2_x, a_J2_y, a_J2_z])
    else:
        a_J2 = np.array([0, 0, 0])  

    return a_grav + a_drag + a_J2

def run_simulation(velocity_multiplier, enable_drag=False, B=1e-6, enable_J2=False, inc=0):

    # starting vector on the x-axis
    x = R_E + h
    r = np.array([x, 0, 0])

    # push satellite in any direction
    v = np.array([0, np.sqrt((G*M_E)/(x)) * np.cos(np.radians(inc)), np.sqrt((G*M_E)/(x)) * np.sin(np.radians(inc))]) * velocity_multiplier
    v0_mag = np.linalg.norm(v)
    
    if v0_mag == 0:
        t_total = 1000 # will crash into Earth
    else:
        inv_a = (2/x) - (v0_mag**2/(G*M_E)) # vis-viva

        if inv_a <= 0: # parabolic or hyperbolic orbit so no closed loop
            t_total = 10800
        else:
            a = 1/inv_a

            t_total = 5 * (2*np.pi) * (np.sqrt(a**3/(G*M_E)))

    # If drag is enabled, simulate 8 full orbits so we can see the spiral clearly!
    if enable_J2:
        t_total = 5600 * 60
    elif enable_drag and B > 1e-10:
        t_total = 5600 * 8
    print(t_total)
    # get initial acceleration
    a_total = get_total_acceleration(r, v, enable_drag, B, enable_J2)    
    
    dt = 10 # time step
    n_steps = int(t_total/dt)
    # X and Y positions for orbit plot
    X, Y, Z = [], [], []
    v_mag = []
    for j in range(n_steps):
        
        # store X, Y and Z position
        X.append(r[0])
        Y.append(r[1])
        Z.append(r[2])
        v_mag.append(np.linalg.norm(v))

        # break loop if we touch Earth's surface
        if np.sqrt(r[0]**2 + r[1]**2 + r[2]**2) <= R_E:
            print("Satellite has crashed into Earth")
            break
        
        # Velocity Verlet integrator method
        # update to new position
        r_new = r + (v*dt) + (0.5*a_total*dt**2)
        
        # predict velocity
        v_pred = v + a_total * dt

        # total acceleration vector
        a_total_new = get_total_acceleration(r_new, v_pred, enable_drag, B, enable_J2)

        # update velocity at new position
        v_new = v + 0.5*(a_total + a_total_new)*dt # use average acceleration a_avg = (a + a_new)/2

        # update vectors
        r = r_new
        v = v_new
        a_total = a_total_new

    return X, Y, Z, v_mag

# plotting
fig = plt.figure(figsize=(16, 8))
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122)
plt.subplots_adjust(bottom=0.2)

# add text with current velocity and positions
telemetry_text = ax1.text2D(0.05, 0.95, "", transform=ax1.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

# add sliders for relevant parameters
# velocity factor
ax_v_factor = plt.axes([0.15, 0.03, 0.45, 0.025])
v_slider = Slider(ax_v_factor, 'Initial Velocity Factor', -1.5, 1.5, valinit=1.0, valstep=0.05)

# Ballistic coefficient
ax_B = plt.axes([0.15, 0.07, 0.45, 0.025])
B_slider = Slider(ax_B, 'Ballistic Coefficient', 1e-10, 0.0001, valinit=1e-6, valstep=1e-5)

# inclination
ax_inc = plt.axes([0.15, 0.11, 0.45, 0.025])
inc_slider = Slider(ax_inc, 'Inclination', 0, 90, valinit=45, valstep=1)

# J2 button
ax_J2 = plt.axes([0.75, 0.04, 0.12, 0.08])
J2_button = CheckButtons(ax_J2, labels=['Enable J2'], actives=[False])

# run default circular orbit
X, Y, Z, v_mag = run_simulation(1.0, enable_drag=(B_slider.val > 1e-9), B=B_slider.val, enable_J2=J2_button.get_status()[0], inc=inc_slider.val)

# how much has Earth rotated?
w_E = 7.2921e-5 # rad/s
dt = 10
t = np.arange(len(X))*dt
E_rot = w_E*t # array of angle Earth has rotated at each satellite instance

# calculate initial ground track plot
r_s = np.linalg.norm(np.array([X, Y, Z]), axis=0)
lat = np.arcsin(Z/r_s) * (180/np.pi)
lon = ((np.arctan2(Y, X) - E_rot) * (180/np.pi) + 180) % 360 - 180 # modulo to ensure stays in -180 to 180

# moving satellite object
satellite, = ax1.plot([], [], [], 'r.', label='Satellite')
orbit_line, = ax1.plot(X, Y, Z, 'r', linestyle='--', label='Orbit Line')

# vectors
vel_line, = ax1.plot([], [], [], color='lime', lw=3, label='Velocity Vector')
grav_line, = ax1.plot([], [], [], color='cyan', lw=3)
acc_line, = ax1.plot([], [], [], color='magenta', lw=2, label='Total Acceleration Vector')

# satellite ground track
satellite_gt, = ax2.plot([], [], 'ro') # ground track position
gt_line, = ax2.plot(lon, lat, 'r.', markersize=0.4)

# slider changes
def update_slider(val):

    new_v = v_slider.val
    new_B = B_slider.val
    new_inc = inc_slider.val

    enable_J2_bool = J2_button.get_status()[0]

    global X, Y, Z, v_mag, r_s, lat, lon, gt_line

    use_drag = True if new_B > 1e-9 else False

    X, Y, Z, v_mag = run_simulation(new_v, enable_drag=use_drag, B=new_B, enable_J2=enable_J2_bool, inc=new_inc)

    orbit_line.set_data(np.array(X), np.array(Y))
    orbit_line.set_3d_properties(np.array(Z))
    
    # how much has Earth rotated?
    w_E = 7.2921e-5 # rad/s
    dt = 10
    t = np.arange(len(X))*dt
    E_rot = w_E*t # array of angle Earth has rotated at each satellite instance

    # get Latitude and Longitude plot
    r_s = np.linalg.norm(np.array([X, Y, Z]), axis=0)
    lat = np.arcsin(Z/r_s) * (180/np.pi)
    lon = ((np.arctan2(Y, X) - E_rot) * (180/np.pi) + 180) % 360 - 180

    gt_line.set_data(lon, lat)

    # update frames to use new number of positions
    ani._frames = len(X)
    ani.frame_seq = ani.new_frame_seq()

def set_vector(line, pos, vec):
    xs = np.array([pos[0], pos[0] + vec[0]])
    ys = np.array([pos[1], pos[1] + vec[1]])
    zs = np.array([pos[2], pos[2] + vec[2]])

    line.set_data(xs, ys)
    line.set_3d_properties(zs)

# animation
def update(j):

    if j >= len(X): # park satellite at last frame
        j = len(X) - 1
    
    # update vectors
    r_j = np.array([X[j], Y[j], Z[j]]) # get position again

    if j < len(X) - 1: # estimate velocity using next position
        v_j = (np.array([X[j+1], Y[j+1], Z[j+1]]) - r_j) / 10 # dt = 10
    else:
        v_j = (r_j - np.array([X[j-1], Y[j-1], Z[j-1]])) / 10

    # calculate total acceleration again
    enable_drag_bool = B_slider.val > 1e-9
    enable_J2_bool = J2_button.get_status()[0]
    a_tot_j = get_total_acceleration(r_j, v_j, enable_drag=enable_drag_bool, B=B_slider.val, enable_J2=enable_J2_bool)
    
    # gravity-only acceleration vector
    r_mag = np.linalg.norm(r_j)
    a_grav_j = -(G * M_E / r_mag**3) * r_j
   
    # need to scale vectors otherwise we dont see them
    v_scale = 500
    a_scale = 2e5

    v_vec = v_j * v_scale
    g_vec = a_grav_j * a_scale
    a_vec = a_tot_j * a_scale

    set_vector(vel_line, r_j, v_vec)
    set_vector(grav_line, r_j, g_vec)
    set_vector(acc_line, r_j, a_vec)

    # update text telemetry
    r_km = np.linalg.norm([X[j], Y[j], Z[j]])/1000
    alt_km = r_km - (R_E/1000)
    v_km_s = v_mag[j]/1000
    telemetry_text.set_text(f"Altitude: {alt_km:,.0f} km\nVelocity: {v_km_s:.2f} km/s")

    satellite.set_data(X[j], Y[j])
    satellite.set_3d_properties(Z[j])

    orbit_line.set_data(np.array(X[:j+1]), np.array(Y[:j+1]))
    orbit_line.set_3d_properties(np.array(Z[:j+1]))

    # update satellite ground track position

    satellite_gt.set_data([lon[j]], [lat[j]])

    return telemetry_text, satellite, orbit_line, vel_line, grav_line, acc_line, satellite_gt, gt_line

# creating Earth meshgrid (of lat and long)
u, v = np.meshgrid(np.radians(np.linspace(0, 360, 30)), np.radians(np.linspace(0, 180, 30)))
X_Egrid = R_E * np.cos(u) * np.sin(v)
Y_Egrid = R_E * np.sin(u) * np.sin(v)
Z_Egrid = R_E * np.cos(v)

# Earth topographic image
img = Image.open('images/earth_surface.jpeg')
img = img.resize((60, 60))
img_data = np.array(img) / 255.0 # normalize pixel colors to 0-1
ax1.plot_surface(X_Egrid, Y_Egrid, Z_Egrid, facecolors=img_data, rstride=1, cstride=1, antialiased=True)

# set limits
box_limit = 2 * R_E
ax1.set_xlim(-box_limit, box_limit)
ax1.set_ylim(-box_limit, box_limit)
ax1.set_zlim(-box_limit, box_limit)
ax1.set_box_aspect([1, 1, 1])

ax1.set_xlabel('X Axis (m)')
ax1.set_ylabel('Y Axis (m)')
ax1.set_zlabel('Z Axis (m)')
ax1.legend(loc="upper right")

# plot 2D ground track
try:
    img = plt.imread('images/Earthmap1000x500.jpg')
    ax2.imshow(img, extent=[-180, 180, -90, 90], aspect='auto', alpha=0.8)
except FileNotFoundError:
    ax2.grid(True, linestyle=':', alpha=0.8) 

# set limits and plot 2D groundtrack
ax2.set_xlim([-180, 180])
ax2.set_ylim([-90, 90])
ax2.set_xlabel('Longitude ($^\circ$)')
ax2.set_ylabel('Latitude ($^\circ$)')

# Format ticks with degree symbols
ax2.xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}°'))
ax2.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.0f}°'))

# animation
ani = FuncAnimation(fig, update, frames=len(X), interval=10, blit=True)
v_slider.on_changed(update_slider)
B_slider.on_changed(update_slider)
inc_slider.on_changed(update_slider)
J2_button.on_clicked(update_slider)
plt.show()