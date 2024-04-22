*
* Write Stuff to LCD
*
        OPT     H01
        ORG     $1000

KEYIN   EQU     $FF9A

LCDCLR  EQU     $F4ED
DISCHL  EQU     $F426
DISPIT  EQU     $FF5B

* LCDMOD (aka WITDAT) is used to send the data to the LCD controller via 0x2A, it dis- and renables the interrupts
* it accepts parameters over the A register
LCDMOD  EQU     $F4A5
* DATAMOD is used to block execution until the LCD driver is ready again at 0x28 and the passes execution to WRTP26
DATAMOD EQU     $F4BC
* WRTP26 is used to select the LCD controller and the command or data mode via 0x26, it dis- and renables the interrupts
* it uses A and B for parameters
WRTP26  EQU     $FED4

* clear screen and init memory values
        JSR     LCDCLR
        LDAA    #0
        STAA    CNTLPR
        LDAA    #1
        STAA    CHIP
        LDAA    #0
        STAA    OFROW

* write a row of a LCD controller
* X is used as a pointer to the image data, it is not destroyed trough the issued routine calls to the bios
        LDX     #IMGSTA
        * not sure what A is used here, must be 0x0F
WRROW   LDAA    #$0F
        * select command mode and chip (mode is the 4th bit, 1-3 is the chip select, selectable chips start at 1 and end at 6)
        LDAB    #$08
        ORAB    CHIP
        JSR     WRTP26

        * send the "write" command
        LDAA    #$64
        JSR     LCDMOD

        * send command data to select the start offset 
        * 8th bit is ? (is always set here), 1-7th bits are the start offset
        * bank0 = 0 - 40 (0x28), bank1 = 64 (0x40) - 104 (0x68)
        LDAA    #$80
        ORAA    OFROW
        JSR     LCDMOD

        * not sure what A is used here, must be 0x08
        LDAA    #$08
        * select data mode (mode is the 4th bit, 1-3 is the chip select)
        LDAB    #$00
        JSR     DATAMOD

        * load pixel data pointed by X into A, and increase X and send it to the LCD controller
WRCOL   LDAA    0,X
        JSR     LCDMOD
        INX
        * do looping for the 40 columns of a controller
        INC     CNTLPR
        LDAA    CNTLPR
        CMPA    #40
        BNE     WRCOL

        * select no chip and switch to command mode
        LDD     #$0F08
        * change the mode via DATAMOD and WRTP26
        JSR     DATAMOD

* we are done with writing a row
        * we reset the row counter
DONEROW LDAA    #0
        STAA    CNTLPR

        * check if we wrote the second row and jump to the according offset if we have
        LDAA    OFROW
        CMPA    #64
        BEQ     DONECHP

        * if we only wrote the first row, we increase the offset to bank1
        LDAA    #64
        STAA    OFROW
        * and write the second row
        BRA     WRROW

* we are done with writing second row, thus done with the chip
        * reset the offset to bank0
DONECHP LDAA    #0
        STAA    OFROW
        * increase the chip
        LDAA    CHIP
        INCA
        STAA    CHIP
        * write next row/chip if we not over chip 6
        CMPA    #7
        BNE     WRROW
        * reset chip if were over
        LDAA    #1
        STAA    CHIP

* check if we reached the end of the image sequence
        #JSR     KEYIN

        * store X on stack, reset it to 0 and increment until 4096 to create a short delay
        PSHX
        LDX     #0
DELAYL  INX
        CPX     #4096
        BNE     DELAYL
        PULX

        CPX     #IMGEND
        * if not continue
        BNE     WRROW
        * if we are at the end, reset the pointer
        LDX     #IMGSTA
        BRA     WRROW

* work area
CNTLPR  FCB     0
CHIP    FCB     0
OFROW   FCB     0

IMGSTA
* insert here your own images as FCB definitions
IMGEND
        END
