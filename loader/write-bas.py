#!/usr/bin/env python2

import serial
import sys
import binascii
import time
import platform

# use following command on the HX-20 to load
# LOAD"COM0:(68N13)"

if len(sys.argv) < 3:
  print "provide serial device and file name"
  sys.exit(-1)

serial_device = sys.argv[1]
file_name = sys.argv[2]
serial_handle = serial.Serial(serial_device, 4800, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, rtscts=1)
file_handle = open(file_name,"rb")
input_byte = file_handle.read(1)
while input_byte != "":
  serial_handle.write(input_byte)
  # for the mac, i needed to add a delay after every line
  # i think on the mac, there might be something wrong with the serial port configuration or the FTDI driver,
  # not sure...
  if platform.system() == 'Darwin':
    if(input_byte == '\n'):
      time.sleep(0.5)
  sys.stdout.write(input_byte)
  sys.stdout.flush()
  input_byte = file_handle.read(1)

serial_handle.flush()
file_handle.close()
serial_handle.close()
