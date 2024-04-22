#!/usr/bin/env python2

import serial
import sys
import binascii
import time
import os
import platform
import struct

# use following command on the HX-20 BASIC to load
# LOAD"COM0:(68N13)"
# then use the RUN command to store the assembly program at memory location 0x1000
# to run the program, you can use the MONITOR command G1000 or the BASIC command EXEC&H1000
#
# if your program is bigger than 0x1000 bytes, you have to increase the MEMSET value
# (MEMSET defines the start address of BASIC)

if len(sys.argv) < 3:
  print "provide serial device and binary file name"
  sys.exit(-1)

serial_device = sys.argv[1]
file_name = sys.argv[2]

size = os.path.getsize(file_name)
offset = 0x1000
basic_code  = '0 MEMSET &H2000\r\n'
basic_code += '1 FOR I=&H'+format(offset,'X')+' TO &H'+format(offset+size-1,'X')+'\r\n'
basic_code += '2 READ A\r\n'
basic_code += '3 POKE I, A\r\n'
basic_code += '4 NEXT\r\n'

file_handle = open(file_name,"rb")
read_byte_count = 32
input_bytes = file_handle.read(read_byte_count)
line_counter = 5
while input_bytes != "":
  read_bytes = ''
  for byte in input_bytes:
    read_bytes += str(struct.unpack('B', byte)[0])+','
  basic_code += str(line_counter)+' DATA '+read_bytes[:-1]+'\r\n'
  input_bytes = file_handle.read(read_byte_count)
  line_counter += 1

serial_handle = serial.Serial(serial_device, 4800, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, rtscts=1)
# on the mac there seems to be an issue with the serial port
# it was not possible to reliabliy transport the data to the epson
# a workaround is this: write line by line and add some sleep between
if platform.system() == 'Darwin':
  for line in basic_code.splitlines():
    print(line)
    serial_handle.write(line+'\r\n')
    time.sleep(0.5)
else:
  serial_handle.write(basic_code)

serial_handle.flush()
file_handle.close()
serial_handle.close()
print("done")

