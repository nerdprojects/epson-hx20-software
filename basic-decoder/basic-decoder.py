#!/usr/bin/env python3

import sys
import os

# copied from https://hxtape.sourceforge.net/, thanks for the reverse engineering!
basic_commands = {}
basic_commands[128] = "END"
basic_commands[129] = "FOR"
basic_commands[130] = "NEXT"
basic_commands[131] = "DATA"
basic_commands[132] = "DIM"
basic_commands[133] = "READ"
basic_commands[134] = "LET"
basic_commands[135] = "GO"
basic_commands[136] = "RUN"
basic_commands[137] = "IF"
basic_commands[138] = "RESTORE"
basic_commands[139] = "RETURN"
basic_commands[140] = "REM"
basic_commands[141] = "'"
basic_commands[142] = "STOP"
basic_commands[143] = "ELSE"
basic_commands[144] = "TRON"
basic_commands[145] = "TROFF"
basic_commands[146] = "SWAP"
basic_commands[147] = "DEFSTR"
basic_commands[148] = "DEFINT"
basic_commands[149] = "DEFSNG"
basic_commands[150] = "DEFDBL"
basic_commands[151] = "DEFFIL"
basic_commands[152] = "ON"
basic_commands[153] = "LPRINT"
basic_commands[154] = "LLIST"
basic_commands[155] = "RENUM"
basic_commands[156] = "ERROR"
basic_commands[157] = "RESUME"
basic_commands[158] = "AUTO"
basic_commands[159] = "DELETE"
basic_commands[160] = "DEF"
basic_commands[161] = "POKE"
basic_commands[162] = "PRINT"
basic_commands[163] = "CONT"
basic_commands[164] = "LIST"
basic_commands[165] = "CLEAR"
basic_commands[166] = "OPTION"
basic_commands[167] = "RANDOMIZE"
basic_commands[168] = "WHILE"
basic_commands[169] = "WEND"
basic_commands[170] = "NEW"
basic_commands[171] = "ERASE"
basic_commands[172] = "LOADM"
basic_commands[173] = "LOAD?"
basic_commands[174] = "SAVEM"
basic_commands[175] = "SAVE"
basic_commands[176] = "LOAD"
basic_commands[177] = "MERGE"
basic_commands[178] = "OPEN"
basic_commands[179] = "CLOSE"
basic_commands[180] = "LINE"
basic_commands[181] = "SCROLL"
basic_commands[182] = "SOUND"
basic_commands[183] = "MON"
basic_commands[184] = "FILES"
basic_commands[185] = "MOTOR"
basic_commands[186] = "PUT"
basic_commands[187] = "GET"
basic_commands[188] = "LOCATES"
basic_commands[189] = "LOCATE"
basic_commands[190] = "CLS"
basic_commands[191] = "KEY"
basic_commands[192] = "WIDTH"
basic_commands[193] = "PSET"
basic_commands[194] = "PRESET"
basic_commands[195] = "COPY"
basic_commands[196] = "EXEC"
basic_commands[197] = "WIND"
basic_commands[198] = "GCLS"
basic_commands[199] = "SCREEN"
basic_commands[200] = "COLOR"
basic_commands[201] = "LOGIN"
basic_commands[202] = "TITLE"
basic_commands[203] = "STAT"
basic_commands[204] = "PCOPY"
basic_commands[205] = "MEMSET"
basic_commands[206] = "BASE"
basic_commands[207] = "TAB("
basic_commands[208] = "TO"
basic_commands[209] = "SUB"
basic_commands[210] = "FN"
basic_commands[211] = "SPC("
basic_commands[212] = "USING"
basic_commands[213] = "USR"
basic_commands[214] = "ERL"
basic_commands[215] = "ERR"
basic_commands[216] = "OFF"
basic_commands[217] = "ALL"
basic_commands[218] = "THEN"
basic_commands[219] = "NOT"
basic_commands[220] = "STEP"
basic_commands[221] = "+"
basic_commands[222] = "-"
basic_commands[223] = "*"
basic_commands[224] = "/"
basic_commands[225] = "^"
basic_commands[226] = "AND"
basic_commands[227] = "OR"
basic_commands[228] = "XOR"
basic_commands[229] = "EQV"
basic_commands[230] = "IMP"
basic_commands[231] = "MOD"
basic_commands[232] = "\\"
basic_commands[233] = ">"
basic_commands[234] = "="
basic_commands[235] = "<"

