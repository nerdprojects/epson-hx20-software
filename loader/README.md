# Program Loaders
Some utilities I use to load basic or assembly programs to the HX-20:

## setup.bas / loader.asm
The two stage loader scripts I use the most:
- setup.bas -> BASIC program that is considered the first stage loader. It sets up the second stage loader, menu entries and function button assignments
- loader.asm -> Assembly code of the second stage loader, a compiled version is contained in setup.bas

### Usage
1. Enter BASIC on the HX-20 and issue following LOAD command:
  LOAD"COM0:(68N13)"
2. Write the setup.bas to the HX-20
  ./write-bas.py /dev/ttyUSB0 setup.bas
3. On the HX-20 run the the BASIC program
  RUN
4. After that you can hit the BREAK button on the HX-20 and you should have two new menu entries
  3 LOADER
  4 PROGRAM
5. Hit 3 to start the binary loader
6. Send your compiled, binary program to the HX-20
   ./write-asm.py /dev/ttyUSB some-binary-program.b
7. Hit BREAK when done with sending
8. Now you can run the program with the menu entry "4. PROGRAM" or the MONITOR command "G1000"

### Notes
If you have a big assembly program, you have to increase the start address of BASIC with the MEMSET command.
Else the BASIC memory section will collide with your program. (See the BASIC manual on page 3-37 and 5-10.)

## convert-asm-basic-loader.py
An alternative but slower way to load assembly programs. It's a script that converts a binary file to BASIC instructions. These instructions load the binary file at offset 0x1000 when RUN on the HX-20. The instuctions are sent over the serial port to the HX-20.

### Usage
1. Enter BASIC on the HX-20 and issue following LOAD command:
  LOAD"COM0:(68N13)"
2. Run the script:
  ./convert-asm-basic-loader.py /dev/ttyUSB0 some-binary-program.b
3. On the HX-20 run the the BASIC program
  RUN
4. You can now use following BASIC command to run the program (or use the MONTIOR command G1000)
  EXEC&H1000

## write-asm.py / write-bas.py
Scripts used to send binary or BASIC files to the HX-20 over the serial port.
Used in conjuction with the other scripts in this folder.
