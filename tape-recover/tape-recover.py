#!/usr/bin/env python3

import sys
import os
from scipy.io import wavfile
from decode_functions import decode_zerocross 
from decode_functions import decode_peak_old
from decode_functions import decode_peak
from extract_functions import extract_hx20_tape

def write_bits_file(bits, file_name):
  print('Writing bitfile ' + file_name)
  bits_text_file = open(file_name, 'w')
  bits_text_file.write(bits.to01())
  bits_text_file.close()

def print_usage():
  usage_string = '''Usage: tape-recover.py zerocross <wav-file> [dc-offset=0.0] [plot] [bitfile]
       tape-recover.py peak <wav-file> [peak-threshold=0.2] [plot] [bitfile]
       tape-recover.py bitfile <bit-file>'''
  print(usage_string)

if len(sys.argv) < 3:
  print('Error: Not enough arguments')
  print_usage()
  sys.exit(1)

operation = sys.argv[1]
if operation != 'peak' and operation != 'zerocross' and operation != 'bitfile':
  print('Error: Invalid operation "' + operation + '"')
  print_usage()
  sys.exit(1)

input_file_path = sys.argv[2]
input_name = os.path.basename(input_file_path).split('.')[0]

if operation == 'bitfile':
  from bitarray import bitarray
  input_file = open(input_file_path, 'r')
  bit_data = input_file.read()
  bits = bitarray(bit_data)
  extract_hx20_tape(bits, range(0, len(bits)), input_name)
  sys.exit(0)

import numpy
samplerate, data = wavfile.read(input_file_path)
channels = len(data.shape)
if channels != 1:
  print('Error: Only mono wav files supported.')
  sys.exit(1)

# normalize
if data.dtype == numpy.uint8:
  data = data / 127
  data = data - 1
elif data.dtype == numpy.int16:
  data = data / 32767
elif data.dtype == numpy.int32:
  data = data / 2147483647

if operation == 'zerocross':
  dc_offset = 0
  if len(sys.argv) > 3:
    try:
      dc_offset = float(sys.argv[3])
    except ValueError:
      print('Error: Invalid dc-offset value "' + sys.argv[3] + '"')
      print_usage()
      sys.exit()

  bit_data, filtered_data, frequency_difference_data = decode_zerocross(data, samplerate, dc_offset)
  bit_values = [i[0] for i in bit_data]

  status_data = extract_hx20_tape(bit_data, input_name)

  if len(sys.argv) > 4 and sys.argv[4] == 'plot':
    import matplotlib.pyplot as plt
    import numpy
    data = data + dc_offset

    bit_positions = [i[1] for i in bit_data]
    bit_positions = bit_positions[:len(bit_positions)-1]
    bit_plot_values = numpy.array(bit_values)[1:] * 0.25 - 0.125

    status_positions = [i[1] for i in status_data]
    status_values = [i[0] for i in status_data]
    status_values = numpy.array(status_values) * 0.5 - 0.25

    frequency_difference_positions = [i[1] for i in frequency_difference_data]
    frequency_difference_values = [i[0] for i in frequency_difference_data]
    frequency_difference_values = numpy.array(frequency_difference_values) * 0.5

    plt.axhline(y=0.0, color='black', linestyle='-')
    plt.plot(range(0, len(data)), data, label='Original')
    plt.plot(range(0, len(filtered_data)), filtered_data, label='Filtered')
    plt.plot(bit_positions, bit_plot_values, drawstyle='steps-post', label='Bits')
    plt.plot(status_positions, status_values, drawstyle='steps-post', label='Status')
    plt.plot(frequency_difference_positions, frequency_difference_values, label='Frequency Difference')
    plt.legend(loc='upper right')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.show()

  if len(sys.argv) > 5 and sys.argv[5] == 'bitfile':
    from bitarray import bitarray
    write_bits_file(bitarray(bit_values), input_name + '.bits.txt')

if operation == 'peak':
  peak_threshold = 0.2
  if len(sys.argv) > 3:
    try:
      peak_threshold = float(sys.argv[3])
    except ValueError:
      print('Error: Invalid peak-threshold value "' + sys.argv[3] + '"')
      print_usage()
      sys.exit()

  bit_data, lowpass_data, peak_data, peak_threshold_data, frequency_difference_data = decode_peak(data, samplerate, peak_threshold)

  bit_values = [i[0] for i in bit_data]

  status_data = extract_hx20_tape(bit_data, input_name)
  if len(sys.argv) > 4 and sys.argv[4] == 'plot':
    import matplotlib.pyplot as plt
    import numpy

    peaks = [i[0] for i in peak_data]
    peak_positions = [i[1] for i in peak_data]

    peak_thresholds = [i[0] for i in peak_threshold_data]
    peak_threshold_positions = [i[1] for i in peak_threshold_data]

    bit_positions = [i[1] for i in bit_data]
    bit_plot_values = numpy.array(bit_values) * 0.25 - 0.125

    status_positions = [i[1] for i in status_data]
    status_values = [i[0] for i in status_data]
    status_values = numpy.array(status_values) * 0.5 - 0.25

    frequency_difference_positions = [i[1] for i in frequency_difference_data]
    frequency_difference_values = [i[0] for i in frequency_difference_data]
    frequency_difference_values = numpy.array(frequency_difference_values) * 0.5

    plt.axhline(y=0.0, color='black', linestyle='-')
    #plt.plot(range(0, len(data)), data, label='Original')
    plt.plot(range(0, len(lowpass_data)), lowpass_data, label='Lowpass')
    plt.plot(bit_positions, bit_plot_values, drawstyle='steps-post', label='Bits')
    plt.plot(status_positions, status_values, drawstyle='steps-post', label='Status')
    #plt.plot(peak_positions, peaks, label='Peak')
    plt.plot(peak_threshold_positions, peak_thresholds, label='Peak Threshold')
    plt.plot(frequency_difference_positions, frequency_difference_values, label='Frequency Difference')
    plt.legend(loc='upper right')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.show()

  if len(sys.argv) > 5 and sys.argv[5] == 'bitfile':
    from bitarray import bitarray
    write_bits_file(bitarray(bit_values), input_name + '.bits.txt')

