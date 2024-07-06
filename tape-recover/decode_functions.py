#!/usr/bin/env python3

import numpy
from bitarray import bitarray
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter, freqz

def butter_lowpass(cutoff, fs, order=5):
  return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

def butter_highpass(cutoff, fs, order=5):
  return butter(order, cutoff, fs=fs, btype='high', analog=False)

def butter_highpass_filter(data, cutoff, fs, order=5):
  b, a = butter_highpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

def decode_zerocross(data, sample_rate, dc_offset):

  bit_data = []
  frequency_difference_data = []

  sample_count = len(data)

  cutoff = 2000
  order = 1
  filtered_data = butter_lowpass_filter(data, cutoff, sample_rate, order)
  filtered_data = data

  # we use a high pass filter to remove dc offsets from the signal
  cutoff = 2000
  order = 1
  filtered_data = butter_highpass_filter(filtered_data, cutoff, sample_rate, order)

  waveform_start = 0
  waveform_last_start = 0

  last_sample_value = 0
  current_sample_value = 0

  # iterate over all samples and fill the bitarray
  for sample_number in range(sample_count):

    # update progess every 10000 samples:
    if sample_number % 10000 == 0:
      percent_done = sample_number / sample_count * 100
      print('decoding zerocross: ' + str(int(percent_done)) + '% done', end='\r')

    last_sample_value = current_sample_value
    current_sample_value = filtered_data[sample_number] + dc_offset
    #print(str(current_sample_value))

    # detect waveform start, by zero cross
    if current_sample_value >= 0.0 and last_sample_value < 0.0:
      waveform_last_start = waveform_start
      waveform_start = sample_number

      waveform_sample_count = sample_number - waveform_last_start
      # bail out to prevent devision by zero
      if waveform_sample_count <= 0:
        continue

      waveform_frequency = sample_rate / waveform_sample_count
      #print(' waveform length '+str(waveform_frequency)+' '+str(waveform_sample_count))
      # if we have a 1khz wave, we have a 1
      if waveform_frequency > 800 and waveform_frequency < 1400:
        bit_data.append((1, sample_number))
        frequency_difference_data.append((waveform_frequency / 1000 - 1, sample_number))
      
      # if we have a 2khz wave, we have a 0
      elif waveform_frequency > 1400 and waveform_frequency < 2600:
        bit_data.append((0, sample_number))
        frequency_difference_data.append((waveform_frequency / 2000 - 1, sample_number))

  print()
  return bit_data, filtered_data, frequency_difference_data

def decode_peak_old(data, sample_rate, peak_threshold):

  # previous version of the peak algorithm
  # the new one seems to have only advantages over the old one

  bit_data = []
  peak_data = []

  cutoff = 1000
  order = 6
  lowpass_data = butter_lowpass_filter(data, cutoff, sample_rate, order)

  sample_count = len(data)

  peak_start = 0
  peak_last_start = 0
  last_sample = 0
  current_sample = 0

  frequency = 1000.0

  # iterate over all samples and fill the bit data
  for sample_number in range(sample_count):

    peak_data.append((0,sample_number))

    # update progess every 10000 samples:
    if sample_number % 10000 == 0:
      percent_done = sample_number / sample_count * 100
      print('decoding peak: ' + str(int(percent_done)) + '% done', end='\r')

    last_sample = current_sample
    current_sample = lowpass_data[sample_number]

    # we ignore everything thats below the peak value
    if current_sample < peak_threshold:
      current_sample = peak_threshold

    # detect sine peak
    if last_sample == peak_threshold and current_sample > peak_threshold:

      peak_last_start = peak_start
      peak_start = sample_number

      range_sample_count = sample_number - peak_last_start

      # calculate the space (0) and mark (1) sample counts
      mark_sample_count = sample_rate / frequency
      space_sample_count = mark_sample_count // 2

      space_count = round((range_sample_count - mark_sample_count) / space_sample_count)

      if space_count > 0:
        #print('found zero at '+str(sample_number) + ' for ' + str(range_sample_count) + ' samples')
        for i in range(space_count):
          bit_data.append((0, sample_number - range_sample_count + mark_sample_count + i * space_sample_count))

      bit_data.append((1, sample_number))
      peak_data.append((1, sample_number))

  print()
  return bit_data, lowpass_data, peak_data

