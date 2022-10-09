*
* Hello World
*
        OPT     H01
        ORG     $1000

DSPSCR  EQU     $FF4F
SCRFNC  EQU     $FF5E
KEYIN   EQU     $FF9A
KEYSTS  EQU     $FF9D

* prepare init screen
        LDD     #$8422
        STD     SCRPK1
        LDAA    #$87
        STAA    SCRPK2
        LDD     #$1303
        STD     SCRPK2+1
        LDD     #$1400
        STD     SCRPK2+3

* init screen
        LDX     #SCRPK1
        JSR     SCRFNC
        LDX     #SCRPK2
        JSR     SCRFNC

* print string
        LDX     #OUTSTRT
REPEAT  LDAA    0,X
                * we need to backup the X register, because the subroutine mixes it up
        STX     INDEX
        JSR     DSPSCR
        LDX     INDEX
        INX
        CPX     #OUTEND
        BNE     REPEAT

* exit on key input
        JSR     KEYIN
        RTS

* output string and index register backup
OUTSTRT FCC     'HELLO YOU IDIOT!'
        FCB     $0a,$0d,$0a,$0d
        FCC     'hit any key'
        FCB     $0a,$0d
        FCC     'to exit...'
OUTEND
INDEX   FDB     0

* virtual screen packet
                * 0x84 = select screen device
SCRPK1  FCB     $84                    
                * 0x22 = LCD (0x30 would be external display)
        FCB     $22
                * 0x87 = set screen size and buffer address
SCRPK2  FCB     $87
                * screen width and height (20x4 chars)
        FCB     19,3
                * screen buffer location
        FDB     $1400

        END
