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

def main():
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
    rfm69.encryption_key = b'\x00\x06\x01\x08\x01\x09\x07\x00\x00\x01\x02\x03\x01\x09\x07\x01'

    # set delay before transmitting ACK (seconds)
    rfm69.ack_delay = 0.1
    # set node addresses
    rfm69.node = 7
    rfm69.destination = 5
    # initialize counter
    counter = 0
    ack_failed_counter = 0
    display_temps = False

    execution_loop = True
    while execution_loop:
        packet = None
        # check for packet rx
        packet = rfm69.receive(with_ack=True, with_header=True)

        if packet is not None:
            # Display the packet text and rssi
            # Print out the raw bytes of the packet:
            # print("Received (raw header):", [hex(x) for x in packet[0:4]])
            # print("Received (ray payload):  {0}".format(packet[4:]))
            # print("RSSI: {0}".format(rfm69.last_rssi))

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
            #print(sensor_json)

            # Publish MQTT message
            mqtt.Client.connected_flag = False
            broker = "192.168.12.27"

            client = mqtt.Client("sensor_rfm69_mqtt")  # Create a MQTT client object
            client.username_pw_set(username="kintzel_mqtt", password="Bl00d$ucker")
            client.on_connect = on_connect  # bind call back function
            client.loop_start()  # Start loop
            # print("Connecting to broker ", broker)

            client.connect(broker, port=1883, keepalive=60, bind_address="")
            while not client.connected_flag:
                time.sleep(1)

            client.publish("shop", sensor_json)

            client.loop_stop()  # Stop loop
            client.disconnect()

            # Check the board buttons
            #   - If Button A has been pressed - display the temps
            #   - If Button B or C has been pressed - clear the display
            if not btnA.value:
                # Button A Pressed
                display_temps = True
            elif not btnB.value:
                # Button B Pressed
                display_temps = False
                display.text("B - Going Dark!", 10, display_line2, 1)
                display.show()
            elif not btnC.value:
                # Button C Pressed
                display_temps = False
                display.text("C - Going Dark!", 10, display_line2, 1)
                display.show()

            if display_temps:
                display.text("Front Room:  " + str(round(fDegF, 1)), 5, display_line1, 1)
                display.text(" Back Room:  " + str(round(fBackDegF, 1)), 5, display_line2, 1)
                display.text("      RSSI: " + str(rfm69.last_rssi), 5, display_line3, 1)
                display.show()

            time.sleep(10)

            # Clear the display and lets do it again
            display.fill(0)
            display.show()


def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        #print("connected OK Returned code=",rc)
    #else:
        #print("Bad connection Returned code=", rc)


if __name__ == "__main__":
    main()


