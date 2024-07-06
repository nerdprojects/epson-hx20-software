#!/usr/bin/env python3

import serial
import sys
import binascii
import time
import platform

# use following command on the HX-20 to load
# LOAD"COM0:(68N13)"

if len(sys.argv) < 3:
  print('provide serial device and file name')
  sys.exit(-1)

serial_device = sys.argv[1]
file_name = sys.argv[2]
serial_handle = serial.Serial(serial_device, 4800, bytesize = 8, parity = serial.PARITY_NONE, stopbits = 1, rtscts = 1)
file_handle = open(file_name, 'rb')
input_byte = file_handle.read(1)
while input_byte:
  serial_handle.write(input_byte)
  # the HX-20 Basic seems to need some time to interpret or storing the data we send,
  # which can result in a "BO Error" if we send it too fast, therefore we delay here
  time.sleep(0.01)

  character = '.'
  try:
    character = input_byte.decode('ascii')
  except UnicodeDecodeError:
    pass

  sys.stdout.write(character)
  sys.stdout.flush()
  input_byte = file_handle.read(1)

print('done')
serial_handle.flush()
file_handle.close()
serial_handle.close()