def decode_peak(data, sample_rate, peak_threshold):

  # because the 2khz waves are too noisy, we just detect the 1khz sine peaks
  # and calculate the distance and therefore the zeros in between them

  bit_data = []
  peak_data = []

  cutoff = 1000
  # 4th order seems to be the max value that can be used to successfully
  # recover a signal from a clean cas1 recording, everything beyond that
  # distorts the amplitude of the signal too much, 
  # try a higher value with a cas1 recording and plot parameter to see what i mean
  order = 4
  lowpass_data = butter_lowpass_filter(data, cutoff, sample_rate, order)

  sample_count = len(data)

  last_sample = 0
  current_sample = 0
  next_sample = 0

  peak_auto_threshold = False
  if peak_threshold <= 0:
    peak_auto_threshold = True

  # iterate over all samples to detect the peaks
  for sample_number in range(sample_count - 1):

    # update progess every 10000 samples:
    if sample_number % 10000 == 0:
      percent_done = sample_number / sample_count * 100
      print('detecting peaks: ' + str(int(percent_done)) + '% done', end='\r')

    last_sample = current_sample
    current_sample = lowpass_data[sample_number]
    next_sample = lowpass_data[sample_number + 1]

    # detect peak
    if last_sample < current_sample and current_sample > next_sample:
      peak_data.append((current_sample, sample_number))

  print()

  frequency = 1000.0
  peak_count = len(peak_data)
  peak_threshold_data = []

  frequency_difference_data = []

  peak_start = 0
  peak_last_start = 0

  # detect bits from peak values
  for peak_number in range(peak_count):

    # update progess every 100 peaks:
    if peak_number % 100 == 0:
      percent_done = peak_number / peak_count * 100
      print('detecting bits: ' + str(int(percent_done)) + '% done', end='\r')

    peak_value = peak_data[peak_number][0]
    peak_position = peak_data[peak_number][1]

    if peak_auto_threshold:
      # adjust peak threshold automatically
      # the first 5 peaks, we just use the peak value as threshold
      # as this should be the 1 khz sine wave at the start of every block
      if peak_number <= 5 and peak_value > 0.01:
        peak_threshold = peak_value
      # after the first 5 peaks, we start to calculate the difference
      # between the current and previous peak, so that we dont adjust
      # the threshold to the smaller 2 khz peaks 
      if peak_number > 5:
        last_peak_threshold_value = peak_threshold_data[peak_number - 1][0]
        difference = last_peak_threshold_value - peak_value
        # lowering difference is 0.1 and raising diffrence is 0.1
        if (difference < 0.10 and difference > -0.10) and peak_value > 0.015:
          peak_threshold = peak_value

    peak_threshold_data.append((peak_threshold, peak_position))

    if peak_value >= peak_threshold:

      peak_last_start = peak_start
      peak_start = peak_position

      range_sample_count = peak_start - peak_last_start
      peak_last_position = peak_position

      # calculate the space (0) and mark (1) sample counts
      mark_sample_count = sample_rate / frequency
      space_sample_count = mark_sample_count // 2

      space_count = round((range_sample_count - mark_sample_count) / space_sample_count)

      if space_count > 0:
        #print('found 0 at '+str(peak_position) + ' for ' + str(range_sample_count) + ' samples')
        for i in range(space_count):
          bit_data.append((0, peak_position - range_sample_count + mark_sample_count + i * space_sample_count))
        frequency_difference_data.append((0, peak_position))
      else:
        frequency_difference_data.append((range_sample_count / (sample_rate / 1000) - 1, peak_position))

      #print('found 1 at '+str(peak_position))
      bit_data.append((1, peak_position))

  print()
  return bit_data, lowpass_data, peak_data, peak_threshold_data, frequency_difference_data

