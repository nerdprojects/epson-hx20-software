# Epson HX-20 Software

A collection of little programs I wrote for the HX-20.

## Programs
- dump-memory -> BASIC and assembly version of a memory dump tool, that just sends out the memory content to the serial port
- terminal -> Terminal emulator software (based on the corresponding listing in the software manual)
- loader -> Consisting of a BASIC script that sets up a binary loader, that can be used to load assembly programs from the serial port
- tape-recover -> Scripts that can recover programs and data from HX-20 tape recordings.
- basic-decoder -> A python script that converts the binary Epson Basic format to a human-readable format. 
- hello-word -> Hello world for Epson HX-20 in assembly
- viewer -> An assembly program to display images or fluid animations on the HX-20.

## Instructions
### Load Programs
There are multiple options to load programs to the Epson HX-20. I know of following:
- Send over serial port
- Send as FSK audio (casette port)
- Use a floppy emulator: https://norbertkehrer.github.io/flashx20.html or https://www.mh-aerotools.de/hp/hx-20/

I use the plain serial connection as it seems to be the simplest solution for me.
I first load a small BASIC program that installs a binary loader and then I use this binary loader to further load my assembly programs.
See the "loader" folder for detailed instructions.


### Assemble
To assemble the .asm files I use A09: https://github.com/Arakula/A09

    ./a09 yourbinary.asm

You need to define the correct assembler options in the asm file:
- "OPT H01" -> 6301 processor language
- "ORG $1000" -> offset where binary is loaded

### Disassemble
I use f9dasm for this: https://github.com/Arakula/f9dasm

    ./f9dasm -offset 1000 -6301 yourbinary.bin

## Information
### Manuals
Check out the great HX-20 manuals. They contain very detailed descriptions of the system (software and hardware) and even assembly listings of the operating system ROM. They can be found here for example: https://electrickery.nl/comp/hx20/doc

### Memory Map
     ___________
    |           |
    | 0000-004D | Protected BIOS RAM
    |___________|
    |           |
    | 004F-0A3F | RAM (Used by BIOS and BASIC I think)
    |___________|
    |           |
    | 0A40-3FFF | RAM
    |___________|
    |           |
    | 4000-5FFF | RAM (With the expansion card I have installed, otherwise it's empty)
    |___________|
    |           |
    | 6000-7FFF | RAM (With the expansion card I have installed, otherwise it's the optional ROM)
    |___________|
    |           |
    | 8000-9FFF | BASIC ROM 3
    |___________|
    |           |
    | A000-BFFF | BASIC ROM 2
    |___________|
    |           |
    | C000-DFFF | BIOS ROM 1
    |___________|
    |           |
    | E000-FFFF | BIOS ROM 0
    |___________|

### Bank Switching
If you have an expansion card installed, it's possible to do bank switching. (Described in the Hardware Manual on page 4-30).

To switch the internal BASIC roms to the expansion board roms (ROM4: 0x8000 - 0x9fff and ROM3: 0xa000 - 0xbfff) read or write to address 0x30. This triggers the ROM E signal on the expansion port and make the expansion ROMs available. To reset the bank to the internal HX20 Roms, read or write address 32.

- Open MONITOR
- Store 80 at 7E to enable writes to low memory addresses 0x00 - 0x4D
- Call STORE on address 30 to pull up the ROM E signal (you can cancel the store operation)
- Verify the bank switch by dumping 0x8000
- Call STORE on address 32 to pull down the ROM E signal and switch to the original bank

### Exec Headers
Described in the Software Manual on page 16-1.

The headers have to be at the start addresses of the ROM.
(0xc000, 0xa000, 0x8000, 0x6000, 0x4000). Other headers may follow but have to be linked by the first one.
The init function (ctrl+shift+§ / cold start) populates a table with the reference to the found exec headers.
This table can also be modified manually:
- First the value 0x3a, 0x41, 0x15, 0x00 is written to 0x13c, where 0x15, 0x00 is the address of the exec header, which can be freely chosen.
- Then at 0x1500 the exec header is written in the same format as the ROM headers:

         | 0x41 (A) = Application, 0x42 (B) = BASIC Interpreter
         |
         |    | adress of next header, 0xffff if last header
         |    | 
         |    |  __| start address   __| end byte
         |  __| |  |                 | |
        || |  | |  | M O  N I  T O  R| |
      ba41 ffff d77e 4d4f 4e49 544f 5200
                                        
                     B A  S  I  C
      ba42 ffff 800c 4241 5349 4300

### Reprogram Function Keys
Apart from using the BASIC commands "KEY" and "KEY LIST", it's also possible to modify the function keys with the MONITOR:
Enter MONITOR and write your desired BASIC command as ASCII to the memory location 0x502 for PF1, 0x512 for PF2, 0x522 for PF3 and so on.
End the command with 0x00 or with 0x0d to automatically execute it on keypress. Interestingly, commands can be longer than 0x10 bytes and still work fine.
However, defining such long commands is only possible by using the MONITOR.
