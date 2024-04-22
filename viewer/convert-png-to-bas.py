#!/usr/bin/env python2

from PIL import Image
import sys

if len(sys.argv) < 2:
  print "provide 120x32 grayscale png-8 image"
  sys.exit(-1)

image = Image.open(sys.argv[1])
pixels = image.load()

basic_code  = '00 CLS\r\n'
basic_code += '10 FOR Y=0 TO 31 STEP 1\r\n'
basic_code += '20 FOR X=0 TO 119 STEP 1\r\n'
basic_code += '30 READ P\r\n'
basic_code += '40 IF P = 1 THEN PSET(X,Y)\r\n'
basic_code += '50 NEXT\r\n'
basic_code += '60 NEXT\r\n'
basic_code += '70 EXEC &HFF9A\r\n' # 0xFF9A is the BIOS routine KEYIN, which blocks until a key is pressed
basic_code += '80 CLS\r\n'
counter = 80
for y in range(32):
  counter = counter + 10
  data_statement = str(counter) + ' DATA '
  for x in range(120):
    if pixels[x,y] < 127:
      data_statement += '0,'
    else:
      data_statement += '1,'
  data_statement = data_statement[:-1] + '\r\n'
  basic_code += data_statement

print(basic_code)