def decode_peak_try(data, sample_rate, peak_threshold):

  # this is another decode algorithm, that i played around with
  # it is not really usable at the moment

  bits = bitarray()

  bit_position_data = []
  peak_data = []

  cutoff = 1000
  order = 6
  lowpass_data = butter_lowpass_filter(data, cutoff, sample_rate, order)

  sample_count = len(data)

  peak_start = 0
  peak_last_start = 0
  last_sample = 0
  current_sample = 0

  sample_max_value = 0
  sample_max_values = []
  peak_threshold_data = []
  peak_threshold_data.append(peak_threshold)

  frequency = 1000.0

  # handle automatic peak detection
  for sample_number in range(sample_count):

    current_sample = lowpass_data[sample_number]
    sample_max_value = max(sample_max_value, current_sample)
    if sample_number > 0 and sample_number % 256 == 0:
      peak_threshold = sample_max_value# * 0.5# - 0.03# * sample_max_value
      peak_threshold_data.append(peak_threshold)
      sample_max_value = 0

  for i in range(len(peak_threshold_data) - 1):
    if abs(peak_threshold_data[i + 1] - peak_threshold_data[i]) > 0.15:
      peak_threshold_data[i + 1] = peak_threshold_data[i]

  final_peak_threshold_data = []
  for i in range(len(peak_threshold_data) * 2):
    final_peak_threshold_data.append(peak_threshold_data[i // 2])

  peak_threshold_data = final_peak_threshold_data

  peak_threshold_data = peak_threshold_data[1:]
  peak_threshold_data.append(peak_threshold)

  # iterate over all samples and fill the bitarray
  for sample_number in range(sample_count):

    peak_data.append(0)

    # update progess every 10000 samples:
    if sample_number % 10000 == 0:
      percent_done = sample_number / sample_count * 100
      print('decoding peak: ' + str(int(percent_done)) + '% done', end='\r')

    last_sample = current_sample
    current_sample = lowpass_data[sample_number]

    # get peak threshold value
    peak_threshold = peak_threshold_data[sample_number // 128]

    # we ignore everything thats below the peak value
    if current_sample < peak_threshold:
      current_sample = peak_threshold

    # detect sine peak
    if last_sample == peak_threshold and current_sample > peak_threshold:

      peak_last_start = peak_start
      peak_start = sample_number

      range_sample_count = sample_number - peak_last_start

      # calculate the space (0) and mark (1) sample counts
      mark_sample_count = sample_rate / frequency
      space_sample_count = mark_sample_count // 2

      space_count = round((range_sample_count - mark_sample_count) / space_sample_count)

      if space_count > 0:
        #print('found zero at '+str(sample_number) + ' for ' + str(range_sample_count) + ' samples')
        for i in range(space_count):
          bits.append(0)
          bit_position_data.append(sample_number - range_sample_count + mark_sample_count + i * space_sample_count)

      bits.append(1)
      bit_position_data.append(sample_number)
      peak_data[sample_number] = 1

  print()
  return bits, bit_position_data, lowpass_data, peak_data, peak_threshold_data

def decode_peak_fft_try(data, sample_rate, peak_threshold):

  # this is a decode algorithm with fft, that i played around with
  # it is not really usable at the moment

  bits = bitarray()

  bit_data = []
  bit_position_data = []
  peak_data = []
  freq_data = []

  cutoff = 1000
  order = 6
  lowpass_data = butter_lowpass_filter(data, cutoff, sample_rate, order)

  sample_count = len(data)

  peak_start = 0
  peak_last_start = 0
  last_sample = 0
  current_sample = 0

  fft_value_list = []
  fft_value_list_length = 133
  # we use this offset to exclude the start of the 1khz sine wave from our fft
  fft_value_list_offset = round(sample_rate / 1000 / 2)

  frequency = 1000.0
  frequency_fft = 1000.0

  # iterate over all samples and fill the bitarray
  for sample_number in range(sample_count):

    bit_data.append(1)
    peak_data.append(0)

    # update progess every 10000 samples:
    if sample_number % 10000 == 0:
      percent_done = sample_number / sample_count * 100
      print('decoding peak: ' + str(int(percent_done)) + '% done', end='\r')

    last_sample = current_sample
    current_sample = lowpass_data[sample_number]
    fft_sample = data[sample_number]

    # lets prepare some data for fft here
    fft_value_list.append(fft_sample)
    if len(fft_value_list) > fft_value_list_length + fft_value_list_offset:
      fft_value_list.pop(0)

    # we ignore everything thats below the peak value
    if current_sample < peak_threshold:
      current_sample = peak_threshold

    # detect sine peak
    if last_sample == peak_threshold and current_sample > peak_threshold:

      peak_last_start = peak_start
      peak_start = sample_number

      range_sample_count = sample_number - peak_last_start

      fft_filtered_value_list = fft_value_list[:-fft_value_list_offset]

      # we do multiple ffts with different bin sizes, so we can check for the more accurate results
      # if we would rely on one fft, we would not be exact enough and produce incorrect results

      # create a frequency -> absolute value dictionary
      fft_abs_result = {}

      # lets do 12 ffts
      for fft_offset in range(0,12):
        # prepare some variables
        fft_size = fft_value_list_length - fft_offset
        fft_bin_size = sample_rate / fft_size
        fft_target_bin = round(2000 / fft_bin_size)
        # do fft
        fft_result = fft(fft_filtered_value_list, fft_size)
        # calculate the resulting frequency
        freq = fft_target_bin * fft_bin_size
        # add it to our result dict together with the fft value
        fft_abs_result[freq] = numpy.abs(fft_result[fft_target_bin])

      # get biggest value, therefore most accurate frequency match, from fft results
      frequency_fft = 0.01
      fft_max_value = 0
      for key in fft_abs_result:
        if fft_abs_result[key] > fft_max_value:
          fft_max_value = fft_abs_result[key]
          frequency_fft = key

      #print('frequency: ' + str(frequency))

      # calculate the space (0) and mark (1) sample counts
      mark_sample_count = sample_rate / frequency
      space_sample_count = mark_sample_count // 2

      space_count = round((range_sample_count - mark_sample_count) / space_sample_count)

      if space_count > 0:
        #print('found zero at '+str(sample_number) + ' for ' + str(range_sample_count) + ' samples')
        for i in range(space_count):
          bits.append(0)
          bit_position_data.append(sample_number - range_sample_count + mark_sample_count + i * space_sample_count)
        #for i in range(sample_number - round(range_sample_count - mark_sample_count), sample_number):
        #  bit_data[i] = 0

      bits.append(1)
      bit_position_data.append(sample_number)
      peak_data[sample_number] = 1

    freq_data.append(frequency_fft / 1000)

  print()
  return bits, bit_position_data, lowpass_data, peak_data, freq_data
