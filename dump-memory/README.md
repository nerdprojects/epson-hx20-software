# Memory Dumper
Can be used to extract the memory content of the HX-20 over serial port:
- dump-memory.bas -> Slow BASIC script that outputs hexeditor like data to the serial port. You can use for example "pyserial-miniterm" with a baud rate of 4800 to receive the data.
- dump-memory.asm -> Fast assembly program to dump memory. You need to setup the start and end address in the assembly code or adjust it on the HX-20 with the MONITOR command. To recive the data, use the read-asm-dump.py script.
