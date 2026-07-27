# using vpython to visualise the rocket falling

from vpython import canvas, box, cylinder, cone, vector, color, button, rate
import time
import os
import serial

# constants
G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m

# setup 3D canvas
scene = canvas(
    title="3D Spacecraft HIL Visualizer - Step 1 Test",
    width=900,
    height=600,
    background=color.black,
    center=vector(0,15,0)
    )

# Add an On-Screen STOP Button (CTRL-C not working)
def stop_simulation():
    print("\n[INFO] Stopped via UI button.")
    os._exit(0)

button(text="STOP SIMULATION", bind=stop_simulation)

# Scene shapes
ground = box(pos=vector(0, -1, 0), size=vector(60, 2, 60), color=color.gray(0.4))
landing_pad = cylinder(pos=vector(0, 0, 0), axis=vector(0, 0.2, 0), radius=10, color=color.yellow)

# rocket shape
body = cylinder(pos=vector(0, 0, 0), axis=vector(0, 10, 0), radius=1.2, color=color.cyan)
nose = cone(pos=vector(0, 10, 0), axis=vector(0, 3, 0), radius=1.2, color=color.red)
flame = cone(pos=vector(0, 0, 0), axis=vector(0, -4, 0), radius=1.0, color=color.orange, visible=False)

# update rocket
def set_spacecraft_state(alt, thruster_on):
    
    # scale to transition from physical units to 3D graphics units
    if alt > 1000:
        y_vis = 50 + (alt - 1000) * (250 / 19000)
    else:
        y_vis = alt * (50 / 1000)

    body.pos = vector(0, y_vis, 0)
    nose.pos = vector(0, y_vis+10, 0)
    flame.pos = vector(0, y_vis, 0)
    flame.visible = thruster_on

    scene.center = vector(0, y_vis+5, 0)

# communicate with the Pico
SERIAL_PORT = 'COM7'
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"Connected to Pico on {SERIAL_PORT}")
except Exception as e:
    print(f"Serial warning: Could not open {SERIAL_PORT} ({e})")
    print("Running in simulated fallback mode...")
    ser = None

# initial conditions
t = 0
alt = 10000 # m
vel = -0.0 # downward velocity
dt = 0.033 # time step
thruster_on = False
t_a = 0.0

while True:
    rate(30)

    if ser:
        
        # send data to the Pico        
        data_to_send = f"{t:.1f},{alt:.1f},{vel:.3f}\n"
        ser.write(data_to_send.encode('utf-8'))
        ser.flush()

        # print if laptop receives data
        raw_bytes = ser.readline()
        resp = raw_bytes.decode('utf-8').strip()
        
        # print response
        if resp:
            print(f"[SENT] {data_to_send.strip():<15} | [RECV] {resp}")
        else:
            print(f"[SENT] {data_to_send.strip():<15} | [RECV] NO RESPONSE (TIMEOUT)")        

        if "THRUSTER_ON" in resp:
            t_a = 50.0 # thruster acceleration
            thruster_on = True
        else:
            t_a = 0
            thruster_on = False

        if alt > 0:
            # acceleration due to gravity
            a_g = -(G*M_E)/((R_E + (alt))**2)
            total_a = a_g + t_a

            vel += (total_a * dt)
            alt += (vel * dt)
            t += dt
        else:
            alt = 0
            vel = 0
            thruster_on = False

        # update the 3D visualizer
        set_spacecraft_state(alt, thruster_on)