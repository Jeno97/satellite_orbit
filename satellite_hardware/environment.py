import serial
import time

# Open serial port at standard baud rate of 115200 bits per s
# timeout gives 1s for Pico to reply, if not we return empty byte string
ser = serial.Serial('COM7', 115200, timeout = 1)

time.sleep(2) # 2 seconds to settle after opening
ser.reset_input_buffer()

print("--- HIL SIMULATION STARTED ---")

# simulate satellite falling
try:
    for i in range(500, -5, -5):
        
        # send data to Pico
        sim_time = float((500-i)/5)
        alt = float(i)

        data_to_send = f"{sim_time:.1f},{alt:.1f}\n"
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

        # sleep
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopping simulation...")

finally:
    ser.close()
    print("Serial port closed safely.")