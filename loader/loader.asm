*
* ASM based Serial Program Loader
*
        OPT     H01
        ORG     $A40

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

* setup screen
        LDD     #$1303
        STD     SCRPK2+1
        LDX     #SCRPK1
        JSR     SCRFNC
        LDX     #SCRPK2
        JSR     SCRFNC

* print info
        LDX     #INFO
PRINT   LDAA    0,X
        PSHX
        JSR     DSPSCR
        PULX
        INX
        CPX     #INFOEND
        BNE     PRINT

* set serial mode (0xCD = no parity, cts, dsr, rts, cd, 1 stop bit)
*                 (0x68 = 4800 baud, 8 bit word length)
        LDD     #$CD68
        JSR     RSMST
        LDAA    #1
        JSR     RSONOF
        * serial buffer address and size (0xFFDC points to the systems I/O buffer)
        LDX     $FFDC
        LDD     #260
        JSR     RSOPEN

* read data from seral into target buffer
        LDX     #$1000
        PSHX
READ    JSR     KEYSTS
        * exit whne break key is hit
        BCS     BRKRTN

* 0xFFD8 holds the amount of received characters
        LDX     $FFD8
        LDD     0,X
        BEQ     READ
        * load the received char into A
        JSR     RSGET
        * store A into target buffer
        PULX
        STAA    0,X
        INX
        PSHX
        BRA     READ

BRKRTN  RTS

* strings
INFO    FCC    'Binary loader ready'
        FCB    $0d,$0a
        FCB    $0d,$0a
        FCC    'Hit BREAK when done'
        FCB    $0d,$0a
        FCC    'with sending'
INFOEND

* virtual screen packet
                * select screen device
SCRPK1  FCB     $84                    
        FCB     $22
                * set screen size and buffer address
SCRPK2  FCB     $87
        FCB     19,3
        FDB     $1400
        END
