"""
sensor_rfm69.py

My first attempt to create a sensor receiver

Author: Mark Kintzel
"""
#############################################################################
# Libraries
#############################################################################
# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM69 radio module.
import adafruit_rfm69

#############################################################################
# Initialize RFM69 Board
#############################################################################
# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()

# Set up some variables to help with writing to the display
display_width = display.width
display_height = display.height
display_line1 = 0
display_line2 = 12
display_line3 = 24

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
#rfm69.encryption_key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08'
rfm69.encryption_key = b'\x00\x06\x01\x08\x01\x09\x07\x00\x00\x01\x02\x03\x01\x09\x07\x01'

# Provide some instructions before continuing into the Execution Loop
display.text('sensor_rfm69.py', 0, display_line1, 1)
display.text('A = Continue', 10, display_line2, 1)
display.text('C = Exit', 10, display_line3, 1)
display.show()

execution_loop = True
wait2start = True
while wait2start:
    # Wait until Button A or C is pressed
    if not btnA.value:
        # Button A Pressed
        wait2start = False
        time.sleep(0.2)

    if not btnC.value:
        # Button C Pressed - never enter the execution loop & exit
        display.fill(0)
        display.text('Clean  Up & Exit', 10, display_line2, 1)
        display.show()
        time.sleep(0.5)

        execution_loop = False
        wait2start = False

    time.sleep(0.1)


while execution_loop:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi Radio', 35, display_line1, 1)

    # check for packet rx
    packet = rfm69.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 10, display_line3, 1)
    else:
        # Display the packet text and rssi
        display.fill(0)
        # Print out the raw buytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        prev_packet = packet
        packet_text = str(prev_packet, "utf-8")
#        packet_text = str(prev_packet, "ascii")
        display.text('RX: ', 0, display_line2, 1)
        display.text(packet_text, 25, display_line2, 1)
        time.sleep(1)

    if not btnA.value:
        # Send Button A
        display.fill(0)
        button_a_data = bytes("Button A!\r\n","utf-8")
        rfm69.send(button_a_data)
        display.text('Sent Button A!', 25, display_line2, 1)
    elif not btnB.value:
        # Send Button B
        display.fill(0)
        button_b_data = bytes("Button B!\r\n","utf-8")
        rfm69.send(button_b_data)
        display.text('Sent Button B!', 25, display_line2, 1)
    elif not btnC.value:
        # Button C Pressed
        display.fill(0)
        display.text('Clean  Up & Exit', 10, display_line2, 1)
        display.show()
        time.sleep(0.5)
        execution_loop = False

    display.show()
    time.sleep(0.1)

    # Clear the screen and exit
display.fill(0)
display.show()


