import sys
import uselect
from machine import Pin, SPI
import framebuf
import time

# Fast blink on startup so we know the script is working
led = Pin("LED", Pin.OUT)
for _ in range(3):
    led.value(1)
    time.sleep(0.05)
    led.value(0)
    time.sleep(0.05)

# dimensions of display
WIDTH = 160
HEIGHT = 80

# 16-bit RGB565 color hex values
BLACK    = 0x0000
WHITE    = 0xFFFF
CYAN     = 0x07FF
RED      = 0xF800
GREEN    = 0x07E0
DARKGRAY = 0x2104

# --- PHYSICAL BOARD PIN TO GPIO MAPPING ---
# Physical Pin 14 -> GP10 (SPI Clock)
# Physical Pin 15 -> GP11 (SPI Data / MOSI)
# Physical Pin 16 -> GP12 (Reset)
# Physical Pin 17 -> GP13 (Data / Command)
# Physical Pin 19 -> GP14 (Chip Select)

PHYSICAL_PIN_14 = 10  # GP10
PHYSICAL_PIN_15 = 11  # GP11
PHYSICAL_PIN_16 = 12  # GP12
PHYSICAL_PIN_17 = 13  # GP13
PHYSICAL_PIN_19 = 14  # GP14

# Initialize SPI1 at 30 MHz (clock on GP10, data/MOSI on GP11)
spi = SPI(1, baudrate=30000000, polarity=0, phase=0, sck=Pin(PHYSICAL_PIN_14), mosi=Pin(PHYSICAL_PIN_15))

# Control Pins
dc  = Pin(PHYSICAL_PIN_17, Pin.OUT) # Data / Command mode switcher
cs  = Pin(PHYSICAL_PIN_19, Pin.OUT) # Chip select
rst = Pin(PHYSICAL_PIN_16, Pin.OUT) # Hardware reset line

# --- 3. Low-Level SPI Helper Functions ---
def write_cmd(cmd):
    """Sends a single configuration COMMAND byte to the screen chip."""
    cs.value(0)        # Select screen (pull CS LOW)
    dc.value(0)        # Tell screen: "This is a Command, not pixel data" (pull DC LOW)
    spi.write(bytearray([cmd]))
    cs.value(1)        # Deselect screen (pull CS HIGH)

def write_data(data):
    """Sends a DATA byte (like color info or memory setup) to the screen."""
    cs.value(0)        # Select screen
    dc.value(1)        # Tell screen: "This is Data" (pull DC HIGH)
    spi.write(bytearray([data]))
    cs.value(1)        # Deselect screen

# --- 3. HARDWARE INIT & RAM BUFFER ---
OFFSET_X = 1 # need to shift to align as the driver uses 128x160 display
OFFSET_Y = 26

def init_display():
    # Hardware reset
    rst.value(0)
    time.sleep_ms(50)
    rst.value(1)
    time.sleep_ms(50)
    
    write_cmd(0x01) # Software Reset
    time.sleep_ms(150)
    write_cmd(0x11) # Sleep Out
    time.sleep_ms(200)
    
    write_cmd(0x3A) # Pixel Format
    write_data(0x05) # 16-bit RGB565
    
    write_cmd(0x36) # Memory Access Control (Orientation)
    write_data(0x68) 
    
    write_cmd(0x29) # Display ON
    time.sleep_ms(50)

init_display()

# Allocate memory in Pico RAM (160 x 80 x 2 bytes per pixel = 25.6 KB)
buffer = bytearray(160 * 80 * 2)

# Create the framebuf object instance named 'fb'
fb = framebuf.FrameBuffer(buffer, 160, 80, framebuf.RGB565)

def push_display():
    # 1. Apply hardware offsets to column (X) and row (Y) address setup
    x_start = OFFSET_X
    x_end   = OFFSET_X + WIDTH - 1
    y_start = OFFSET_Y
    y_end   = OFFSET_Y + HEIGHT - 1

    # Column Address Set (0x2A)
    write_cmd(0x2A)
    cs.value(0); dc.value(1)
    spi.write(bytearray([0x00, x_start, 0x00, x_end]))
    cs.value(1)

    # Row Address Set (0x2B)
    write_cmd(0x2B)
    cs.value(0); dc.value(1)
    spi.write(bytearray([0x00, y_start, 0x00, y_end]))
    cs.value(1)

    # 3. RAM Write Command (0x2C)
    write_cmd(0x2C)
    cs.value(0); dc.value(1)
    spi.write(buffer)
    cs.value(1)

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)
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
                
                # Display telemetry on the screen
                fb.fill(BLACK) # clear
                
                fb.fill_rect(0, 0, 160, 14, DARKGRAY)
                fb.text("HIL AVIONICS HUD", 14, 3, CYAN)
                
                fb.text(f"TIME: {sim_time:6.1f}s", 5, 20, WHITE)
                fb.text(f"ALT : {alt:6.0f}m", 5, 33, WHITE)
                fb.text(f"VEL : {vel:6.1f}m/s", 5, 46, WHITE)
                
                if alt <= 0.0:
                    # Touchdown confirmed (GREEN)
                    fb.fill_rect(5, 60, 150, 16, GREEN)
                    fb.text("TOUCHDOWN CONF", 18, 64, BLACK)
                elif thruster_active:
                    # Engine firing (RED)
                    fb.fill_rect(5, 60, 150, 16, RED)
                    fb.text("BURN: ACTIVE", 32, 64, WHITE)
                else:
                    # Freefall (DARK GRAY)
                    fb.fill_rect(5, 60, 150, 16, DARKGRAY)
                    fb.text("FREEFALL...", 38, 64, WHITE)
                
                # flush RAM buffer to LCD screen over SPI
                push_display()
                
        except (ValueError, IndexError):
            pass
