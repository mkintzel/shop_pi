# Shop Sensor Project
This project contains the Raspberry PI receiver and processing code for the Shop sensor project.
The code will listen to the attached RFM69 radio for an incoming packet and then process that packet
and send to NodeRed through MQTT.

Project now includes a batch version that sends messages via MQTT to NodeRed and a TTY version to run
at the command line 

