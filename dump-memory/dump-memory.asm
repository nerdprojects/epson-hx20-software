*
* dump ROM
*
        OPT     H01
        ORG     $1000

RSONOF  EQU     $FF85
RSMST   EQU     $FF88
RSPUT   EQU     $FF76

* set serial mode (0xCD = no parity, cts, dsr, rts, cd, 1 stop bit)
*                 (0x68 = 4800 baud, 8 bit word length)
        LDD     #$CD68
        JSR     RSMST
        LDAA    #1
        JSR     RSONOF

* store start memory address 0x6000 in X
        LDX     #$6000
* load memory content pointed by X into A
REPEAT  LDAA    0,X
        JSR     RSPUT
* increase and check if end memory address 0x8000 is reached
        INX
        CPX     #$8000
        BNE     REPEAT
* trigger trap when finished
TRAP    FCB     $00

        END
