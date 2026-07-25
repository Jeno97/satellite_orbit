import serial
import time

# constants
G = 6.6743e-11 # m^3kg^-1s^-2
M_E = 5.9722e24 # kg
R_E = 6.378e6 # m

# Open serial port at standard baud rate of 115200 bits per s
# timeout gives 1s for Pico to reply, if not we return empty byte string
ser = serial.Serial('COM7', 115200, timeout = 1)

time.sleep(2) # 2 seconds to settle after opening
ser.reset_input_buffer()

print("--- HIL SIMULATION STARTED ---")

# simulate satellite falling
try:
    # send initial data to Pico
    t = 0
    alt = 300 # km
    vel = -0.1 # downward velocity
    dt = 0.5 # time step

    while alt > 0:

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

        # acceleration due to gravity
        a_g = -(G*M_E)/((R_E + (alt*1000))**2) / 1000 # convert g to km/s^2
        if "THRUSTER_ON" in resp:
            t_a = 0.020 # thruster acceleration
        else:
            t_a = 0

        total_a = a_g + t_a

        vel += (total_a * dt)
        alt += (vel * dt)
        t += dt

        # sleep
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopping simulation...")

finally:
    ser.close()
    print("Serial port closed safely.")