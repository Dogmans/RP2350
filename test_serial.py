#!/usr/bin/env python3
import serial
import time

try:
    ser = serial.Serial('COM7', 115200, timeout=2)
    print(f"✓ Connected to {ser.port} @ {ser.baudrate} baud")
    
    # Try to read some data
    print("Listening for 5 seconds...")
    start = time.time()
    while time.time() - start < 5:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"  RX: {data}")
    
    ser.close()
    print("✓ Serial connection test complete")
except Exception as e:
    print(f"✗ Error: {e}")
