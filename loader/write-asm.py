#!/usr/bin/env python2

import serial
import sys
import binascii
import time
import platform

# use the LOADER program on the HX-20 to receive and store the transmited data
# make sure you increase the start address of BASIC with the MEMSET command
# if you have a big assembly program

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
  # on mac i need the 0.002 sleep, else data is not transferred correctly
  if platform.system() == 'Darwin':
    time.sleep(0.002)
  sys.stdout.write(binascii.hexlify(input_byte))
  sys.stdout.flush()
  input_byte = file_handle.read(1)

serial_handle.flush()
serial_handle.close()
file_handle.close()
print('')
print('done')
