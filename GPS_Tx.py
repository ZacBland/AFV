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
gps_ser = serial.Serial(gps_port, baudrate=9600, timeout=1) # 9600 baud rate for u-blox 7

# RFD900x Module Connection
rfd_port = "COM13"  # Replace with your COM port for RFD900x module
rfd_ser = serial.Serial(rfd_port, baudrate=57600, timeout=1)  # 57600 baud rate for RFD900x

while True:
    data_out = gps_ser.readline().decode('ascii', errors='ignore').strip()

    # Print raw NMEA sentence for debugging
    print(f"Raw NMEA Sentence: {data_out}")

    if data_out.startswith('$GPGGA'):
        try:
            msg = pynmea2.parse(data_out)
            coord_data = {
                'time': str(msg.timestamp) if msg.timestamp else "Unavailable",
                'latitude': msg.latitude if msg.latitude != 0.0 else "Unavailable",
                'longitude': msg.longitude if msg.longitude != 0.0 else "Unavailable",
                'altitude': msg.altitude if msg.altitude is not None else "Unavailable",
                'altitude_units': msg.altitude_units if msg.altitude_units else "Unavailable",
                'fix_type': msg.gps_qual,
                'hdop': msg.horizontal_dil if msg.horizontal_dil is not None else "Unavailable"
            }
            json_coord_data = json.dumps(coord_data)
            print(json_coord_data)

            # Send JSON coordinate data over RFD900x connection
            rfd_ser.write(json_coord_data.encode('ascii') + b'\n')

        except pynmea2.ParseError as e:
            print(f"Parse error: {e}")
            continue
          
    elif data_out.startswith('$GPVTG'):
        try:
           msg = pynmea2.parse(data_out)
           speed_direction_data = {
               'true_track_degrees': float(msg.true_track) if msg.true_track is not None else "Unavailable",
               'magnetic_track_degrees': float(msg.mag_track) if msg.mag_track is not None else "Unavailable",
               'speed_knots': float(msg.spd_over_grnd_kts) if msg.spd_over_grnd_kts is not None else "Unavailable",
               'speed_kph': float(msg.spd_over_grnd_kmph) if msg.spd_over_grnd_kmph is not None else "Unavailable"
               }
           json_speed_direction_data = json.dumps(speed_direction_data)
           print(json_speed_direction_data)

           # Send JSON speed and direction data over RFD900x connection
           rfd_ser.write(json_speed_direction_data.encode('ascii') + b'\n')

        except pynmea2.ParseError as e:
            print(f"Parse error: {e}")
            continue



