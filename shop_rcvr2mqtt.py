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
# Import the JSON module
import json
# Import the mqtt module
import paho.mqtt.client as mqtt

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Define radio parameters.
# Frequency of the raio in Mhz.  Must match
RADIO_FREQ_MHZ = 915.0

# set GPIO pins as nessessary for the radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)

# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, RADIO_FREQ_MHZ)

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
#rfm69.encryption_key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08'
rfm69.encryption_key = b'\x00\x06\x01\x08\x01\x09\x07\x00\x00\x01\x02\x03\x01\x09\x07\x01'

# set delay before transmitting ACK (seconds)
rfm69.ack_delay = 0.1
# set node addresses
rfm69.node = 7
rfm69.destination = 5
# initialize counter
counter = 0
ack_failed_counter = 0

execution_loop = True
while execution_loop:
    packet = None
    # check for packet rx
    packet = rfm69.receive(with_ack=True, with_header=True)

    if packet is not None:
        # Display the packet text and rssi
        # Print out the raw bytes of the packet:
#        print("Received (raw header):", [hex(x) for x in packet[0:4]])
#        print("Received (ray payload):  {0}".format(packet[4:]))
#        print("RSSI: {0}".format(rfm69.last_rssi))

        packet_text = str(packet[4:], "utf-8")

        # Extract the sensor data from the string
        x = packet_text.split(",")
        fDegC = float(x[0])
        fBackDegC = float(x[1])
        fPressure = float(x[2])

        # Convert C to F
        fDegF = (fDegC * 9 / 5) + 32
        fBackDegF = (fBackDegC * 9 / 5) + 32

        # Create a dictionary object
        sensor_dict = {
            "front_temp": round(fDegF, 1),
            "back_temp": round(fBackDegF, 1),
            "pressure": round(fPressure, 1),
            "sensor": packet[1],
            "RSSI": rfm69.last_rssi,
            "sequence": hex(packet[2]),
            "status": hex(packet[3])
        }

        # Create a JSON string from the disctionary object
        sensor_json = json.dumps(sensor_dict)
#        print(sensor_json)
#        print("\n")

        # Publish MQTT message
        ourClient = mqtt.Client("kintzel_mqtt")  # Create a MQTT client object
        ourClient.connect("192.168.12.27", 1883)  # Connect to the test MQTT broker
        ourClient.publish("shop", sensor_json)

        time.sleep(5)


