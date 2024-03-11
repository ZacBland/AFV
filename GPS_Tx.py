# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 17:04:12 2024

@author: alexm

Description: To run on BeeLink onboard AFV. Extracts GPS information from 
             GLONASS U-blox 7 USB GPS module, parses data, and sends data
             over RFD900x telemetryy module. 
"""

import serial
import pynmea2
import json

# GPS Module Connection
gps_port = "COM12"  # Replace with your COM port for GPS module
gps_ser = serial.Serial(gps_port, baudrate=9600, timeout=1)

# RFD900x Module Connection
rfd_port = "COM13"  # Replace with your COM port for RFD900x module
rfd_ser = serial.Serial(rfd_port, baudrate=57600, timeout=1)  # Assuming 57600 baud rate for RFD900x

while True:
    data_out = gps_ser.readline().decode('ascii', errors='ignore').strip()

    # Print raw NMEA sentence for debugging
    print(f"Raw NMEA Sentence: {data_out}")
        
    if data_out.startswith('$GPRMC'):
        try:
            msg = pynmea2.parse(data_out)
            nav_data = {
                'time': str(msg.timestamp) if msg.timestamp else "Unavailable",
                'latitude': msg.latitude if msg.latitude != 0.0 else "Unavailable",
                'longitude': msg.longitude if msg.longitude != 0.0 else "Unavailable",
                'speed': msg.spd_over_grnd if msg.spd_over_grnd is not None else "Unavailable",
                'course': msg.true_course if msg.true_course is not None else "Unavailable",
                'date': msg.datestamp if msg.datestamp else "Unavailable",
                'status': msg.status if msg.status else "Unavailable",  # 'A' = Data Valid, 'V' = Navigation receiver warning
            }
            json_nav_data = json.dumps(nav_data)
            print(json_nav_data)

           # Send JSON navigation data over RFD900x connection
            rfd_ser.write(json_nav_data.encode('ascii') + b'\n')

        except pynmea2.ParseError as e:
            print(f"Parse error: {e}")
            continue


