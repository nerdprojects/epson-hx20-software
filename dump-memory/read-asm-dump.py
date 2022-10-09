#!/usr/bin/env python3

import serial
import sys

if len(sys.argv) < 3:
  print('provide serial device and file name')
  sys.exit(-1)

serial_device = sys.argv[1]
file_name = sys.argv[2]
file_handle = open(file_name,'wb')
ser = serial.Serial(serial_device, 4800, parity=serial.PARITY_NONE, rtscts=1, bytesize=8, stopbits=1)
counter = 0
while True:
  input_bytes = ser.read(1)
  counter += 1
  print(input_bytes.hex(), end=' ')
  if counter % 16 == 0:
    print('')
    print('{:04x}: '.format(counter), end='')
  sys.stdout.flush()
  file_handle.write(input_bytes)

file_handle.close()