basic_functions = {}
basic_functions[128] = "SGN"
basic_functions[129] = "INT"
basic_functions[130] = "ABS"
basic_functions[131] = "FRE"
basic_functions[132] = "POS"
basic_functions[133] = "SQR"
basic_functions[134] = "LOG"
basic_functions[135] = "EXP"
basic_functions[136] = "COS"
basic_functions[137] = "SIN"
basic_functions[138] = "TAN"
basic_functions[139] = "ATN"
basic_functions[140] = "PEEK"
basic_functions[141] = "LEN"
basic_functions[142] = "STR$"
basic_functions[143] = "VAL"
basic_functions[144] = "ASC"
basic_functions[145] = "CHR$"
basic_functions[146] = "EOF"
basic_functions[147] = "LOF"
basic_functions[148] = "CINT"
basic_functions[149] = "CSNG"
basic_functions[150] = "CDBL"
basic_functions[151] = "FIX"
basic_functions[152] = "SPACE$"
basic_functions[153] = "HEX$"
basic_functions[154] = "OCT$"
basic_functions[155] = "LEFT$"
basic_functions[156] = "RIGHT$"
basic_functions[157] = "MID$"
basic_functions[158] = "INSTR"
basic_functions[159] = "VARPTR"
basic_functions[160] = "STRING$"
basic_functions[161] = "RND"
basic_functions[162] = "TIME"
basic_functions[163] = "DATE"
basic_functions[164] = "DAY"
basic_functions[165] = "INKEY$"
basic_functions[166] = "INPUT"
basic_functions[167] = "CSRLIN"
basic_functions[168] = "POINT"
basic_functions[169] = "TAPCNT"
basic_functions[214] = "ERL"
basic_functions[215] = "ERR"

def print_char(char):
  global over_file_size
  if char < 0x20:
    print_info('non-printable character ' + hex(char))
  if not over_file_size:
    sys.stdout.buffer.write(input_byte.to_bytes(1,'big'))
    sys.stdout.flush()
  else:
    sys.stderr.buffer.write(input_byte.to_bytes(1,'big'))
    sys.stderr.flush()

def print_string(string):
  global over_file_size
  if not over_file_size:
    sys.stdout.buffer.write(bytes(string, 'ascii'))
    sys.stdout.flush()
  else:
    sys.stderr.buffer.write(bytes(string, 'ascii'))
    sys.stderr.flush()

def print_info(string):
  sys.stderr.buffer.write(bytes('\n---> ' + string + '\n', 'ascii'))
  sys.stderr.flush()

def read_file_bytes(file, count):
  input_bytes = file.read(count)
  if len(input_bytes) != count:
    print_info('reached end of file')
    sys.exit(0)
  return input_bytes
  
# on the hx-20 character code table, we only have assignments to 0x9f
# from 0xa0 to 0xff no assignments are present.
# statements are separated by 0x00

# 0. byte ff
# 1. and 2. form a two byte size value

# next 2 bytes are unknown (sometimes its 3 bytes. not sure how this works)
# next 2 bytes form a line number
# if next byte is not 0xff or 0x00 its a basic command
# if its 0xff, the byte after it is a basic function, if no mapping exists the byte is read as is (e.g. characters)
# if its 0x00 then the sequence is done and start over

if len(sys.argv) < 1:
  print('Usage: basic-decoder.py <input-file>')
input_file_path = sys.argv[1]
if not os.path.isfile(input_file_path):
  print_info('input file not found')
  sys.exit(1)

input_file_size = os.path.getsize(input_file_path)
input_file = open(input_file_path, 'rb')
header_byte = read_file_bytes(input_file, 1)[0]
if header_byte != 0xff:
  print_info('header 0xff not found')
  sys.exit(1)

print_info('start decoding')
size = int.from_bytes(read_file_bytes(input_file, 2), byteorder='big', signed=False)
over_file_size = False
print_info('size is: '+str(size))

while True:
  # TODO: reverse this two or three bytes that are unknown and implement it correctly
  # currently this is just a wild guess here
  # i think it might be the size of the current command or so
  # or where the next command is located
  some_bytes_we_dont_know_yet_for_what_they_are_used = read_file_bytes(input_file, 2)
  #print_info(some_bytes_we_dont_know_yet_for_what_they_are_used.hex() + ' ' + hex(input_file.tell()))
  if some_bytes_we_dont_know_yet_for_what_they_are_used[1] == 0x1b:
    some_bytes_we_dont_know_yet_for_what_they_are_used = read_file_bytes(input_file, 1)
    #print_info(some_bytes_we_dont_know_yet_for_what_they_are_used.hex() + ' ' + hex(input_file.tell()))
  linenumber_bytes = read_file_bytes(input_file, 2)
  # it seems, that if there is a linenumber with 0x1b as the first byte, an additonal 0x1b is present after it
  # kind of confusing, but for now i just read this byte and ignore it
  if linenumber_bytes[1] == 0x1b:
    #print_info('skipping over additional 0x1b in line number')
    read_file_bytes(input_file, 1)
  linenumber = int.from_bytes(linenumber_bytes, byteorder='big', signed=False)

  print_string(str(linenumber) + ' ')
  in_quotes = False
  input_bytes = read_file_bytes(input_file, 1)
  input_byte = input_bytes[0]
  while input_byte != 0x00:

    if input_byte == 0x22:
      in_quotes = not in_quotes

    if in_quotes:
      print_char(input_byte)
    elif input_byte == 0xff:
      input_bytes = read_file_bytes(input_file, 1)
      function_byte = input_bytes[0]
      if basic_functions.get(function_byte) != None:
        print_string(basic_functions[function_byte])
      else:
        print_char(function_byte)
    elif basic_commands.get(input_byte) != None:
        print_string(basic_commands[input_byte])
    else:
        print_char(input_byte)
    input_bytes = read_file_bytes(input_file, 1)
    input_byte = input_bytes[0]

  print_string('\n')
  if(input_file.tell() > size):
    # we also print commands that are present after the declared file size
    # they are not part of the program, but might still hold some information of interest
    over_file_size = True
    print_info('command decoded after file size:')
