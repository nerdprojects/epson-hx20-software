#!/usr/bin/env python3

import sys
import glob

def parseFileName(block_file_name):
  file = open(block_file_name,'rb')
  data = file.read(80)
  data_name = data[4:15]
  data_type = data[15]
  data_encoding = data[16]
  
  block_file_name = data_name.decode('ascii').strip()
  # TODO: implement complete german code table
  #       add functionality for other code tables
  block_file_name = block_file_name.replace('[', 'Ä')
  block_file_name = block_file_name.replace('\\', 'Ö')
  block_file_name = block_file_name.replace(']', 'Ü')
  block_file_name = block_file_name.replace('{', 'ä')
  block_file_name = block_file_name.replace('|', 'ö')
  block_file_name = block_file_name.replace('}', 'ü')

  # replace invalid linux path character
  block_file_name = block_file_name.replace('/', '_')

  if data_encoding == 0:
    block_file_name += '.BIN'

  if data_type == 0:
    block_file_name += '.BAS'
  elif data_type == 1:
    block_file_name += '.DATA'
  elif data_type == 2:
    block_file_name += '.ASM'

  return block_file_name

def loadFileData(block_file_name):
  file = open(block_file_name, 'rb')
  return file.read(256)

if len(sys.argv) < 2:
  print('Usage: merge-blocks.py input-file-prefix')
  sys.exit()

input_file_prefix = sys.argv[1]
input_files = sorted(glob.glob(input_file_prefix + '*.block'))

output_file = None
output_file_name = None
output_data = bytearray()

last_good_number = -1
error = False

i = 0
for input_file_name in input_files:
  i += 1
  input_file_parts = input_file_name[len(input_file_prefix) + 1:-len('.block')].split('_')
  #print(input_file_parts)

  #if i == len(input_files):
    #print('reached end of files')

  if len(input_file_parts) > 5:
    #print('file name parse error')
    continue

  offset = input_file_parts[0]
  block_type = input_file_parts[1]
  number = int(input_file_parts[2])
  copy = input_file_parts[3]
  status = input_file_parts[4]

  if status != 'OK':
    #print('block not OK')
    continue

  if last_good_number == number:
    #print('block number is the same as previous block number')
    continue

  print('- ' + input_file_name)

  if number != 1 and last_good_number + 1 != number:
    error = True

  if block_type == 'H':
    error = False
    last_good_number = -1
    output_data = bytearray()
    output_file_name = parseFileName(input_file_name)
    print('Found header block with file ' + output_file_name)
    if output_file is not None:
      print('Writing file ' + output_file_name)
      output_file.write(output_data)
      output_file.close()

  elif block_type == 'D':
    output_data.extend(loadFileData(input_file_name))

  elif block_type == 'E':
    print('Found END header block, ', end = '')

    if error:
      print('error is present in the block sequence, will not save file')
      continue

    if output_file_name is None:
      output_file_name = parseFileName(input_file_name)
      print('parsed file name ' + output_file_name + ' from end header block, ', end = '')
    print('writing file ' + input_file_prefix + '_' + offset + '_' + output_file_name)
    output_file = open(input_file_prefix + '_' + offset + '_' + output_file_name, 'wb')
    output_file.write(output_data)
    output_file.close()
    output_file = None

  last_good_number = number


