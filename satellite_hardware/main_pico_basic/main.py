import sys
import uselect
from machine import Pin
import time

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

led = Pin("LED", Pin.OUT)

# Fast blink on startup so we know the script is working
for _ in range(3):
    led.value(1)
    time.sleep(0.05)
    led.value(0)
    time.sleep(0.05)

thruster_active = False

while True:
    if poll.poll(10):
        try:
            line = sys.stdin.readline().strip()
        
            if not line:
                continue
            
            parts = line.split(",")
            if len(parts) >= 3:
                sim_time = float(parts[0])
                alt = float(parts[1])
                vel = float(parts[2])
                
                if alt <= 5000:
                    if vel <= -50.0:
                        thruster_active = True
                    elif vel >= -1.0:
                        thruster_active = False
                else:
                    thruster_active = False # dont turn on above 200km

                # Drive hardware directly with the boolean
                led.value(thruster_active)
                event_status = "THRUSTER_ON" if thruster_active else "THRUSTER_OFF"
                  
                # Send response back over USB serial                    
                sys.stdout.write(f"ACK,{sim_time:.1f},{alt:.1f},{event_status}\n")

                
        except (ValueError, IndexError):
            pass
