#!/usr/bin/env python3

from bitarray import bitarray
from bitarray.util import make_endian
from crccheck.crc import Crc16Kermit
from bitarray import bitarray

# done with tmS_06-07.pdf

def _get_byte(bits, bit_positions, status, offset):

  if offset+8 >= len(bits):
    _append_status(0, offset, bit_positions, status)
    print('reached end of data')
    return False

  # check if stop bit is set correctly
  if bits[offset+8] != 1:
    _append_status(0, offset, bit_positions, status)
    print("stop bit missing at "+str(bit_positions[offset]))
    return False

  return make_endian(bits[offset:offset+8], 'little').tobytes()[0]

def _append_status(status_value, offset, bit_positions, status):
  if len(bit_positions) > 0 and len(bit_positions) - 1 >= offset:
    status.append((status_value, bit_positions[offset]))

def extract_hx20_tape(bit_data, file_name):

  bits = bitarray([i[0] for i in bit_data])
  bit_positions = [i[1] for i in bit_data]

  status = []
  status.append((0,0))

  offset = 0

  # 40 or more zeros + 1 + 0xff with 1 stop bit + 0xaa with 1 stop bit (little endian)
  preamble = bitarray( 30 * '0' + '1' + '111111111' + '010101011')

  while True:

    # search for the preamble
    preamble_match = bits.find(preamble, offset)
    if preamble_match == -1:
      _append_status(0, offset, bit_positions, status)
      print('preamble not found')
      _append_status(0, len(bits) - 1, bit_positions, status)
      return status;
    print('preamble match = ' + str(bit_positions[preamble_match]))
    _append_status(1, preamble_match, bit_positions, status)

    # extract block
    block_bytes = bytearray()

    offset = preamble_match + len(preamble)
    block_type = _get_byte(bits, bit_positions, status, offset)
    block_bytes.append(block_type)
    # header ('H' = 0x48) and eof ('E' = 0x45) blocks are 80 bytes, data blocks ('D' = 0x44) are 256 bytes
    if block_type == ord('H'):
      block_size = 80
    elif block_type == ord('E'):
      block_size = 80
    elif block_type == ord('D'):
      block_size = 256
    else:
      _append_status(0, offset, bit_positions, status)
      print('invalid block type: ' + hex(block_type))
      continue
    print('block type = ' + hex(block_type))

    offset += 9
    block_number_1 = _get_byte(bits, bit_positions, status, offset)
    block_bytes.append(block_number_1)
    offset += 9
    block_number_2 = _get_byte(bits, bit_positions, status, offset)
    block_bytes.append(block_number_2)
    block_number = (block_number_1 << 8) + block_number_2;
    print('block number = ' + hex(block_number))
    offset += 9
    block_copy = _get_byte(bits, bit_positions, status, offset)
    block_bytes.append(block_copy)
    print('block copy = ' + hex(block_copy))

    block_data_bytes = bytearray()

    print('block size = ' + str(block_size) + ' bytes')
    for i in range(block_size):
      offset += 9
      data = _get_byte(bits, bit_positions, status, offset)
      block_bytes.append(data)
      block_data_bytes.append(data)
      #print('data '+str(i)+' = '+hex(data)+' '+chr(data))

    offset += 9
    block_crc_1 = _get_byte(bits, bit_positions, status, offset)
    offset += 9
    block_crc_2 = _get_byte(bits, bit_positions, status, offset)
    block_crc = (block_crc_2 << 8) + block_crc_1;
    print('block crc = ' + hex(block_crc))

    crc = Crc16Kermit.calc(block_bytes)
    print('calculated crc = ' + hex(crc))

    crc_status = 'OK'
    if block_crc != crc:
      _append_status(0, offset, bit_positions, status)
      print('crc mismatch')
      crc_status = 'ERROR'
 
    format_string = '{:0' + str(len(str(bit_positions[-1]))) + 'd}'
    block_data_file_path = file_name + '_' + format_string.format(int(bit_positions[preamble_match])) + '_' + chr(block_type) + '_' + str(block_number) + '_' + str(block_copy) + '_' + crc_status + '.block'
    print('writing block data file: ' + block_data_file_path)
    block_file = open(block_data_file_path, 'wb')
    block_file.write(block_data_bytes)
    block_file.close()

    offset += 9
    if _get_byte(bits, bit_positions, status, offset) != 0xaa:
      _append_status(0, offset, bit_positions, status)
      print("first part of postamble not found")
    offset += 9
    if _get_byte(bits, bit_positions, status, offset) != 0x00:
      _append_status(0, offset, bit_positions, status)
      print("second part of postamble not found")
    offset += 9
    _append_status(0, offset, bit_positions, status)
    print()

  return status
