*
* Example of Terminal Mode
* ( Code from Software Manual Chapter 5, page 7)
*
        OPT     H01
        ORG     $1000

DSPSCR  EQU     $FF4F
SCRFNC  EQU     $FF5E
RSONOF  EQU     $FF85
RSMST   EQU     $FF88
RSOPEN  EQU     $FF82
RSCLOS  EQU     $FF7F
RSGET   EQU     $FF79
RSPUT   EQU     $FF76
KEYIN   EQU     $FF9A
KEYSTS  EQU     $FF9D

        * construct screen package
START   LDD     #$8422
        STD     SCRPK1
        LDAA    #$87
        STAA    SCRPK2
        LDD     #$1303
        STD     SCRPK2+1
        LDD     #$1400
        STD     SCRPK2+3
        * initialize screen
        LDX     #SCRPK1
        JSR     SCRFNC
        LDX     #SCRPK2
        JSR     SCRFNC
        * set mode (stop:1 cd:no-check, rts:off, drs:no-check, cts:no-check, parity:none, 8 bits length, 4800 bps)
*        LDD     #$F568
        * set mode (stop:1 cd:no-check, rts:on, drs:check, cts:check, parity:none, 8 bits length, 4800 bps)
        LDD     #$CD68
        * set mode (stop:1 cd:no-check, rts:on, drs:no-check, cts:no-check,  parity:even, 7 bits length, 300 bps)
*        LDD     #$3D27
        JSR     RSMST
        * rs232c driver on
        LDAA    #1
        JSR     RSONOF
        * (x):buffer address (system buffer)
        LDX     $FFDC
        * (a,b): buffer size
        LDD     #260
        * receive open
        JSR     RSOPEN

        * accept from keyboard
REDKEY  JSR     KEYSTS
        * if break key is pressed, return (in basic mode)
        BCS     BRKRTN
        BEQ     RCVRS

        * accept characters from keyboard
        JSR     KEYIN
        * transmit accepted characters
        JSR     RSPUT
        * display accepted characters to virtual screen.
        JSR     DSPSCR
        * are there received characters in the buffer ?
RCVRS   LDX     $FFD8
        LDD     0,X
        BEQ     REDKEY
        JSR     RSGET
        CMPA    #$7F
        * ignore 7f - ff characters
        BCC     REDKEY
        * display received characters
        JSR     DSPSCR
        BRA     REDKEY

BRKRTN  RTS

* virtual screen packet
                * select screen device
SCRPK1  FCB     $84                    
        FCB     $22
                * set screen size and buffer address
SCRPK2  FCB     $87
        FCB     19,3
        FDB     $1400
        END
