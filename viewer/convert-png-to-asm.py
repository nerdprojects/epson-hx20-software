#!/usr/bin/env python2

from PIL import Image
import sys

if len(sys.argv) < 2:
  print "provide 120x32 grayscale png-8 image"
  sys.exit(-1)

image = Image.open(sys.argv[1])
pixels = image.load()
i = 0
for y in [0,8,0,8,0,8,16,24,16,24,16,24]:

  fcb_statement = '        FCB     '

  if i in (0,1,6,7):
    start_range = 0
    end_range = 40

  if i in (2,3,8,9):
    start_range = 40
    end_range = 80

  if i in (4,5,10,11):
    start_range = 80
    end_range = 120

  for x in range(start_range,end_range):
    byte = 0
    for bit in range(8):
      if pixels[x,y+bit] < 127:
        # toggle the bit if pixel is set
        mask = 1 << bit
        byte |= mask
    fcb_statement += str(byte)+','

  i += 1

  print(fcb_statement[:-1])


