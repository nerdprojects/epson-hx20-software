*
* Write Stuff to LCD
*
        OPT     H01
        ORG     $1000

DSPSCR  EQU     $FF4F
SCRFNC  EQU     $FF5E
KEYIN   EQU     $FF9A
KEYSTS  EQU     $FF9D

LCDCLR  EQU     $F4ED
DISPIT  EQU     $F3FB

* prepare init screen
        LDD     #$1303
        STD     SCRPK2+1

* init screen
        LDX     #SCRPK1
        JSR     SCRFNC
        LDX     #SCRPK2
        JSR     SCRFNC

* fill screen with char
        * init counters with 0
SCRFIL  LDAA    #$0
        STAA    COUNTX
        STAA    COUNTY
        * load counter into X
LOOP    LDX     COUNT
        * load ascii char into A
        LDAA    CHAR
        * display char in A on column and line defined by X
        JSR     DISPIT
        * increase the X counter
        INC     COUNTX
        * check if we already reached the last column
        LDAA    #$14
        CMPA    COUNTX
        BNE     LOOP

        * we reached last column, now we increase the line
        INC     COUNTY
        * and set counter of X to 0 again
        LDAA    #$0
        STAA    COUNTX
        * check if we reached the last line
        LDAA    #$4
        CMPA    COUNTY
        BNE     LOOP

        * now we are done with filling the screen, so we xor the char to toggle it with another graph char
        * and then we start over
        LDAA    CHAR
        EORA    #$1F
        STAA    CHAR
        JMP     SCRFIL

* exit on key input
        JSR     KEYIN
        RTS

* work area
COUNT
COUNTX  FCB     0
COUNTY  FCB     0
CHAR    FCB     $8F

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
